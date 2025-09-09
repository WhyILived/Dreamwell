#!/usr/bin/env python3
"""
Quick Database Check - Simple status check
"""

from app import create_app, db
from models import User

def quick_check():
    """Quick database status check"""
    print("🔍 Quick Database Check")
    print("-" * 30)
    
    try:
        app = create_app()
        with app.app_context():
            # Test connection using modern SQLAlchemy syntax
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Database connected")
            
            # Count users
            user_count = User.query.count()
            print(f"👥 Users: {user_count}")
            
            # Show recent users
            recent_users = User.query.order_by(User.created_at.desc()).limit(3).all()
            if recent_users:
                print("📋 Recent users:")
                for user in recent_users:
                    print(f"  • {user.email} ({user.company_name or 'No company'}) - Password: {user.password}")
            
            print("✅ Database is working!")
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    quick_check()
