#!/usr/bin/env python
"""
Interactive Password Reset Tool
"""

from auth import reset_password, get_all_users
from getpass import getpass

print("\n" + "=" * 60)
print("NanoBio Studio - Password Recovery/Reset")
print("=" * 60 + "\n")

# Show available users
all_users = get_all_users()
print("Available Users:")
for i, (username, role) in enumerate(all_users, 1):
    print(f"  {i}. {username} ({role})")

print("\n" + "-" * 60)

# Get username to reset
username = input("\nEnter username to reset password for: ").strip()

# Verify user exists
if not any(u[0] == username for u in all_users):
    print(f"❌ Error: User '{username}' not found!")
    exit(1)

# Get new password
print("\nPassword Requirements:")
print("  • Minimum 6 characters")
print("  • Must contain at least 1 letter and 1 number")
print("  • Allowed: A-Z, a-z, 0-9, @$!%*#?&")

new_password = getpass("\nEnter new password: ")
confirm_password = getpass("Confirm new password: ")

if new_password != confirm_password:
    print("❌ Passwords do not match!")
    exit(1)

# Reset password
success, message = reset_password(username, new_password)

print("\n" + "-" * 60)
if success:
    print(f"✅ SUCCESS: {message}")
else:
    print(f"❌ FAILED: {message}")

print("=" * 60 + "\n")
