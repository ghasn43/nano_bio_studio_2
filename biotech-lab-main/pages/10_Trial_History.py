"""
Trial History Page - View all completed and active trials
"""
import streamlit as st
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.trial_registry import (
    get_all_trials,
    get_recent_trials,
    get_trial_by_id,
    update_trial_parameters,
    export_trial_to_json,
    get_missing_parameters
)
from modules.professional_report_generator import generate_professional_pdf_report
from components.ui_components import render_trial_header
from components.workflow_guide import render_workflow_progress, render_step_header, render_navigation_buttons


def generate_trial_pdf_report(trial: dict) -> BytesIO:
    """
    Generate a professional PDF report using the AI-powered report generator
    """
    try:
        result = generate_professional_pdf_report(trial)
        if result is not None:
            return result
        else:
            st.error("❌ PDF generator returned None - reportlab may not be installed")
            return None
    except Exception as e:
        st.error(f"❌ Error generating PDF: {str(e)}")
        import traceback
        st.code(traceback.format_exc(), language="python")
        return None


st.set_page_config(page_title="Trial History", layout="wide")

st.markdown("""
<style>
.trial-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.status-active {
    color: #4ade80;
    font-weight: bold;
}
.status-completed {
    color: #60a5fa;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Show workflow progress
render_workflow_progress()

st.divider()

# Display trial header if active
render_trial_header()

st.divider()

render_step_header(5)

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["All Trials", "Recent Trials", "Trial Details"])

with tab1:
    st.markdown("## All Trials")
    trials = get_all_trials()
    
    if trials:
        # Create dataframe for display
        trial_data = []
        for trial in trials:
            trial_data.append({
                "Trial ID": trial['trial_id'],
                "Disease": trial['disease_name'],
                "Drug": trial['drug_name'],
                "NP Size (nm)": trial['np_size_nm'],
                "Status": trial['status'],
                "Created": trial['creation_timestamp'][:16],
            })
        
        st.dataframe(trial_data, use_container_width=True, hide_index=True)
        
        st.info(f"Total trials: {len(trials)}")
        
        # Batch PDF generation option
        st.markdown("---")
        st.markdown("### Generate PDFs for Selected Trials")
        
        trial_ids = [t['trial_id'] for t in trials]
        selected_for_pdf = st.multiselect(
            "Select trials to generate PDFs:",
            trial_ids,
            key="batch_pdf_select"
        )
        
        if selected_for_pdf:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Generate PDFs", key="batch_generate_pdf"):
                    pdf_files = {}
                    failed_trials = []
                    progress_bar = st.progress(0)
                    
                    for idx, trial_id in enumerate(selected_for_pdf):
                        trial = get_trial_by_id(trial_id)
                        if trial:
                            with st.spinner(f"Generating PDF for {trial_id}..."):
                                try:
                                    pdf_buffer = generate_trial_pdf_report(trial)
                                    if pdf_buffer and pdf_buffer.getbuffer().nbytes > 0:
                                        pdf_files[trial_id] = pdf_buffer
                                    else:
                                        failed_trials.append(trial_id)
                                except Exception as e:
                                    st.error(f"Error generating PDF for {trial_id}: {str(e)}")
                                    failed_trials.append(trial_id)
                        
                        progress_bar.progress((idx + 1) / len(selected_for_pdf))
                    
                    if pdf_files:
                        st.session_state['batch_pdf_files'] = pdf_files
                        st.success(f"✅ Generated {len(pdf_files)} PDF(s) successfully!")
                    
                    if failed_trials:
                        st.warning(f"⚠️ Failed to generate PDF for: {', '.join(failed_trials)}")
            
            with col2:
                if 'batch_pdf_files' in st.session_state and st.session_state['batch_pdf_files']:
                    st.info(f"{len(st.session_state['batch_pdf_files'])} PDF(s) ready for download")
                    
                    for trial_id, pdf_buffer in st.session_state['batch_pdf_files'].items():
                        safe_trial_id = trial_id.replace('/', '_')
                        pdf_filename = f"trial_{safe_trial_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        # Ensure buffer is at position 0 for download
                        pdf_buffer.seek(0)
                        st.download_button(
                            label=f"⬇️ {trial_id[:20]}...",
                            data=pdf_buffer,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key=f"batch_download_{trial_id}"
                        )
    else:
        st.warning("No trials found. Start a new trial on the Disease Selection page.")

with tab2:
    st.markdown("## Recent Trials (Last 10)")
    recent = get_recent_trials(limit=10)
    
    if recent:
        for trial in recent:
            with st.expander(f"{trial['trial_id']} - {trial['disease_name']} ({trial['status']})"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("### Basic Info")
                    st.write(f"**Disease:** {trial['disease_name']}")
                    st.write(f"**Drug:** {trial['drug_name']}")
                    st.write(f"**Status:** {trial['status']}")
                
                with col2:
                    st.markdown("### NP Parameters")
                    st.write(f"**Size:** {trial['np_size_nm']} nm")
                    st.write(f"**Charge:** {trial['np_charge_mv']} mV")
                    st.write(f"**PEG:** {trial['np_peg_percent']}%")
                
                with col3:
                    st.markdown("### Metadata")
                    st.write(f"**Created:** {trial['creation_timestamp'][:10]}")
                    st.write(f"**PDI:** {trial.get('np_pdi', 'N/A')}")
                    st.write(f"**Zeta:** {trial.get('np_zeta_potential', 'N/A')}")
                
                with col4:
                    st.markdown("### Actions")
                    if st.button(f"📂 Load Trial", key=f"load_{trial['trial_id']}"):
                        st.session_state.trial_id = trial['trial_id']
                        st.session_state.trial_disease_name = trial['disease_name']
                        st.success("Trial loaded to session!")
                        st.rerun()
                    
                    if st.button(f"📄 Export JSON", key=f"export_{trial['trial_id']}"):
                        export_path = export_trial_to_json(trial['trial_id'])
                        if export_path:
                            st.success(f"Exported to: {export_path}")
                
                # Parameter Validation Section
                missing_params = get_missing_parameters(trial['trial_id'])
                if missing_params:
                    st.warning(f"⚠️ Missing parameters ({len(missing_params)}): {', '.join(missing_params[:3])}" + 
                              ("..." if len(missing_params) > 3 else ""))
                    
                    with st.expander(f"📝 Complete Trial Parameters ({len(missing_params)} missing)"):
                        st.markdown("**Update missing parameters for report generation:**")
                        
                        param_col1, param_col2 = st.columns(2)
                        
                        with param_col1:
                            st.subheader("Nanoparticle Parameters")
                            
                            zeta = st.number_input(
                                "Zeta Potential (mV)",
                                value=float(trial.get('np_zeta_potential') or 0.0),
                                step=0.1,
                                key=f"zeta_{trial['trial_id']}"
                            )
                            
                            pdi = st.number_input(
                                "PDI (Polydispersity Index)",
                                value=float(trial.get('np_pdi') or 0.0),
                                min_value=0.0,
                                max_value=1.0,
                                step=0.01,
                                key=f"pdi_{trial['trial_id']}"
                            )
                        
                        with param_col2:
                            st.subheader("Treatment Parameters")
                            
                            dose = st.number_input(
                                "Dose (mg/kg)",
                                value=float(trial.get('treatment_dose_mgkg') or 0.0),
                                step=0.1,
                                key=f"dose_{trial['trial_id']}"
                            )
                            
                            route = st.text_input(
                                "Administration Route",
                                value=trial.get('treatment_route', ''),
                                key=f"route_{trial['trial_id']}"
                            )
                            
                            frequency = st.text_input(
                                "Dosing Frequency (e.g., Daily, Twice weekly)",
                                value=trial.get('treatment_frequency', ''),
                                key=f"freq_{trial['trial_id']}"
                            )
                            
                            duration = st.number_input(
                                "Treatment Duration (days)",
                                value=int(trial.get('treatment_duration_days') or 0),
                                step=1,
                                key=f"duration_{trial['trial_id']}"
                            )
                        
                        if st.button(f"💾 Save Parameters", key=f"save_params_{trial['trial_id']}"):
                            success = update_trial_parameters(
                                trial['trial_id'],
                                np_zeta_potential=zeta if zeta > 0 else None,
                                np_pdi=pdi if pdi > 0 else None,
                                treatment_dose_mgkg=dose if dose > 0 else None,
                                treatment_route=route if route else None,
                                treatment_frequency=frequency if frequency else None,
                                treatment_duration_days=duration if duration > 0 else None
                            )
                            if success:
                                st.success("✅ Parameters saved successfully! Refresh to see updates.")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save parameters")
                else:
                    st.success("✅ All parameters complete")
                
                # PDF Generation Section
                st.divider()
                pdf_col1, pdf_col2 = st.columns([1, 1])
                
                with pdf_col1:
                    if st.button(f"🔄 Generate PDF", key=f"gen_pdf_{trial['trial_id']}"):
                        with st.spinner("Generating PDF report..."):
                            try:
                                pdf_buffer = generate_trial_pdf_report(trial)
                                if pdf_buffer and pdf_buffer.getbuffer().nbytes > 0:
                                    st.success("✅ PDF generated successfully!")
                                    st.session_state[f"pdf_buffer_{trial['trial_id']}"] = pdf_buffer
                                elif pdf_buffer is None:
                                    st.error("❌ PDF generation failed - buffer is None")
                                else:
                                    st.error("❌ PDF buffer is empty")
                            except Exception as e:
                                st.error(f"❌ Error in PDF generation: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                
                with pdf_col2:
                    if f"pdf_buffer_{trial['trial_id']}" in st.session_state:
                        pdf_buffer = st.session_state[f"pdf_buffer_{trial['trial_id']}"]
                        # Ensure buffer is at position 0 for download
                        pdf_buffer.seek(0)
                        safe_trial_id = trial['trial_id'].replace('/', '_')
                        pdf_filename = f"trial_{safe_trial_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_buffer,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key=f"download_pdf_{trial['trial_id']}"
                        )
    else:
        st.info("No recent trials found.")

with tab3:
    st.markdown("## Trial Details & Comparison")
    
    trials = get_all_trials()
    if trials:
        # Select trials to compare
        trial_ids = [t['trial_id'] for t in trials]
        selected_trials = st.multiselect(
            "Select trials to compare:",
            trial_ids,
            max_selections=3
        )
        
        if selected_trials:
            comparison_data = []
            
            for trial_id in selected_trials:
                trial = get_trial_by_id(trial_id)
                if trial:
                    comparison_data.append({
                        "Trial ID": trial_id[:15] + "...",
                        "Disease": trial['disease_name'],
                        "Drug": trial['drug_name'],
                        "Size (nm)": trial['np_size_nm'],
                        "Charge (mV)": trial['np_charge_mv'],
                        "PEG (%)": trial['np_peg_percent'],
                        "Status": trial['status'],
                        "Created": trial['creation_timestamp'][:10],
                    })
            
            st.markdown("### Comparison Matrix")
            st.dataframe(comparison_data, use_container_width=True, hide_index=True)
            
            st.divider()
            
            st.markdown("### Export & Download Options")
            col1, col2, col3 = st.columns(3)
            
            # Export as JSON
            with col1:
                if st.button("📄 Export as JSON", key="comparison_json"):
                    comparison_json = json.dumps(comparison_data, indent=2)
                    st.download_button(
                        label="⬇️ Download JSON",
                        data=comparison_json,
                        file_name=f"trial_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="comparison_json_download"
                    )
            
            # Generate individual PDFs
            with col2:
                if st.button("🔄 Generate Individual PDFs", key="generate_comparison_pdfs"):
                    pdf_files = {}
                    progress_bar = st.progress(0)
                    
                    for idx, trial_id in enumerate(selected_trials):
                        trial = get_trial_by_id(trial_id)
                        if trial:
                            with st.spinner(f"Generating PDF for comparison trial {trial_id[:10]}..."):
                                try:
                                    pdf_buffer = generate_trial_pdf_report(trial)
                                    if pdf_buffer and pdf_buffer.getbuffer().nbytes > 0:
                                        pdf_files[trial_id] = pdf_buffer
                                except Exception as e:
                                    st.error(f"Error generating PDF for {trial_id}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(selected_trials))
                    
                    if pdf_files:
                        st.session_state['comparison_pdf_files'] = pdf_files
                        st.success(f"✅ Generated {len(pdf_files)} PDF(s)!")
            
            # Download PDFs
            with col3:
                if 'comparison_pdf_files' in st.session_state:
                    st.info(f"{len(st.session_state['comparison_pdf_files'])} PDFs ready")
            
            # Display download buttons for each PDF
            if 'comparison_pdf_files' in st.session_state:
                st.markdown("#### Download Generated PDFs:")
                pdf_cols = st.columns(min(3, len(st.session_state['comparison_pdf_files'])))
                
                for col_idx, (trial_id, pdf_buffer) in enumerate(st.session_state['comparison_pdf_files'].items()):
                    with pdf_cols[col_idx % 3]:
                        safe_trial_id = trial_id.replace('/', '_')
                        pdf_filename = f"trial_{safe_trial_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        # Ensure buffer is at position 0 for download
                        pdf_buffer.seek(0)
                        st.download_button(
                            label=f"⬇️ {trial_id[:15]}...",
                            data=pdf_buffer,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key=f"comparison_download_{trial_id}"
                        )
    else:
        st.info("No trials available for comparison.")

st.markdown("---")

st.markdown("## Trial Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Export All Trials")
    if st.button("Export All Trials as CSV"):
        trials = get_all_trials()
        if trials:
            import pandas as pd
            df = pd.DataFrame(trials)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"all_trials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

with col2:
    st.markdown("### Trial Statistics")
    trials = get_all_trials()
    if trials:
        status_counts = {}

st.divider()

st.markdown("## Back to Workflow")

# Workflow navigation
render_navigation_buttons(
    current_step=5,
    prev_step_page="pages/02_Design_Calibration.py"
)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Start New Trial", use_container_width=True):
        st.switch_page("pages/00_Disease_Selection.py")
with col2:
    if st.button("🏠 Return to Dashboard", use_container_width=True):
        st.switch_page("App.py")
        disease_counts = {}
        
        for trial in trials:
            # Count by status
            status = trial['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by disease
            disease = trial['disease_name']
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        st.write(f"**Total Trials:** {len(trials)}")
        st.write("**By Status:**")
        for status, count in status_counts.items():
            st.write(f"- {status}: {count}")
        st.write("**By Disease:**")
        for disease, count in disease_counts.items():
            st.write(f"- {disease}: {count}")
