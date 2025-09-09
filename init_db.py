#!/usr/bin/env python3
"""
Database initialization script
Run this to create the database tables
"""

from app import create_app, db
from models import User

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Optional: Create a test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(
                email='test@example.com',
                password='TestPassword123',
                company_name='Test Company',
                website='https://testcompany.com'
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created: test@example.com / TestPassword123")
        else:
            print("ℹ️  Test user already exists")

if __name__ == '__main__':
    init_database()
