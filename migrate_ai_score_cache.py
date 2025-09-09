#!/usr/bin/env python3
"""
Migration script to create the ai_score_cache table for caching AI-generated influencer scores.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, AIScoreCache

def migrate_ai_score_cache():
    """Create the ai_score_cache table if it doesn't exist."""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ AIScoreCache table created successfully!")
            
            # Verify the table exists
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_score_cache'"))
            if result.fetchone():
                print("✅ AIScoreCache table verified in database")
            else:
                print("❌ AIScoreCache table not found in database")
                
        except Exception as e:
            print(f"❌ Error creating AIScoreCache table: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting AIScoreCache migration...")
    success = migrate_ai_score_cache()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)
