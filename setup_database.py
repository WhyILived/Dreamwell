#!/usr/bin/env python3
"""
Fresh database setup script for Dreamwell
This will create the database tables from scratch using SQLite
"""

from app import create_app, db
from models import User
import os

def setup_database():
    """Set up the database with fresh tables"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Setting up Dreamwell database...")
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"📊 Database URI: {db_uri}")
        
        try:
            # Drop all existing tables (if any)
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("🏗️  Creating fresh tables...")
            db.create_all()
            
            print("✅ Database setup completed successfully!")
            print("\n📋 Created tables:")
            print("   - users (companies)")
            
            # Optional: Create a test user
            test_user = User(
                email='test@dreamwell.com',
                password='TestPassword123',
                company_name='Test Company',
                website='https://testcompany.com'
            )
            db.session.add(test_user)
            db.session.commit()
            
            print("\n🧪 Created test user:")
            print("   Email: test@dreamwell.com")
            print("   Password: TestPassword123")
            print("   Company: Test Company")
            print("   Website: https://testcompany.com")
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Make sure you have write permissions in the project directory")
            print("   2. Check that no other process is using the database file")
            return False
    
    return True

if __name__ == '__main__':
    success = setup_database()
    if success:
        print("\n🎉 Ready to start the application!")
        print("   Run: python run.py")
    else:
        print("\n💡 Please fix the issues above and try again.")
