#!/usr/bin/env python3
"""
Database Checker Script for Dreamwell
Checks SQLite database status, tables, and data
"""

import os
import sqlite3
from datetime import datetime
from app import create_app, db
from models import User

def check_database_file():
    """Check if database file exists and get its info"""
    db_path = "instance/dreamwell.db"
    
    print("🔍 Database File Check")
    print("=" * 50)
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        print(f"✅ Database file exists: {db_path}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"📅 Last modified: {file_modified}")
        return True
    else:
        print(f"❌ Database file not found: {db_path}")
        return False

def check_database_connection():
    """Test database connection"""
    print("\n🔌 Database Connection Check")
    print("=" * 50)
    
    try:
        app = create_app()
        with app.app_context():
            # Test basic connection using modern SQLAlchemy syntax
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Get database info
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT sqlite_version()")).fetchone()
                print(f"📊 SQLite version: {result[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables():
    """Check what tables exist in the database"""
    print("\n📋 Database Tables Check")
    print("=" * 50)
    
    try:
        app = create_app()
        with app.app_context():
            # Get list of tables using modern SQLAlchemy syntax
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)).fetchall()
            
            if result:
                print("✅ Tables found:")
                for table in result:
                    table_name = table[0]
                    # Get row count for each table
                    with db.engine.connect() as conn:
                        count_result = conn.execute(db.text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
                        row_count = count_result[0] if count_result else 0
                        print(f"  📊 {table_name}: {row_count:,} rows")
            else:
                print("❌ No tables found")
                return False
                
            return True
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def check_users_table():
    """Check the users table specifically"""
    print("\n👥 Users Table Check")
    print("=" * 50)
    
    try:
        app = create_app()
        with app.app_context():
            # Get table schema using modern SQLAlchemy syntax
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA table_info(users)")).fetchall()
            
            if result:
                print("✅ Users table schema:")
                for col in result:
                    col_id, name, data_type, not_null, default, pk = col
                    nullable = "NOT NULL" if not_null else "NULL"
                    primary = " (PRIMARY KEY)" if pk else ""
                    print(f"  📝 {name}: {data_type} {nullable}{primary}")
                
                # Get sample data
                users = User.query.limit(5).all()
                if users:
                    print(f"\n📊 Sample users ({len(users)} shown):")
                    for user in users:
                        print(f"  🆔 ID: {user.id}")
                        print(f"  📧 Email: {user.email}")
                        print(f"  🔑 Password: {user.password}")  # Show unhashed password for testing
                        print(f"  🏢 Company: {user.company_name or 'Not provided'}")
                        print(f"  🌐 Website: {user.website}")
                        print(f"  ✅ Active: {user.is_active}")
                        print(f"  📅 Created: {user.created_at}")
                        print()
                else:
                    print("❌ No users found in database")
                    
                return True
            else:
                print("❌ Users table not found")
                return False
                
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return False

def check_database_integrity():
    """Check database integrity"""
    print("\n🔧 Database Integrity Check")
    print("=" * 50)
    
    try:
        app = create_app()
        with app.app_context():
            # Run integrity check using modern SQLAlchemy syntax
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA integrity_check")).fetchone()
            
            if result and result[0] == "ok":
                print("✅ Database integrity check passed")
                return True
            else:
                print(f"❌ Database integrity check failed: {result[0] if result else 'Unknown error'}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking database integrity: {e}")
        return False

def get_database_stats():
    """Get comprehensive database statistics"""
    print("\n📈 Database Statistics")
    print("=" * 50)
    
    try:
        app = create_app()
        with app.app_context():
            # Get database size using modern SQLAlchemy syntax
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA page_count")).fetchone()
                page_count = result[0] if result else 0
                
                result = conn.execute(db.text("PRAGMA page_size")).fetchone()
                page_size = result[0] if result else 0
            
            db_size = page_count * page_size
            print(f"📊 Database size: {db_size:,} bytes ({db_size/1024:.1f} KB)")
            
            # Get user statistics
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            inactive_users = total_users - active_users
            
            print(f"👥 Total users: {total_users}")
            print(f"✅ Active users: {active_users}")
            print(f"❌ Inactive users: {inactive_users}")
            
            # Get recent activity
            recent_users = User.query.filter(
                User.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            print(f"📅 Users created today: {recent_users}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return False

def main():
    """Main function to run all database checks"""
    print("🔍 Dreamwell Database Checker")
    print("=" * 60)
    print(f"⏰ Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Database File", check_database_file),
        ("Database Connection", check_database_connection),
        ("Tables", check_tables),
        ("Users Table", check_users_table),
        ("Database Integrity", check_database_integrity),
        ("Database Statistics", get_database_stats)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n📋 Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All database checks passed! Your database is healthy.")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
