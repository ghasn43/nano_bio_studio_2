"""
Authentication module for NanoBio Studio
Handles user login, signup, and role management
"""

import json
import hashlib
import os
import secrets
from pathlib import Path
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, users_file="users.json", sessions_file="sessions.json"):
        self.users_file = users_file
        self.sessions_file = sessions_file
        self.initialize_users_file()
        self.clean_expired_sessions()
    
    def initialize_users_file(self):
        """Initialize users file with default admin account"""
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "email": "admin@nanobio.com",
                    "full_name": "Administrator"
                }
            }
            self.save_users(default_users)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=4)
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        users = self.load_users()
        if username in users:
            hashed_password = self.hash_password(password)
            if users[username]["password"] == hashed_password:
                return {
                    "username": username,
                    "role": users[username]["role"],
                    "email": users[username]["email"],
                    "full_name": users[username]["full_name"]
                }
        return None
    
    def create_session(self, username):
        """Create a persistent session for user"""
        sessions = self.load_sessions()
        session_token = secrets.token_urlsafe(32)
        
        sessions[session_token] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        
        self.save_sessions(sessions)
        return session_token
    
    def validate_session(self, session_token):
        """Validate session token and return user info"""
        sessions = self.load_sessions()
        
        if session_token in sessions:
            session = sessions[session_token]
            expires_at = datetime.fromisoformat(session["expires_at"])
            
            if datetime.now() < expires_at:
                # Session is valid, extend expiration
                session["expires_at"] = (datetime.now() + timedelta(minutes=30)).isoformat()
                self.save_sessions(sessions)
                
                # Get user info
                users = self.load_users()
                username = session["username"]
                if username in users:
                    return {
                        "username": username,
                        "role": users[username]["role"],
                        "email": users[username]["email"],
                        "full_name": users[username]["full_name"]
                    }
            else:
                # Session expired, remove it
                del sessions[session_token]
                self.save_sessions(sessions)
        
        return None
    
    def delete_session(self, session_token):
        """Delete a session (logout)"""
        sessions = self.load_sessions()
        if session_token in sessions:
            del sessions[session_token]
            self.save_sessions(sessions)
    
    def load_sessions(self):
        """Load sessions from JSON file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_sessions(self, sessions):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=4)
    
    def clean_expired_sessions(self):
        """Remove expired sessions"""
        sessions = self.load_sessions()
        current_time = datetime.now()
        
        expired_tokens = []
        for token, session in sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if current_time >= expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del sessions[token]
        
        if expired_tokens:
            self.save_sessions(sessions)
    
    def register_user(self, username, password, email, full_name, role="user"):
        """Register a new user"""
        users = self.load_users()
        
        # Check if username already exists
        if username in users:
            return False, "Username already exists"
        
        # Add new user
        users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "email": email,
            "full_name": full_name
        }
        
        self.save_users(users)
        return True, "User registered successfully"
    
    def get_all_users(self):
        """Get all users (admin only)"""
        users = self.load_users()
        user_list = []
        for username, data in users.items():
            user_list.append({
                "username": username,
                "role": data["role"],
                "email": data["email"],
                "full_name": data["full_name"]
            })
        return user_list
    
    def delete_user(self, username):
        """Delete a user (admin only)"""
        if username == "admin":
            return False, "Cannot delete admin account"
        
        users = self.load_users()
        if username in users:
            del users[username]
            self.save_users(users)
            return True, "User deleted successfully"
        return False, "User not found"
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        users = self.load_users()
        if username in users:
            if users[username]["password"] == self.hash_password(old_password):
                users[username]["password"] = self.hash_password(new_password)
                self.save_users(users)
                return True, "Password changed successfully"
            return False, "Incorrect old password"
        return False, "User not found"
    
    def admin_reset_password(self, username, new_password):
        """Admin reset user password (admin only)"""
        users = self.load_users()
        if username in users:
            users[username]["password"] = self.hash_password(new_password)
            self.save_users(users)
            return True, "Password reset successfully"
        return False, "User not found"
    
    def update_username(self, old_username, new_username):
        """Update username (admin only)"""
        if old_username == "admin":
            return False, "Cannot change admin username"
        
        users = self.load_users()
        
        if old_username not in users:
            return False, "User not found"
        
        if new_username in users:
            return False, "New username already exists"
        
        # Copy user data to new username
        users[new_username] = users[old_username]
        # Delete old username
        del users[old_username]
        self.save_users(users)
        return True, "Username updated successfully"
    
    def update_user_role(self, username, new_role):
        """Update user role (admin only)"""
        if username == "admin":
            return False, "Cannot change admin role"
        
        users = self.load_users()
        if username in users:
            users[username]["role"] = new_role
            self.save_users(users)
            return True, "Role updated successfully"
        return False, "User not found"
    
    def update_user_info(self, username, email=None, full_name=None):
        """Update user information (admin only)"""
        users = self.load_users()
        if username in users:
            if email:
                users[username]["email"] = email
            if full_name:
                users[username]["full_name"] = full_name
            self.save_users(users)
            return True, "User information updated successfully"
        return False, "User not found"
    
    def get_user_details(self, username):
        """Get detailed user information"""
        users = self.load_users()
        if username in users:
            return {
                "username": username,
                "role": users[username]["role"],
                "email": users[username]["email"],
                "full_name": users[username]["full_name"]
            }
        return None
