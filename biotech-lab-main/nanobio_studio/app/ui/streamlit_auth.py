"""
Streamlit Integration Utilities

Session management, auth UI, and helper functions for Streamlit pages.
"""

import streamlit as st
import logging
from typing import Optional, Callable
from datetime import datetime
from nanobio_studio.app.auth import JWTHandler, Role, Permission, RBACManager
from nanobio_studio.app.config import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()

# JWT Handler instance
jwt_handler = JWTHandler(
    secret_key="your-secret-key-change-in-production",
    algorithm="HS256",
    expiration_hours=24,
)


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
        roles: list[str],
    ) -> str:
        """
        Login user and create token.

        Args:
            user_id: User ID
            username: Username
            email: Email address
            roles: User roles

        Returns:
            JWT token
        """
        # Convert role strings to Role enum
        role_enums = [Role(r) for r in roles]

        # Get permissions for roles
        permissions = RBACManager.get_permissions_for_roles(role_enums)

        # Create token
        token = jwt_handler.create_token(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=[p.value for p in permissions],
        )

        # Update session state
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.email = email
        st.session_state.roles = role_enums
        st.session_state.permissions = list(permissions)
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
    def require_permission(permission: Permission) -> bool:
        """Check if current user has permission"""
        user = StreamlitAuth.get_current_user()

        if not user:
            return False

        for perm in user["permissions"]:
            if perm == permission:
                return True

        return False

    @staticmethod
    def require_role(role: Role) -> bool:
        """Check if current user has role"""
        user = StreamlitAuth.get_current_user()

        if not user:
            return False

        return role in user["roles"]


def require_login(page_name: str = "This page"):
    """
    Check if user is logged in via the main App.py authentication system.
    Works with the old auth.py, not StreamlitAuth JWT system.
    
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


def require_permission(permission: Permission, page_name: str = "This feature"):
    """
    Check if user has required permission.
    
    Usage:
        if not require_permission(Permission.MODEL_TRAIN, "Model training"):
            return
    """
    # First check if user is logged in
    if not require_login("This feature"):
        return False
    
    # For now, allow all permissions if user is logged in
    # TODO: Implement role-based permission checking
    # This can be extended later to check actual user roles/permissions from the database
    
    return True


def require_role(role: Role, page_name: str = "This page"):
    """
    Decorator/check to require specific role.

    Usage:
        if not require_role(Role.ADMIN):
            st.stop()
    """
    if not StreamlitAuth.is_authenticated():
        st.warning("🔒 Please log in first")
        st.stop()
        return False

    if not StreamlitAuth.require_role(role):
        st.error(f"❌ {page_name} requires role: {role.value}")
        st.stop()
        return False

    return True


def show_user_info():
    """Display current user information"""
    user = StreamlitAuth.get_current_user()

    if user:
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**User:** {user['username']}")

        with col2:
            roles_str = ", ".join([r.value for r in user["roles"]])
            st.write(f"**Roles:** {roles_str}")

        with col3:
            if st.button("Logout", key="logout_btn"):
                StreamlitAuth.logout()
                st.rerun()


def show_permissions_matrix():
    """Display user permissions matrix"""
    user = StreamlitAuth.get_current_user()

    if not user:
        return

    st.subheader("Your Permissions")

    permissions_dict = {
        "Datasets": [Permission.DATASET_READ, Permission.DATASET_CREATE, Permission.DATASET_DELETE],
        "Models": [Permission.MODEL_READ, Permission.MODEL_TRAIN, Permission.MODEL_DELETE, Permission.MODEL_EXPORT],
        "Predictions": [Permission.PREDICT_READ, Permission.PREDICT_CREATE],
        "Rankings": [Permission.RANK_READ, Permission.RANK_CREATE],
    }

    for category, perms in permissions_dict.items():
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**{category}**")

        for perm in perms:
            has_perm = perm in user["permissions"]
            status = "✅" if has_perm else "❌"
            with col2:
                st.write(f"{status} {perm.value}")
