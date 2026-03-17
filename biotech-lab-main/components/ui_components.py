"""
UI Components Module - Reusable UI components for all pages
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.trial_registry import get_trial_by_id

def render_trial_header():
    """
    Render persistent trial header bar
    Shows trial ID, disease, NP parameters, and drug info
    """
    if 'trial_id' in st.session_state and st.session_state.trial_id:
        trial_id = st.session_state.trial_id
        disease_name = st.session_state.get('trial_disease_name', 'Unknown')
        
        # Fetch trial details from registry
        trial_data = get_trial_by_id(trial_id)
        
        # Create header HTML
        header_html = f"""
        <div style="
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 5px solid #00d4ff;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-size: 18px;">Active Trial: {trial_id}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">
                        <b>Disease:</b> {disease_name} | 
                        <b>Drug:</b> {trial_data.get('drug_name', 'N/A') if trial_data else 'N/A'}
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 13px;">
                        <b>NP Params:</b> {trial_data.get('np_size_nm', 'N/A') if trial_data else 'N/A'}nm | 
                        Charge: {trial_data.get('np_charge_mv', 'N/A') if trial_data else 'N/A'}mV | 
                        PEG: {trial_data.get('np_peg_percent', 'N/A') if trial_data else 'N/A'}%
                    </p>
                </div>
                <div style="text-align: right; font-size: 12px;">
                    <p style="margin: 0;">Status: <b>{trial_data.get('status', 'Active') if trial_data else 'Active'}</b></p>
                    <p style="margin: 5px 0 0 0;">Created: {trial_data.get('creation_timestamp', 'N/A')[:16] if trial_data else 'N/A'}</p>
                </div>
            </div>
        </div>
        """
        
        st.markdown(header_html, unsafe_allow_html=True)
        return trial_id
    
    return None

def render_page_navigation(current_page: str):
    """
    Render page navigation breadcrumb
    Shows which step user is on
    """
    pages = {
        "00_Disease_Selection": ("1", "Disease Selection"),
        "01_Design_Parameters": ("2", "Design Parameters"),
        "9_AI_Co_Designer": ("3", "AI Co-Designer"),
        "15_External_Data_Sources": ("4", "External Data"),
        "16_Live_Data_Dashboard": ("5", "Live Dashboard"),
        "17_Data_Analytics": ("6", "Analytics"),
        "10_Trial_History": ("7", "Trial History"),
    }
    
    nav_html = '<div style="display: flex; gap: 10px; margin-bottom: 20px;">'
    
    for page_key, (step, label) in pages.items():
        is_current = current_page == page_key
        style = "background: #1e3c72; color: white;" if is_current else "background: #e0e0e0; color: #333;"
        nav_html += f'<span style="padding: 8px 12px; border-radius: 5px; {style}"><b>Step {step}:</b> {label}</span>'
    
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)
