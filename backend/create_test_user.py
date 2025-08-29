#!/usr/bin/env python3
"""Script to create a test user for testing document conversion"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.api.deps import get_db
from app.models import UserCreate
from app.crud import create_user
from app.core.security import get_password_hash

def create_test_user():
    """Create a test user for testing"""
    try:
        db = next(get_db())
        
        # Check if test user already exists
        from app.models import User
        from sqlmodel import select
        
        existing_user = db.exec(select(User).where(User.email == "test@example.com")).first()
        
        if existing_user:
            print("✅ Test user already exists:")
            print(f"  Email: {existing_user.email}")
            print(f"  ID: {existing_user.id}")
            print(f"  Is active: {existing_user.is_active}")
            return existing_user
        
        # Create new test user
        test_user_data = UserCreate(
            email="test@example.com",
            password="test123",
            full_name="Test User"
        )
        
        test_user = create_user(db, test_user_data)
        
        print("✅ Test user created successfully:")
        print(f"  Email: {test_user.email}")
        print(f"  Password: test123")
        print(f"  ID: {test_user.id}")
        print(f"  Is active: {test_user.is_active}")
        
        return test_user
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_test_user()
