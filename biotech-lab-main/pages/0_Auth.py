# ============================================================
# 🔐 Dedicated Login Page for NanoBio Studio
# ============================================================

import streamlit as st
from pathlib import Path
import sys

# Ensure local modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from auth import (
    authenticate, register_user, count_admin_users, setup_admin_account
)

st.set_page_config(page_title="Login - NanoBio Studio", page_icon="🔐", layout="centered")

# ============================================================
# INITIALIZATION
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

# If already logged in, redirect to main app
if st.session_state.logged_in:
    st.info("✅ You're already logged in! Use the sidebar to navigate.")
    st.stop()

# ============================================================
# PAGE HEADER
# ============================================================
col1, col2 = st.columns([2, 3])

with col1:
    st.title("🧬 NanoBio Studio")
    st.caption("Connecting Nanotechnology & Biotechnology")

with col2:
    st.markdown("### © Experts Group FZE")
    st.caption("Confidential / Proprietary")

st.divider()

# ============================================================
# TABS: ADMIN SETUP / LOGIN / SIGNUP
# ============================================================
admin_count = count_admin_users()

if admin_count == 0:
    tab_options = ["⚙️ Admin Setup", "🔐 Login", "👤 Sign Up"]
else:
    tab_options = ["🔐 Login", "👤 Sign Up"]

tabs = st.tabs(tab_options)

# ============================================================
# TAB 1: ADMIN SETUP (only if no admin exists)
# ============================================================
if admin_count == 0 and len(tabs) > 0:
    with tabs[0]:
        st.info("⚠️ **No admin account exists yet.** Please create one to get started.")
        
        with st.form("admin_setup_form"):
            st.markdown("### Create Admin Account")
            
            admin_username = st.text_input(
                "Admin Username",
                help="Username for the system administrator"
            )
            admin_email = st.text_input(
                "Admin Email (optional)",
                help="Email address for the admin account"
            )
            admin_password = st.text_input(
                "Admin Password",
                type="password",
                help="Must contain at least 6 characters, with letters and numbers"
            )
            admin_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                help="Re-enter your password"
            )
            
            if st.form_submit_button("Create Admin Account", use_container_width=True):
                if admin_password != admin_password_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    success, msg = setup_admin_account(admin_username, admin_password, admin_email)
                    if success:
                        st.success(f"✅ {msg}")
                        st.info("Admin account created! Please log in.")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
    
    login_tab = tabs[1]
    signup_tab = tabs[2] if len(tabs) > 2 else None
else:
    login_tab = tabs[0]
    signup_tab = tabs[1] if len(tabs) > 1 else None

# ============================================================
# LOGIN TAB
# ============================================================
with login_tab:
    st.markdown("### 🔐 Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username", help="Your username")
        password = st.text_input("Password", type="password", help="Your password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            st.form_submit_button("Clear", use_container_width=True)
        
        if login_button:
            if username and password:
                ok, role = authenticate(username, password)
                if ok:
                    # Import for session tracking
                    from datetime import datetime
                    import sqlite3
                    import time
                    
                    # Update login timestamp and session start in database
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn = sqlite3.connect("users.db", check_same_thread=False)
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE users SET session_start = ?, last_login = ?, last_activity = ? WHERE username = ?",
                        (now, now, now, username)
                    )
                    conn.commit()
                    conn.close()
                    
                    # Set session state
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.session_state.role = role
                    st.session_state.login_time = now
                    
                    st.success(f"✅ Welcome back, {username}!")
                    st.balloons()
                    time.sleep(1)
                    st.switch_page("pages/00_Disease_Selection.py")
                else:
                    st.error("❌ Invalid username or password.")
            else:
                st.warning("⚠️ Please enter both username and password")
    
    # Password recovery section
    st.markdown("---")
    st.markdown("#### 🔑 Forgot Your Password?")
    st.info("If you forgot your password, please contact your administrator to reset it. Provide them with your username.")
    
    with st.expander("📝 Password Recovery Options"):
        st.markdown("""
        **If you forgot your password:**
        1. **Contact Your Administrator** - Provide them with your username
        2. **Check Your Email** - Password reset instructions may have been sent
        3. **Account Recovery** - Contact your institution's IT support
        
        **Security Note:** For your protection, only administrators can reset passwords. This prevents unauthorized access to accounts.
        """)

# ============================================================
# SIGNUP TAB
# ============================================================
if signup_tab is not None:
    with signup_tab:
        st.markdown("### 👤 Create New Account")
        
        with st.form("signup_form"):
            st.markdown("Fill in the form below to create a new account")
            
            new_username = st.text_input(
                "Username",
                help="3-30 characters, letters, numbers, underscore, and hyphen only"
            )
            new_email = st.text_input(
                "Email (optional)",
                help="Valid email address for account recovery"
            )
            new_password = st.text_input(
                "Password",
                type="password",
                help="At least 6 characters with letters and numbers"
            )
            new_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                help="Re-enter your password"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                signup_button = st.form_submit_button("Create Account", use_container_width=True)
            with col2:
                st.form_submit_button("Clear", use_container_width=True)
            
            if signup_button:
                # Validate passwords match
                if new_password != new_password_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    # Register user
                    success, msg = register_user(new_username, new_password, new_email, role="student")
                    if success:
                        st.success(f"✅ {msg}")
                        st.info("Your account has been created! Please log in with your credentials.")
                    else:
                        st.error(f"❌ {msg}")
        
        st.markdown("---")
        st.markdown("### Requirements:")
        st.markdown("""
        - **Username:** 3-30 characters (letters, numbers, underscore, hyphen)
        - **Password:** At least 6 characters (must include letters and numbers)
        - **Email:** Optional but recommended for account recovery
        """)

# ============================================================
# DEMO CREDENTIALS
# ============================================================
st.markdown("---")
st.markdown("### 📝 Demo Credentials (for testing)")
with st.expander("View Demo Accounts"):
    st.markdown("""
    **Admin Account:**
    - Username: `admin`
    - Password: `admin123`
    
    **Scientist Account:**
    - Username: `scientist`
    - Password: `science123`
    
    **Viewer Account:**
    - Username: `viewer`
    - Password: `view123`
    """)
