#!/usr/bin/env python3
"""
Secure administrator provisioning script for CodeNova Project Submission API.

Usage:
    python scripts/create_admin.py --username admin --password secret
Or via environment variables:
    ADMIN_USERNAME=admin ADMIN_PASSWORD=secret python scripts/create_admin.py
Or interactively:
    python scripts/create_admin.py
"""

import argparse
import getpass
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.admin import Admin
from app.core.security import hash_password


def parse_args():
    parser = argparse.ArgumentParser(description="Create a new administrator account.")
    parser.add_argument("--username", "-u", type=str, help="Administrator username")
    parser.add_argument("--password", "-p", type=str, help="Administrator password")
    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Resolve username
    username = args.username or os.environ.get("ADMIN_USERNAME")
    if not username:
        try:
            username = input("Enter admin username: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(1)

    username = username.strip()
    if not username or len(username) < 3:
        print("Error: Username must be at least 3 characters long.", file=sys.stderr)
        sys.exit(1)

    # 2. Resolve password
    password = args.password or os.environ.get("ADMIN_PASSWORD")
    if not password:
        try:
            password = getpass.getpass("Enter admin password: ")
            confirm = getpass.getpass("Confirm admin password: ")
            if password != confirm:
                print("Error: Passwords do not match.", file=sys.stderr)
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(1)

    if not password or len(password) < 6:
        print("Error: Password must be at least 6 characters long.", file=sys.stderr)
        sys.exit(1)

    # Initialize DB tables if they don't exist yet
    init_db()

    db = SessionLocal()
    try:
        # Check uniqueness
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"Error: Administrator with username '{username}' already exists.", file=sys.stderr)
            sys.exit(1)

        # Hash with Argon2 and store
        hashed = hash_password(password)
        new_admin = Admin(username=username, password_hash=hashed)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        print(f"Success: Administrator '{username}' (ID: {new_admin.id}) created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Database error during admin creation: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

