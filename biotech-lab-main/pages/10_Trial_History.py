"""
Trial History Page - View all completed and active trials
"""
import streamlit as st
import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.trial_registry import (
    get_all_trials,
    get_recent_trials,
    get_trial_by_id,
    update_trial_status,
    export_trial_to_json
)
from components.ui_components import render_trial_header
from components.workflow_guide import render_workflow_progress, render_step_header, render_navigation_buttons

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
    else:
        st.warning("No trials found. Start a new trial on the Disease Selection page.")

with tab2:
    st.markdown("## Recent Trials (Last 10)")
    recent = get_recent_trials(limit=10)
    
    if recent:
        for trial in recent:
            with st.expander(f"{trial['trial_id']} - {trial['disease_name']} ({trial['status']})"):
                col1, col2, col3 = st.columns(3)
                
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
                    st.markdown("### Actions")
                    if st.button(f"Load Trial {trial['trial_id'][:10]}", key=f"load_{trial['trial_id']}"):
                        st.session_state.trial_id = trial['trial_id']
                        st.session_state.trial_disease_name = trial['disease_name']
                        st.success("Trial loaded to session!")
                        st.rerun()
                    
                    if st.button(f"Export {trial['trial_id'][:10]}", key=f"export_{trial['trial_id']}"):
                        export_path = export_trial_to_json(trial['trial_id'])
                        if export_path:
                            st.success(f"Exported to: {export_path}")
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
            
            # Export comparison
            if st.button("Export Comparison as JSON"):
                comparison_json = json.dumps(comparison_data, indent=2)
                st.download_button(
                    label="Download Comparison",
                    data=comparison_json,
                    file_name=f"trial_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
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
