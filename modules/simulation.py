"""
Delivery Simulation Page - PK/PD Visualization
"""

import streamlit as st
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.pk_model import (
    two_compartment_model,
    calculate_pk_parameters,
    create_pk_plot
)

def show():
    """Display PK/PD simulation interface"""
    st.title("📊 Delivery Simulation (PK/PD)")
    st.markdown("Visualize drug delivery kinetics with two-compartment pharmacokinetic modeling")
    
    st.markdown("---")
    
    # Display current design
    with st.expander("📋 Current Design Parameters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Formulation", st.session_state.design['name'])
            st.metric("Material", st.session_state.design['material'].split('(')[0].strip())
        
        with col2:
            st.metric("Size", f"{st.session_state.design['size']:.1f} nm")
            st.metric("Charge", f"{st.session_state.design['charge']:.1f} mV")
        
        with col3:
            st.metric("Payload", st.session_state.design['payload'])
            st.metric("Dose", f"{st.session_state.design['dose']:.1f} mg/kg")
        
        with col4:
            st.metric("Target", st.session_state.design['target'])
            st.metric("PDI", f"{st.session_state.design['pdi']:.2f}")
    
    st.markdown("---")
    
    # Simulation parameters
    st.subheader("⚙️ Simulation Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.slider(
            "Simulation Duration (hours)",
            min_value=12,
            max_value=168,
            value=48,
            step=6,
            help="Total time to simulate (1 week = 168 hours)"
        )
    
    with col2:
        time_step = st.select_slider(
            "Time Resolution",
            options=[0.05, 0.1, 0.25, 0.5, 1.0],
            value=0.1,
            format_func=lambda x: f"{x} hours",
            help="Smaller values = smoother curves but slower computation"
        )
    
    st.markdown("---")
    
    # Run simulation button
    col_run1, col_run2, col_run3 = st.columns([1, 1, 1])
    
    with col_run2:
        if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
            with st.spinner("Running two-compartment PK model..."):
                # Run simulation
                time, C_plasma, C_tissue = two_compartment_model(
                    dose=st.session_state.design['dose'],
                    kabs=st.session_state.design['kabs'],
                    kel=st.session_state.design['kel'],
                    k12=st.session_state.design['k12'],
                    k21=st.session_state.design['k21'],
                    duration=duration,
                    dt=time_step
                )
                
                # Calculate PK parameters
                pk_params = calculate_pk_parameters(time, C_plasma, C_tissue)
                
                # Store results
                st.session_state.simulation_results = {
                    'time': time,
                    'C_plasma': C_plasma,
                    'C_tissue': C_tissue,
                    'pk_params': pk_params
                }
                
                st.success("✅ Simulation completed successfully!")
    
    st.markdown("---")
    
    # Display results if available
    if st.session_state.simulation_results is not None:
        st.subheader("📈 Simulation Results")
        
        results = st.session_state.simulation_results
        pk_params = results['pk_params']
        
        # Key PK parameters
        st.markdown("### 🔑 Key Pharmacokinetic Parameters")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Plasma C_max",
                f"{pk_params['C_max_plasma']:.2f}",
                help="Peak concentration in plasma"
            )
            st.metric(
                "Plasma T_max",
                f"{pk_params['T_max_plasma']:.1f} h",
                help="Time to reach peak plasma concentration"
            )
        
        with col2:
            st.metric(
                "Tissue C_max",
                f"{pk_params['C_max_tissue']:.2f}",
                help="Peak concentration in tissue"
            )
            st.metric(
                "Tissue T_max",
                f"{pk_params['T_max_tissue']:.1f} h",
                help="Time to reach peak tissue concentration"
            )
        
        with col3:
            st.metric(
                "AUC Plasma",
                f"{pk_params['AUC_plasma']:.1f}",
                help="Total plasma exposure over time"
            )
            st.metric(
                "AUC Tissue",
                f"{pk_params['AUC_tissue']:.1f}",
                help="Total tissue exposure over time"
            )
        
        with col4:
            if pk_params['t_half_plasma'] is not None:
                st.metric(
                    "Plasma t₁/₂",
                    f"{pk_params['t_half_plasma']:.1f} h",
                    help="Plasma half-life"
                )
            else:
                st.metric("Plasma t₁/₂", "N/A", help="Cannot determine half-life")
            
            st.metric(
                "Tissue Accumulation",
                f"{pk_params['tissue_accumulation_ratio']:.2f}",
                help="AUC tissue / AUC plasma ratio"
            )
        
        st.markdown("---")
        
        # Visualization
        st.markdown("### 📊 Concentration-Time Profiles")
        
        fig = create_pk_plot(
            results['time'],
            results['C_plasma'],
            results['C_tissue'],
            pk_params,
            st.session_state.design
        )
        
        st.pyplot(fig)
        
        st.markdown("---")
        
        # Interpretation
        st.markdown("### 💡 Interpretation")
        
        interpretation_col1, interpretation_col2 = st.columns(2)
        
        with interpretation_col1:
            st.markdown("**Distribution Phase:**")
            if pk_params['T_max_tissue'] > pk_params['T_max_plasma']:
                st.info(f"✅ Tissue peak delayed by {pk_params['T_max_tissue'] - pk_params['T_max_plasma']:.1f} hours - typical distribution kinetics")
            else:
                st.warning("⚠️ Tissue peaks earlier than plasma - verify parameters")
            
            st.markdown("**Tissue Targeting:**")
            if pk_params['tissue_accumulation_ratio'] > 1.5:
                st.success(f"✅ Strong tissue accumulation (ratio: {pk_params['tissue_accumulation_ratio']:.2f})")
            elif pk_params['tissue_accumulation_ratio'] > 1.0:
                st.info(f"✓ Moderate tissue accumulation (ratio: {pk_params['tissue_accumulation_ratio']:.2f})")
            else:
                st.warning(f"⚠️ Limited tissue accumulation (ratio: {pk_params['tissue_accumulation_ratio']:.2f})")
        
        with interpretation_col2:
            st.markdown("**Plasma Clearance:**")
            if pk_params['t_half_plasma'] is not None:
                if pk_params['t_half_plasma'] < 6:
                    st.warning(f"⚠️ Rapid clearance (t₁/₂ = {pk_params['t_half_plasma']:.1f} h) - may need PEGylation")
                elif pk_params['t_half_plasma'] < 24:
                    st.info(f"✓ Moderate circulation time (t₁/₂ = {pk_params['t_half_plasma']:.1f} h)")
                else:
                    st.success(f"✅ Extended circulation (t₁/₂ = {pk_params['t_half_plasma']:.1f} h)")
            
            st.markdown("**Peak Concentration:**")
            if pk_params['C_max_plasma'] > 3 * pk_params['C_max_tissue']:
                st.info("High plasma exposure - consider dose adjustment")
            elif pk_params['C_max_tissue'] > pk_params['C_max_plasma']:
                st.success("Favorable tissue targeting profile")
        
        st.markdown("---")
        
        # Download options
        st.markdown("### 💾 Export Data")
        
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        with col_dl1:
            # Export concentration data as CSV
            import pandas as pd
            
            df_results = pd.DataFrame({
                'Time (h)': results['time'],
                'Plasma Concentration': results['C_plasma'],
                'Tissue Concentration': results['C_tissue']
            })
            
            csv_data = df_results.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Concentration Data (CSV)",
                data=csv_data,
                file_name=f"{st.session_state.design['name']}_pk_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_dl2:
            # Export PK parameters
            df_params = pd.DataFrame([pk_params])
            csv_params = df_params.to_csv(index=False)
            
            st.download_button(
                label="📥 Download PK Parameters (CSV)",
                data=csv_params,
                file_name=f"{st.session_state.design['name']}_pk_params.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_dl3:
            # Export plot
            from io import BytesIO
            
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="📥 Download Plot (PNG)",
                data=buf,
                file_name=f"{st.session_state.design['name']}_pk_plot.png",
                mime="image/png",
                use_container_width=True
            )
    
    else:
        st.info("👆 Click **Run Simulation** to generate pharmacokinetic profiles")
        
        # Display sample information
        with st.expander("ℹ️ About Two-Compartment PK Model"):
            st.markdown("""
            ### Model Description
            
            The **two-compartment pharmacokinetic model** simulates drug distribution in the body:
            
            **Central Compartment (Plasma):**
            - Represents blood/plasma
            - Rapid equilibration
            - Site of elimination
            
            **Peripheral Compartment (Tissue):**
            - Represents target tissue or organs
            - Slower equilibration
            - Site of therapeutic action
            
            ### Key Parameters
            
            - **k_abs**: Absorption rate from administration site
            - **k_el**: Elimination rate (metabolism + excretion)
            - **k_12**: Transfer rate from plasma to tissue
            - **k_21**: Transfer rate from tissue back to plasma
            
            ### Interpretation
            
            - **High AUC_tissue/AUC_plasma**: Good tissue targeting
            - **Long t₁/₂**: Extended circulation (stealth effect)
            - **Early T_max_tissue**: Rapid tissue accumulation
            
            This model helps predict:
            - ✅ Optimal dosing regimens
            - ✅ Tissue accumulation kinetics
            - ✅ Clearance and circulation time
            - ✅ Need for PEGylation or surface modification
            """)
