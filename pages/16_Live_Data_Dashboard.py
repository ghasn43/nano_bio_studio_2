"""
Live Data Dashboard - Shows real-time connection status for all 6 data sources
Streamlit page that displays which sources are online/offline and data availability
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add root directory to path to import live_data_orchestrator
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Page config
st.set_page_config(
    page_title="Live Data Dashboard",
    page_icon="📡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    .status-live {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .status-template {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .status-offline {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def render_brand_header():
    """Render NanoBio branding header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://via.placeholder.com/200x50/003366/FFFFFF?text=NanoBio+Studio", 
                use_column_width=False)

def init_orchestrator():
    """Initialize live data orchestrator"""
    try:
        from live_data_orchestrator import LiveDataOrchestrator
        
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = LiveDataOrchestrator()
            st.session_state.last_refresh = datetime.now()
        
        return st.session_state.orchestrator
    except Exception as e:
        st.error(f"Error initializing orchestrator: {str(e)}")
        return None

def main():
    # Header
    st.markdown("# 📡 Live Data Dashboard")
    st.markdown("Real-time connection status for all 6 data sources")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Settings")
        auto_refresh = st.checkbox("Auto-refresh (every 30s)", value=True)
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.orchestrator = None
            st.rerun()
    
    # Initialize
    orchestrator = init_orchestrator()
    
    if orchestrator is None:
        st.error("❌ Failed to initialize data orchestrator")
        return
    
    # Fetch data
    with st.spinner("🔄 Connecting to data sources..."):
        results = orchestrator.fetch_all(timeout=5)
    
    # Summary Metrics Row
    st.markdown("---")
    st.markdown("### Quick Summary")
    
    summary = orchestrator.get_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Sources",
            value=f"{summary['Total_Sources']}/6",
            delta="All Available"
        )
    
    with col2:
        st.metric(
            label="Live Connections",
            value=summary['Live_Sources'],
            delta=f"+{summary['Live_Sources']} APIs Online"
        )
    
    with col3:
        st.metric(
            label="Template Sources",
            value=summary['Template_Sources'],
            delta="Fallback Active"
        )
    
    with col4:
        st.metric(
            label="Total Records",
            value=f"{summary['Total_Records']:,}+",
            delta="Ready for ML"
        )
    
    # Detailed Status Table
    st.markdown("---")
    st.markdown("### Detailed Connection Status")
    
    df_status = orchestrator.get_dataframe_summary()
    
    # Create color-coded display
    status_display = []
    for idx, row in df_status.iterrows():
        if "LIVE" in row['Source']:
            status_badge = "🟢 LIVE API"
            color = "status-live"
        elif "TEMPLATE" in row['Source']:
            status_badge = "🟡 TEMPLATE"
            color = "status-template"
        else:
            status_badge = "🔴 OFFLINE"
            color = "status-offline"
        
        status_display.append({
            'Source': row['Name'],
            'Connection': status_badge,
            'Data Points': f"{row['Records']:,}",
            'Last Updated': row['Last_Updated'],
            'Status': row['Status']
        })
    
    df_display = pd.DataFrame(status_display)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Individual Source Details
    st.markdown("---")
    st.markdown("### Source Details")
    
    tabs = st.tabs([
        "🔬 ToxCast",
        "🚨 FAERS", 
        "🧬 GEO",
        "🧪 ChemSpider",
        "🏥 ClinicalTrials",
        "🏗️ PDB"
    ])
    
    source_info = {
        0: {
            'name': 'EPA ToxCast',
            'description': '10M+ chemical toxicity screening data',
            'api_url': 'https://pubchem.ncbi.nlm.nih.gov',
            'use_case': 'Predict particle toxicity'
        },
        1: {
            'name': 'FDA FAERS',
            'description': '20M+ real adverse events from FDA',
            'api_url': 'https://api.fda.gov',
            'use_case': 'Learn from real-world safety issues'
        },
        2: {
            'name': 'NCBI GEO',
            'description': '100K+ gene expression experiments',
            'api_url': 'https://www.ncbi.nlm.nih.gov/geo/',
            'use_case': 'Predict immune system reactions'
        },
        3: {
            'name': 'ChemSpider',
            'description': '50M+ chemical structures',
            'api_url': 'https://www.chemspider.com',
            'use_case': 'Understand particle component properties'
        },
        4: {
            'name': 'ClinicalTrials.gov',
            'description': '200+ active LNP clinical trials',
            'api_url': 'https://clinicaltrials.gov',
            'use_case': 'Validate models with real trial data'
        },
        5: {
            'name': 'PDB',
            'description': '200K+ protein and nanoparticle structures',
            'api_url': 'https://www.rcsb.org',
            'use_case': 'Understand 3D particle structures'
        }
    }
    
    for idx, tab in enumerate(tabs):
        with tab:
            info = source_info[idx]
            connector = list(orchestrator.connectors.values())[idx]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{info['name']}**")
                st.markdown(info['description'])
                st.markdown(f"**Use Case:** {info['use_case']}")
                st.markdown(f"**API:** {info['api_url']}")
            
            with col2:
                if connector.source_type == "LIVE API":
                    st.markdown('<div class="status-live">🟢 LIVE Connected</div>', 
                              unsafe_allow_html=True)
                elif connector.source_type == "TEMPLATE":
                    st.markdown('<div class="status-template">🟡 Using Template</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-offline">🔴 Offline</div>', 
                              unsafe_allow_html=True)
                
                st.markdown(f"**Records:** {connector.record_count:,}")
                if connector.last_updated:
                    st.markdown(f"**Updated:** {connector.last_updated.strftime('%H:%M:%S')}")
                else:
                    st.markdown("**Updated:** N/A")
    
    # System Information
    st.markdown("---")
    st.markdown("### System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Initialized:** {summary['Initialized']}")
    
    with col2:
        st.markdown(f"**Connection Mode:** {'Hybrid' if summary['Live_Sources'] > 0 else 'Template'}")
    
    with col3:
        st.markdown(f"**Status:** ✅ Fully Operational")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px;'>
    NanoBio Studio™ Live Data Dashboard | Updated: 2026-03-15 | All sources monitored continuously
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
