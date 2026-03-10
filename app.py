"""
NanoBio Studio — Connecting Nanotech × Biotech
An interactive Streamlit application for nanoparticle design and drug delivery simulation

Developed by: Experts Group FZE
Copyright © 2026 Experts Group FZE. All rights reserved.
Intellectual Property Rights: Ghassan Muammar

Contact:
Email: info@expertsgroup.me
Website: https://www.expertsgroup.me
"""

import streamlit as st
import json
import os
from pathlib import Path
from auth import AuthManager
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="NanoBio Studio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication
auth_manager = AuthManager()

# Session timeout settings (30 minutes)
SESSION_TIMEOUT_MINUTES = 30

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.show_signup = False
    st.session_state.login_time = None
    st.session_state.last_activity = None
    st.session_state.session_token = None

# Try to restore session from query params on first load
if 'session_checked' not in st.session_state:
    st.session_state.session_checked = True
    
    # Check for session token in query params
    query_params = st.query_params
    if 'session' in query_params:
        session_token = query_params['session']
        user = auth_manager.validate_session(session_token)
        
        if user:
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.session_token = session_token
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()

# Check session timeout
def check_session_timeout():
    """Check if session has expired"""
    if st.session_state.authenticated and st.session_state.session_token:
        # Validate with server-side session
        user = auth_manager.validate_session(st.session_state.session_token)
        if not user:
            # Session expired on server
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.login_time = None
            st.session_state.last_activity = None
            st.session_state.session_token = None
            st.query_params.clear()
            return True
    return False

# Update last activity time
def update_activity():
    """Update last activity timestamp"""
    if st.session_state.authenticated:
        st.session_state.last_activity = datetime.now()

# Initialize session state
if 'design' not in st.session_state:
    st.session_state.design = {
        'name': 'NP-001',
        'material': 'Lipid Nanoparticle',
        'size': 100.0,
        'charge': -10.0,
        'ligand': 'PEG',
        'payload': 'mRNA',
        'payload_amount': 50.0,
        'target': 'Tumor Tissue',
        'dose': 5.0,
        'pdi': 0.15,
        'kabs': 0.5,
        'kel': 0.1,
        'k12': 0.3,
        'k21': 0.2
    }

if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

if 'cost_results' not in st.session_state:
    st.session_state.cost_results = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def show_login_page():
    """Display login/signup page"""
    st.markdown('<div class="main-header">🧬 NanoBio Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Connecting Nanotechnology × Biotechnology</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_signup:
            # Login Form
            st.markdown("### 🔐 Login")
            st.markdown("---")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if username and password:
                        user = auth_manager.authenticate(username, password)
                        if user:
                            # Create persistent session
                            session_token = auth_manager.create_session(user['username'])
                            
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.session_token = session_token
                            st.session_state.login_time = datetime.now()
                            st.session_state.last_activity = datetime.now()
                            
                            # Set session in URL
                            st.query_params['session'] = session_token
                            
                            st.success(f"Welcome back, {user['full_name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
            
            st.markdown("---")
            if st.button("Don't have an account? Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
            
            st.info("**Default Admin Account:**\n\nUsername: `admin`\n\nPassword: `admin123`")
            
            # Copyright notice on login page
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: #888; font-size: 0.85rem;">
                <p>© 2026 <strong>Experts Group FZE</strong></p>
                <p><strong>IP Rights:</strong> Ghassan Muammar</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Signup Form
            st.markdown("### ✍️ Sign Up")
            st.markdown("---")
            
            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="Enter your email")
                new_fullname = st.text_input("Full Name", placeholder="Enter your full name")
                new_password = st.text_input("Password", type="password", placeholder="Choose a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                submit = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit:
                    if new_username and new_email and new_fullname and new_password:
                        if new_password == confirm_password:
                            if len(new_password) >= 6:
                                success, message = auth_manager.register_user(
                                    new_username, new_password, new_email, new_fullname
                                )
                                if success:
                                    st.success(message + " Please login with your credentials.")
                                    st.session_state.show_signup = False
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("Password must be at least 6 characters long")
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.warning("Please fill in all fields")
            
            st.markdown("---")
            if st.button("Already have an account? Login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()
            
            # Copyright notice on signup page
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: #888; font-size: 0.85rem;">
                <p>© 2026 <strong>Experts Group FZE</strong></p>
                <p><strong>IP Rights:</strong> Ghassan Muammar</p>
            </div>
            """, unsafe_allow_html=True)

def show_admin_panel():
    """Display admin panel for user management"""
    st.markdown("### 👥 User Management (Admin Only)")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["📋 View Users", "➕ Add User", "✏️ Edit User"])
    
    # Tab 1: View Users
    with tab1:
        st.markdown("---")
        users = auth_manager.get_all_users()
        st.markdown(f"**Total Users:** {len(users)}")
        st.markdown("---")
        
        # Display users in a table
        for user in users:
            with st.expander(f"👤 {user['username']} ({user['role'].title()})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Full Name:** {user['full_name']}")
                    st.write(f"**Email:** {user['email']}")
                with col2:
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Role:** {user['role'].title()}")
                
                if user['username'] != "admin":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🗑️ Delete User", key=f"delete_{user['username']}", use_container_width=True):
                            success, message = auth_manager.delete_user(user['username'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
    
    # Tab 2: Add User
    with tab2:
        st.markdown("---")
        st.markdown("#### Add New User")
        
        with st.form("admin_add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username*", placeholder="Enter username")
                new_email = st.text_input("Email*", placeholder="Enter email")
            with col2:
                new_fullname = st.text_input("Full Name*", placeholder="Enter full name")
                new_role = st.selectbox("Role*", ["user", "admin"])
            
            new_password = st.text_input("Password*", type="password", placeholder="Enter password (min 6 chars)")
            
            submit = st.form_submit_button("➕ Add User", use_container_width=True)
            
            if submit:
                if new_username and new_email and new_fullname and new_password:
                    if len(new_password) >= 6:
                        success, message = auth_manager.register_user(
                            new_username, new_password, new_email, new_fullname, new_role
                        )
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Password must be at least 6 characters long")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    # Tab 3: Edit User
    with tab3:
        st.markdown("---")
        users = auth_manager.get_all_users()
        usernames = [u['username'] for u in users]
        
        selected_user = st.selectbox("Select User to Edit", usernames)
        
        if selected_user:
            user_details = auth_manager.get_user_details(selected_user)
            
            if user_details:
                st.markdown("---")
                
                # Edit Username
                with st.expander("📝 Change Username"):
                    with st.form(f"edit_username_{selected_user}"):
                        new_username_edit = st.text_input("New Username", value=selected_user)
                        submit_username = st.form_submit_button("Update Username")
                        
                        if submit_username:
                            if new_username_edit and new_username_edit != selected_user:
                                success, message = auth_manager.update_username(selected_user, new_username_edit)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                            elif new_username_edit == selected_user:
                                st.info("ℹ️ Username is the same")
                
                # Reset Password
                with st.expander("🔑 Reset Password"):
                    with st.form(f"reset_password_{selected_user}"):
                        new_password_admin = st.text_input("New Password", type="password", placeholder="Enter new password (min 6 chars)")
                        confirm_password_admin = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
                        submit_password = st.form_submit_button("Reset Password")
                        
                        if submit_password:
                            if new_password_admin and confirm_password_admin:
                                if new_password_admin == confirm_password_admin:
                                    if len(new_password_admin) >= 6:
                                        success, message = auth_manager.admin_reset_password(selected_user, new_password_admin)
                                        if success:
                                            st.success(f"✅ {message}")
                                        else:
                                            st.error(f"❌ {message}")
                                    else:
                                        st.error("❌ Password must be at least 6 characters long")
                                else:
                                    st.error("❌ Passwords do not match")
                            else:
                                st.warning("⚠️ Please fill in both password fields")
                
                # Edit Role
                with st.expander("👤 Change Role"):
                    with st.form(f"edit_role_{selected_user}"):
                        current_role = user_details['role']
                        new_role_edit = st.selectbox("Role", ["user", "admin"], index=0 if current_role == "user" else 1)
                        submit_role = st.form_submit_button("Update Role")
                        
                        if submit_role:
                            if new_role_edit != current_role:
                                success, message = auth_manager.update_user_role(selected_user, new_role_edit)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.info("ℹ️ Role is the same")
                
                # Edit User Info
                with st.expander("📧 Update User Information"):
                    with st.form(f"edit_info_{selected_user}"):
                        new_email_edit = st.text_input("Email", value=user_details['email'])
                        new_fullname_edit = st.text_input("Full Name", value=user_details['full_name'])
                        submit_info = st.form_submit_button("Update Information")
                        
                        if submit_info:
                            success, message = auth_manager.update_user_info(selected_user, new_email_edit, new_fullname_edit)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

# Main navigation
def main():
    # Update activity timestamp
    update_activity()
    
    st.markdown('<div class="main-header">🧬 NanoBio Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Connecting Nanotechnology × Biotechnology</div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # User info and logout
        st.markdown("---")
        st.markdown(f"**Welcome, {st.session_state.user['full_name']}!**")
        st.markdown(f"Role: {st.session_state.user['role'].title()}")
        
        # Show session time remaining
        if st.session_state.last_activity:
            time_elapsed = datetime.now() - st.session_state.last_activity
            time_remaining = timedelta(minutes=SESSION_TIMEOUT_MINUTES) - time_elapsed
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            
            if minutes_remaining > 0:
                st.caption(f"⏱️ Session: {minutes_remaining} min remaining")
            else:
                st.caption("⏱️ Session expired")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Delete server-side session
            if st.session_state.session_token:
                auth_manager.delete_session(st.session_state.session_token)
            
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.login_time = None
            st.session_state.last_activity = None
            st.session_state.session_token = None
            
            # Clear URL params
            st.query_params.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Navigation menu
        menu_items = [
            "🏠 Home",
            "📚 Materials & Targets",
            "🎨 Design Nanoparticle",
            "📈 Delivery Simulation",
            "⚠️ Toxicity & Safety",
            "💰 Cost Estimator",
            "🤖 Protocol Generator",
            "💾 Import / Export",
            "📘 Tutorial",
            "🧑‍🏫 Instructor Notes"
        ]
        
        # Add admin panel for admin users
        if st.session_state.user['role'] == 'admin':
            menu_items.append("👥 Admin Panel")
        
        page = st.radio(
            "Navigation",
            menu_items,
            key="navigation"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info("**NanoBio Studio v1.0**\n\n© 2026 Experts Group FZE\nAll Rights Reserved\n\n**IP Rights:** Ghassan Muammar\n\n📧 info@expertsgroup.me")
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home()
    elif page == "📚 Materials & Targets":
        show_materials_targets()
    elif page == "🎨 Design Nanoparticle":
        show_design()
    elif page == "📈 Delivery Simulation":
        show_simulation()
    elif page == "⚠️ Toxicity & Safety":
        show_toxicity()
    elif page == "💰 Cost Estimator":
        show_cost()
    elif page == "🤖 Protocol Generator":
        show_protocol()
    elif page == "💾 Import / Export":
        show_import_export()
    elif page == "📘 Tutorial":
        show_tutorial()
    elif page == "🧑‍🏫 Instructor Notes":
        show_instructor()
    elif page == "👥 Admin Panel":
        show_admin_panel()

def show_home():
    """Home page with overview"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🔬 Design</h3>
            <p>Create custom nanoparticles with precise control over physicochemical properties</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>📊 Simulate</h3>
            <p>Visualize drug delivery kinetics with PK/PD modeling</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3>📝 Generate</h3>
            <p>Auto-create experimental protocols and cost estimates</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## 🧩 Core Features")
    
    features = {
        "1️⃣ Materials & Targets": "Browse or upload nanoparticle and biological target libraries",
        "2️⃣ Design Nanoparticle": "Adjust size, charge, ligand, payload, and pharmacokinetic parameters",
        "3️⃣ Delivery Simulation": "Two-compartment simulation showing tissue vs plasma concentration",
        "4️⃣ Toxicity & Safety": "Heuristic risk scoring (size, charge, dose, PDI, steric)",
        "5️⃣ Cost Estimator": "Batch-level and per-subject cost calculation",
        "6️⃣ Protocol Generator": "Auto-generates experimental outline with AI assistance",
        "7️⃣ Import / Export": "Save or reload designs as JSON and export tables as CSV",
        "📘 Tutorial": "Built-in classroom guide with learning objectives",
        "🧑‍🏫 Instructor Notes": "Password-protected teaching resources"
    }
    
    for feature, description in features.items():
        st.markdown(f"**{feature}**: {description}")
    
    st.markdown("---")
    
    st.markdown("## 🚀 Quick Start")
    st.markdown("""
    1. **Explore Materials** - Browse available nanoparticle types and biological targets
    2. **Design Your Nanoparticle** - Adjust parameters to create your formulation
    3. **Run Simulation** - See how your design behaves in the body
    4. **Evaluate Safety** - Check toxicity risk scores
    5. **Estimate Costs** - Calculate production and clinical costs
    6. **Generate Protocol** - Create experimental documentation
    """)
    
    st.success("👈 Use the sidebar to navigate through different modules")
    
    # Copyright footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666;">
        <p><strong>NanoBio Studio</strong> - Connecting Nanotechnology × Biotechnology</p>
        <p>© 2026 <strong>Experts Group FZE</strong>. All Rights Reserved.</p>
        <p><strong>Intellectual Property Rights:</strong> Ghassan Muammar</p>
        <p>📧 info@expertsgroup.me | 🌐 www.expertsgroup.me</p>
    </div>
    """, unsafe_allow_html=True)

def show_materials_targets():
    """Materials and Targets library page"""
    from modules import materials_targets
    materials_targets.show()

def show_design():
    """Nanoparticle design page"""
    from modules import design
    design.show()

def show_simulation():
    """PK/PD simulation page"""
    from modules import simulation
    simulation.show()

def show_toxicity():
    """Toxicity and safety page"""
    from modules import toxicity
    toxicity.show()

def show_cost():
    """Cost estimator page"""
    from modules import cost
    cost.show()

def show_protocol():
    """Protocol generator page"""
    from modules import protocol
    protocol.show()

def show_import_export():
    """Import/Export page"""
    from modules import import_export
    import_export.show()

def show_tutorial():
    """Tutorial page"""
    from modules import tutorial
    tutorial.show()

def show_instructor():
    """Instructor notes page"""
    from modules import instructor
    instructor.show()

if __name__ == "__main__":
    # Check for session timeout
    if check_session_timeout():
        st.warning("⏱️ Your session has expired after 30 minutes of inactivity. Please login again.")
        st.session_state.show_signup = False
        show_login_page()
    # Check authentication
    elif not st.session_state.authenticated:
        show_login_page()
    else:
        main()
