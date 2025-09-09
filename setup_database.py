#!/usr/bin/env python3
"""
Dreamwell database setup/upgrade script

Usage:
  - Fresh setup (drop and recreate all tables, seed test user):
      python setup_database.py --fresh

  - Incremental update (create any new tables/columns as defined in models):
      python setup_database.py
"""

from app import create_app, db
from models import User
import argparse
import os

def setup_database(fresh: bool = False) -> bool:
    """Set up or update the database schema.

    When fresh=True, drops all tables and recreates them, then seeds a test user.
    When fresh=False, performs a non-destructive update by creating any missing tables.
    """
    app = create_app()
    
    with app.app_context():
        print("🚀 Setting up Dreamwell database...")
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"📊 Database URI: {db_uri}")
        
        try:
            if fresh:
                # Drop all existing tables (if any)
                print("🗑️  Dropping existing tables...")
                db.drop_all()
                print("🏗️  Creating fresh tables...")
                db.create_all()
            else:
                # Non-destructive: create any new tables
                print("🔄 Applying non-destructive schema updates (create missing tables)...")
                db.create_all()
            
            print("✅ Database setup completed successfully!")
            print("\n📋 Created tables:")
            print("   - users (companies)")
            print("   - youtube_search_cache (YouTube API caching)")
            
            if fresh:
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
    parser = argparse.ArgumentParser(description='Dreamwell DB setup/upgrade')
    parser.add_argument('--fresh', action='store_true', help='Drop and recreate all tables (DANGEROUS)')
    args = parser.parse_args()

    success = setup_database(fresh=args.fresh)
    if success:
        print("\n🎉 Ready to start the application!")
        print("   Run: python run.py")
    else:
        print("\n💡 Please fix the issues above and try again.")
