"""
Streamlit Authentication Module

Session management and auth UI for Streamlit pages.
Simplified version without complex JWT/RBAC dependencies.
"""

import streamlit as st
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StreamlitAuth:
    """Streamlit authentication utilities"""

    @staticmethod
    def init_session_state():
        """Initialize Streamlit session state"""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "username" not in st.session_state:
            st.session_state.username = None
        if "email" not in st.session_state:
            st.session_state.email = None
        if "roles" not in st.session_state:
            st.session_state.roles = []
        if "permissions" not in st.session_state:
            st.session_state.permissions = []
        if "token" not in st.session_state:
            st.session_state.token = None
        if "login_time" not in st.session_state:
            st.session_state.login_time = None

    @staticmethod
    def login(
        user_id: str,
        username: str,
        email: str,
        roles: list,
    ) -> str:
        """
        Login user and create session.

        Args:
            user_id: User ID
            username: Username
            email: Email address
            roles: User roles

        Returns:
            Session token (simplified)
        """
        # Create simple token
        token = f"token_{user_id}_{int(datetime.utcnow().timestamp())}"

        # Update session state
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.email = email
        st.session_state.roles = roles
        st.session_state.permissions = []
        st.session_state.token = token
        st.session_state.login_time = datetime.utcnow()

        logger.info(f"User logged in: {username}")
        return token

    @staticmethod
    def logout():
        """Logout user"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.email = None
        st.session_state.roles = []
        st.session_state.permissions = []
        st.session_state.token = None
        st.session_state.login_time = None

        logger.info("User logged out")

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        StreamlitAuth.init_session_state()
        return st.session_state.authenticated

    @staticmethod
    def get_current_user() -> Optional[dict]:
        """Get current user info"""
        StreamlitAuth.init_session_state()

        if not st.session_state.authenticated:
            return None

        return {
            "user_id": st.session_state.user_id,
            "username": st.session_state.username,
            "email": st.session_state.email,
            "roles": st.session_state.roles,
            "permissions": st.session_state.permissions,
        }

    @staticmethod
    def require_role(role: str) -> bool:
        """Check if current user has role"""
        user = StreamlitAuth.get_current_user()

        if not user:
            return False

        return role in user["roles"]


def require_login(page_name: str = "This page") -> bool:
    """
    Check if user is logged in via the main App.py authentication system.
    
    Usage:
        if not require_login("ML Training"):
            return
    """
    # Check if user is logged in via App.py session state
    if "logged_in" in st.session_state and st.session_state.logged_in and st.session_state.username:
        return True
    
    # Fallback to StreamlitAuth
    StreamlitAuth.init_session_state()
    if StreamlitAuth.is_authenticated():
        return True
    
    # Not logged in - show warning but don't call st.stop() to allow graceful fallback
    st.warning(f"🔒 {page_name} requires login")
    st.info("Please log in using the login area in the sidebar")
    return False


def require_permission(permission, page_name: str = "This feature") -> bool:
    """
    Check if user has required permission.
    
    Usage:
        if not require_permission(Permission.MODEL_TRAIN, "Model training"):
            return
    """
    # First check if user is logged in
    if not require_login(page_name):
        return False
    
    # For now, allow all permissions if user is logged in
    # TODO: Implement role-based permission checking
    return True


def show_user_info():
    """Display current user information"""
    user = StreamlitAuth.get_current_user()

    if user:
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**User:** {user['username']}")

        with col2:
            roles_str = ", ".join(user["roles"]) if user["roles"] else "None"
            st.write(f"**Roles:** {roles_str}")

        with col3:
            if st.button("Logout", key="logout_btn"):
                StreamlitAuth.logout()
                st.rerun()
