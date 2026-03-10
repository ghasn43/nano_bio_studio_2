#!/usr/bin/env python
"""
Account Recovery Tool - Recover Username and Reset Password
"""

from auth import get_all_users, list_users_detailed, reset_password, get_user_info
import sqlite3

print("=" * 60)
print("NanoBio Studio - Account Recovery Tool")
print("=" * 60)

# Step 1: Show all users
print("\n[STEP 1] RECOVER USERNAMES")
print("-" * 60)
all_users = get_all_users()
print(f"\nFound {len(all_users)} user(s):\n")
for i, (username, role) in enumerate(all_users, 1):
    print(f"  {i}. Username: '{username}' (Role: {role})")

# Step 2: Show detailed user info
print("\n[STEP 2] USER DETAILS")
print("-" * 60)
detailed_users = list_users_detailed()
for user in detailed_users:
    print(f"\n  Username: {user['username']}")
    print(f"  Email:    {user['email']}")
    print(f"  Role:     {user['role']}")
    print(f"  Status:   {user['status']}")
    print(f"  Created:  {user['created_at']}")
    print(f"  Last Login: {user['last_login']}")

# Step 3: Password Recovery
print("\n[STEP 3] PASSWORD RECOVERY/RESET")
print("-" * 60)
print("\nTo reset a password, use one of these methods:\n")

print("METHOD 1 - Interactive Reset (Recommended):")
print("  python reset_password.py\n")

print("METHOD 2 - Python Command:")
print("  python -c \"from auth import reset_password; print(reset_password('admin', 'new_password'))\"\n")

print("METHOD 3 - Create a reset script:")
print("  See: recover_password_interactive.py\n")

# Step 4: If you know which account to reset
print("[STEP 4] EXAMPLE PASSWORD RESET")
print("-" * 60)
print("\nExample for 'admin' user:")
username_to_reset = "admin"
print(f"  from auth import reset_password")
print(f"  success, message = reset_password('{username_to_reset}', 'YourNewPassword123')")
print(f"  print(message)")

print("\n" + "=" * 60)
print("✓ Your usernames are shown above!")
print("✓ To reset password, see METHOD 1, 2, or 3")
print("=" * 60)
