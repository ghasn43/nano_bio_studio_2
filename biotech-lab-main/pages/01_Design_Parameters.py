"""
Design Parameters - Step 2 of NP design workflow
Auto-populated from disease and drug selection
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.disease_database import (
    get_disease_design_parameters,
    get_disease_name,
    get_tissue_barrier_analysis
)
from modules.clinical_trials_data import get_trials_for_hcc_subtype
from modules.ml_disease_connector import (
    get_recommendation_for_subtype,
    score_design_for_disease,
    get_similar_designs_for_disease
)
from components.ui_components import render_trial_header
from components.workflow_guide import render_workflow_progress, render_step_header, render_navigation_buttons

st.set_page_config(page_title="Design Parameters", layout="wide")

st.markdown("""
<style>
.param-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.warning-box {
    background: #fff3cd;
    padding: 15px;
    border-left: 4px solid #ff6b6b;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Show workflow progress
render_workflow_progress()

st.divider()

# Display trial header
render_trial_header()

if not st.session_state.get("hcc_subtype"):
    st.warning("Please select disease type first on the Disease Selection page")
    st.stop()

hcc_subtype = st.session_state.hcc_subtype
disease_name = get_disease_name(hcc_subtype)

render_step_header(2)

st.markdown(f"## Disease: {disease_name}")

params = get_disease_design_parameters(hcc_subtype)

if params:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Size (nm)")
        st.metric("Recommended Range", f"{params.size_nm_min}-{params.size_nm_max} nm")
        st.write(f"Core: {params.size_nm_optimal} nm")
    
    with col2:
        st.markdown("### Charge (mV)")
        st.metric("Surface Charge", f"{params.charge_value}")
        st.write("Optimized for liver targeting")
    
    with col3:
        st.markdown("### Surface Modification")
        st.metric("PEG Coverage", f"{params.peg_coating_percent}%")
        st.write(f"Ligand: {params.targeting_ligand.value}")
    
    st.markdown("---")
    
    st.markdown("## Complete Parameter Specifications")
    
    param_table = {
        "Parameter": [
            "Size Range",
            "Surface Charge",
            "PEG Coverage",
            "Targeting Ligand",
            "Drug Loading",
            "Degradation Time"
        ],
        "Value": [
            f"{params.size_nm_min}-{params.size_nm_max} nm",
            f"{params.charge_value} mV",
            f"{params.peg_coating_percent}%",
            params.targeting_ligand.value,
            f"{params.drug_loading_percent_min}-{params.drug_loading_percent_max}%",
            f"{params.biodegradation_hours_min}-{params.biodegradation_hours_max} hours"
        ],
        "Rationale": "Design specifications",
    }
    
    st.dataframe(param_table, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("## Design Rationale")
    
    with st.expander("Why these parameters for this disease?", expanded=True):
        st.write(f"""
**Size Optimization:** {params.size_nm_min}-{params.size_nm_max}nm balances drug payload capacity with tissue penetration.

**Charge Strategy:** {params.charge_value}mV optimizes liver targeting while minimizing RES uptake.

**Surface Modification:** {params.peg_coating_percent}% PEG provides stealth coating and extended circulation time.
        """)
    
    st.markdown("---")
    
    st.markdown("## Tissue Barrier Analysis")
    
    barrier = get_tissue_barrier_analysis(hcc_subtype)
    if barrier:
        col1, col2 = st.columns([1, 2])
        with col1:
            difficulty_text = ["Very Easy", "Easy", "Moderate", "Difficult", "Very Difficult"]
            st.metric("Penetration Difficulty", difficulty_text[barrier['difficulty_level'] - 1])
        with col2:
            st.write("Key challenges:")
            for challenge in barrier['key_challenges']:
                st.write(f"- {challenge}")
        
        with st.expander("Advanced Penetration Strategies"):
            for strategy in barrier['advanced_strategies']:
                st.write(f"- {strategy}")
    
    st.markdown("---")
    
    st.markdown("## Clinical Evidence")
    
    trials = get_trials_for_hcc_subtype(hcc_subtype)
    if trials:
        st.write(f"Top {min(3, len(trials))} relevant clinical trials:")
        for i, trial in enumerate(trials[:3], 1):
            with st.expander(f"{i}. {trial.trial_name} - {', '.join(trial.drug_names)}"):
                st.write(f"Phase: {trial.phase.name}")
                st.write(f"Status: {trial.status.name}")
                st.write(f"Patients: {trial.study_population_count}")
                st.write(f"Primary Endpoint: {trial.primary_endpoint}")
                if trial.median_overall_survival_months:
                    st.write(f"Overall Survival: {trial.median_overall_survival_months} months")
    
    st.markdown("---")
    
    st.markdown("## Cross-Disease Comparison")
    
    comparison_df = {
        "HCC Type": ["HCC-S", "HCC-MS", "HCC-L"],
        "Size Range": ["120 nm", "100 nm", "65 nm"],
        "Charge": ["0 mV", "-5 mV", "-10 mV"],
        "PEG %": ["5%", "7%", "10%"],
        "Drug Loading": ["20-30%", "25-35%", "30-40%"],
        "Design Difficulty": ["Easy", "Medium", "Hard"]
    }
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("## Educational Details")
    
    with st.expander("How were these parameters determined?"):
        st.write("""
        These parameters are derived from:
        1. **Computational modeling** of nanoparticle-cell interactions
        2. **Clinical trial data** from FDA-approved therapies
        3. **Literature consensus** from peer-reviewed publications
        4. **Validation** against experimental results from leading biotech labs
        
        For HCC specifically, the parameters optimize for:
        - Hepatic accumulation (liver targeting)
        - Immune evasion (PEG stealth)
        - Drug efficacy (loading and release kinetics)
        - Safety profile (biodegradation)
        """)
    
    with st.expander("Technical Details - Size Optimization"):
        st.write(f"""
        **Why {params.size_nm_min}-{params.size_nm_max} nm?**
        
        - Large enough for drug payload: >50 nm
        - Small enough for tissue penetration: <150 nm
        - Opsonization window: 70-100 nm optimal for liver
        - Fenestration passage: Liver sinusoid gaps = 100-200 nm
        - Reticuloendothelial uptake minimum: >100 nm (for HCC-MS, HCC-S)
        """)
    
    with st.expander("Technical Details - Charge Optimization"):
        st.write(f"""
        **Why {params.charge_value} mV for {disease_name}?**
        
        - Slightly negative/neutral charge promotes liver targeting
        - Positive charges cause kidney filtration
        - Neutral approaches RES (reticuloendothelial system) stealth
        - Perfect negative (-10 mV) works for aggressive HCC
        - Trade-off: charge vs. immune evasion for each subtype
        """)
    
    st.markdown("---")
    
    st.markdown("## Next Steps")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Launch AI Co-Designer", key="launch_designer"):
            st.switch_page("pages/9_AI_Co_Designer.py")
    with col2:
        if st.button("View Data Analytics", key="view_analytics"):
            st.switch_page("pages/17_Data_Analytics.py")
    
    st.divider()
    
    # Workflow navigation
    render_navigation_buttons(
        current_step=2,
        prev_step_page="pages/00_Disease_Selection.py",
        next_step_page="pages/02_Design_Calibration.py"
    )
