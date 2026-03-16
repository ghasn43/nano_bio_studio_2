"""
Design Calibration - Step 3 of NP design workflow
Manual parameter tuning with real-time optimization scoring
"""
import streamlit as st
import sys
import os
import numpy as np
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.disease_database import (
    get_disease_design_parameters,
    get_disease_name
)
from modules.ml_disease_connector import score_design_for_disease
from modules.trial_registry import update_trial_status
from components.ui_components import render_trial_header
from components.workflow_guide import render_workflow_progress, render_step_header, render_navigation_buttons

st.set_page_config(page_title="Design Calibration", layout="wide")

st.markdown("""
<style>
.calibration-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.score-gauge {
    text-align: center;
    padding: 20px;
}
.slider-group {
    background: #f0f2f6;
    padding: 15px;
    border-radius: 8px;
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

render_step_header(3)

# Get recommended parameters
params = get_disease_design_parameters(hcc_subtype)

if not params:
    st.error("Could not load design parameters")
    st.stop()

st.markdown("## Current Design Parameters")

# Initialize calibration values in session state
if 'calibration_size' not in st.session_state:
    st.session_state.calibration_size = int(params.size_nm_optimal)
if 'calibration_charge' not in st.session_state:
    st.session_state.calibration_charge = int(params.charge_value)
if 'calibration_peg' not in st.session_state:
    st.session_state.calibration_peg = float(params.peg_coating_percent)
if 'calibration_drug_loading' not in st.session_state:
    st.session_state.calibration_drug_loading = float((params.drug_loading_percent_min + params.drug_loading_percent_max) / 2)

# Create tabs for viewing and adjusting
tab1, tab2 = st.tabs(["Recommended Values", "Manual Calibration"])

with tab1:
    st.markdown("### Recommended Design Parameters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Size Range", f"{params.size_nm_min}-{params.size_nm_max} nm")
        st.caption(f"Optimal: {params.size_nm_optimal} nm")
    
    with col2:
        st.metric("Surface Charge", f"{params.charge_value} mV")
        st.caption("For liver targeting")
    
    with col3:
        st.metric("PEG Coverage", f"{params.peg_coating_percent}%")
        st.caption("Immune evasion")
    
    with col4:
        st.metric("Drug Loading", f"{params.drug_loading_percent_min}-{params.drug_loading_percent_max}%")
        st.caption(f"Range for {disease_name}")
    
    st.markdown("---")
    st.info("""
    ℹ️ **Why these values?**
    - **Size**: Small enough for tissue penetration, large enough for drug payload
    - **Charge**: Optimized for hepatic targeting and RES evasion
    - **PEG**: Stealth coating for extended circulation time
    - **Drug Loading**: Balances efficacy with stability
    """)

with tab2:
    st.markdown("### Manual Parameter Tuning")
    st.write("Adjust the sliders below to fine-tune your nanoparticle design. The scoring dial updates in real-time.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='slider-group'>", unsafe_allow_html=True)
        
        # Size slider
        st.markdown("#### 📏 Particle Size (nm)")
        size_val = st.slider(
            "Size",
            min_value=int(params.size_nm_min),
            max_value=int(params.size_nm_max),
            value=int(st.session_state.calibration_size),
            step=1,
            label_visibility="collapsed",
            key="size_slider"
        )
        st.session_state.calibration_size = size_val
        st.caption(f"Current: **{size_val} nm** | Range: {params.size_nm_min}-{params.size_nm_max} nm")
        
        st.divider()
        
        # Charge slider
        st.markdown("#### ⚛️ Surface Charge (mV)")
        charge_options = list(range(-15, 16))
        charge_val = st.select_slider(
            "Charge",
            options=charge_options,
            value=int(st.session_state.calibration_charge),
            label_visibility="collapsed",
            key="charge_slider"
        )
        st.session_state.calibration_charge = charge_val
        st.caption(f"Current: **{charge_val} mV** | Recommended: {params.charge_value} mV")
        
        st.divider()
        
        # PEG slider
        st.markdown("#### 🛡️ PEG Coverage (%)")
        peg_val = st.slider(
            "PEG",
            min_value=1.0,
            max_value=15.0,
            value=float(st.session_state.calibration_peg),
            step=0.5,
            label_visibility="collapsed",
            key="peg_slider"
        )
        st.session_state.calibration_peg = peg_val
        st.caption(f"Current: **{peg_val}%** | Recommended: {params.peg_coating_percent}%")
        
        st.divider()
        
        # Drug loading slider
        st.markdown("#### 💊 Drug Loading (%)")
        drug_val = st.slider(
            "Drug Loading",
            min_value=float(params.drug_loading_percent_min),
            max_value=float(params.drug_loading_percent_max),
            value=float(st.session_state.calibration_drug_loading),
            step=1.0,
            label_visibility="collapsed",
            key="drug_loading_slider"
        )
        st.session_state.calibration_drug_loading = drug_val
        st.caption(f"Current: **{drug_val}%** | Range: {params.drug_loading_percent_min}-{params.drug_loading_percent_max}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='score-gauge'>", unsafe_allow_html=True)
        st.markdown("#### 📊 Design Score")
        
        # Calculate optimization score
        # Score based on distance from recommended values
        size_diff = abs(size_val - params.size_nm_optimal)
        charge_diff = abs(charge_val - params.charge_value)
        peg_diff = abs(peg_val - params.peg_coating_percent)
        drug_diff = abs(drug_val - (params.drug_loading_percent_min + params.drug_loading_percent_max) / 2)
        
        # Normalize differences to 0-100 score
        max_size_diff = (params.size_nm_max - params.size_nm_min) / 2
        max_charge_diff = 10
        max_peg_diff = 7
        max_drug_diff = (params.drug_loading_percent_max - params.drug_loading_percent_min) / 2
        
        size_score = max(0, 100 - (size_diff / max_size_diff) * 100) if max_size_diff > 0 else 100
        charge_score = max(0, 100 - (charge_diff / max_charge_diff) * 100) if max_charge_diff > 0 else 100
        peg_score = max(0, 100 - (peg_diff / max_peg_diff) * 100) if max_peg_diff > 0 else 100
        drug_score = max(0, 100 - (drug_diff / max_drug_diff) * 100) if max_drug_diff > 0 else 100
        
        overall_score = (size_score + charge_score + peg_score + drug_score) / 4
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={'text': "Optimization Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "#ff6b6b"},
                    {'range': [25, 50], 'color': "#ffd93d"},
                    {'range': [50, 75], 'color': "#95e1d3"},
                    {'range': [75, 100], 'color': "#4ade80"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Score breakdown
        with st.expander("Score Breakdown"):
            st.write(f"**Size Score:** {size_score:.0f}/100 (diff: {size_diff:.1f}nm)")
            st.write(f"**Charge Score:** {charge_score:.0f}/100 (diff: {charge_diff:.1f}mV)")
            st.write(f"**PEG Score:** {peg_score:.0f}/100 (diff: {peg_diff:.1f}%)")
            st.write(f"**Drug Score:** {drug_score:.0f}/100 (diff: {drug_diff:.1f}%)")

st.markdown("---")

st.markdown("## Parameter Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Size Analysis")
    if st.session_state.calibration_size < params.size_nm_min:
        st.warning("⚠️ Below minimum - may not hold drug payload")
    elif st.session_state.calibration_size > params.size_nm_max:
        st.warning("⚠️ Above maximum - may have poor tissue penetration")
    else:
        st.success("✓ Within optimal range")

with col2:
    st.markdown("### Charge Analysis")
    if abs(st.session_state.calibration_charge - params.charge_value) > 5:
        st.info("ℹ️ Significant charge deviation - may affect targeting")
    else:
        st.success("✓ Charge optimized for liver targeting")

with col3:
    st.markdown("### PEG Analysis")
    if st.session_state.calibration_peg >= params.peg_coating_percent:
        st.success("✓ PEG adequate for immune evasion")
    else:
        st.warning("⚠️ Lower PEG - increased RES uptake possible")

st.markdown("---")

st.markdown("## Navigation")

# Workflow navigation
render_navigation_buttons(
    current_step=3,
    prev_step_page="pages/01_Design_Parameters.py",
    next_step_page="pages/10_Trial_History.py"
)

st.markdown("---")

st.markdown("## Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Apply to Design", use_container_width=True):
        st.session_state.applied_design = {
            'size_nm': st.session_state.calibration_size,
            'charge_mv': st.session_state.calibration_charge,
            'peg_percent': st.session_state.calibration_peg,
            'drug_loading': st.session_state.calibration_drug_loading,
            'score': overall_score
        }
        
        if st.session_state.get('trial_id'):
            update_trial_status(
                st.session_state.trial_id,
                'Calibrated',
                f"Manually calibrated design: Size={st.session_state.calibration_size}nm, "
                f"Charge={st.session_state.calibration_charge}mV, PEG={st.session_state.calibration_peg}%, "
                f"Score={overall_score:.1f}"
            )
        
        st.success("✅ Design applied! Ready for AI optimization.")

with col2:
    if st.button("Proceed to AI Co-Designer", use_container_width=True):
        st.switch_page("pages/9_AI_Co_Designer.py")

with col3:
    if st.button("Back to Design Parameters", use_container_width=True):
        st.switch_page("pages/01_Design_Parameters.py")
