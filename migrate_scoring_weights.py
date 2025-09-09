#!/usr/bin/env python3
"""
Migration script to add ScoringWeights table
Run this after updating the models.py file
"""

from app import create_app
from models import db, ScoringWeights

def migrate():
    """Add the ScoringWeights table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the new table
            db.create_all()
            print("✅ ScoringWeights table created successfully")
            
            # Verify the table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'scoring_weights' in tables:
                print("✅ Table 'scoring_weights' verified in database")
            else:
                print("❌ Table 'scoring_weights' not found")
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return False
            
    return True

if __name__ == "__main__":
    print("🔄 Running migration for ScoringWeights table...")
    success = migrate()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
