"""
Sidebar Navigation Renderer
Displays unified navigation structure in Streamlit sidebar
"""

import streamlit as st
from components.navigation_config import NAVIGATION_STRUCTURE

def render_sidebar_navigation():
    """
    Render the unified sidebar navigation menu
    Organized by categories with descriptions
    """
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📋 Navigation Menu")
        st.markdown("---")
        
        # Display each category
        for category, config in NAVIGATION_STRUCTURE.items():
            # Category header with expander
            with st.expander(f"**{category}**", expanded=False):
                description = config.get("description", "")
                if description:
                    st.caption(description)
                
                pages = config.get("pages", [])
                
                if pages:
                    # Handle both string and dict page formats
                    for page in pages:
                        if isinstance(page, dict):
                            name = page.get("name", "Unknown")
                            file_path = page.get("file", "")
                            description = page.get("description", "")
                            
                            # Create clickable page link
                            if st.button(
                                f"➡️ {name}",
                                use_container_width=True,
                                key=f"nav_{file_path}"
                            ):
                                st.switch_page(file_path)
                            
                            if description:
                                st.caption(description)
                        
                        elif isinstance(page, str):
                            # Simple string page reference
                            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                                st.switch_page(page)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Info")
        if 'trial_id' in st.session_state and st.session_state.trial_id:
            st.success(f"**Trial Active**")
            st.caption(st.session_state.trial_id[:20] + "...")
        else:
            st.info("No active trial")
        
        # User info
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            st.markdown("---")
            st.markdown(f"**User:** {st.session_state.username}")
            if 'role' in st.session_state:
                st.markdown(f"**Role:** {st.session_state.role}")

def render_mobile_navigation():
    """
    Render a simpler navigation for mobile devices
    Uses selectbox instead of expanders for better mobile UX
    """
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 🧭 Go To")
        
        # Create a flat list of all pages
        nav_options = ["Select a page..."]
        nav_map = {}
        
        for category, config in NAVIGATION_STRUCTURE.items():
            pages = config.get("pages", [])
            for page in pages:
                if isinstance(page, dict):
                    name = page.get("name", "Unknown")
                    file_path = page.get("file", "")
                    display_name = f"{category} → {name}"
                    nav_options.append(display_name)
                    nav_map[display_name] = file_path
        
        selected = st.selectbox(
            "Navigate to:",
            nav_options,
            label_visibility="collapsed"
        )
        
        if selected != "Select a page..." and selected in nav_map:
            st.switch_page(nav_map[selected])
