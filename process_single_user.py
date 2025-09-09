#!/usr/bin/env python3
"""
Process a single user's website for influencer search
Usage: python process_single_user.py <user_id>
"""

import os
import sys
from dotenv import load_dotenv
from extract import search
from scraper import scrape

# Add the current directory to Python path to import Flask app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User

def process_single_user(user_id):
    """Process a single user by ID"""
    app = create_app()
    
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return False
            
        if not user.website:
            print(f"❌ User {user.company_name or user.email} has no website")
            return False
            
        print(f"👤 Processing User: {user.company_name or user.email}")
        print(f"🌐 Website: {user.website}")
        print(f"🏷️  Current Keywords: {user.keywords or 'None'}")
        
        try:
            # Step 1: Scrape website for keywords
            print("\n📝 Step 1: Scraping website for keywords...")
            keywords = scrape(user.website, top_n=10)
            
            if not keywords:
                print("❌ No keywords found from website")
                return False
                
            print(f"✅ Found {len(keywords)} keywords: {', '.join(keywords[:5])}...")
            
            # Step 2: Update user's keywords in database
            print("\n💾 Step 2: Updating user keywords in database...")
            user.keywords = ', '.join(keywords)
            db.session.commit()
            print("✅ Keywords saved to database")
            
            # Step 3: Search for influencers
            print("\n🔍 Step 3: Searching for YouTube influencers...")
            keyword_string = ', '.join(keywords[:5])  # Use top 5 keywords
            influencers = search(keyword_string)
            
            if not influencers:
                print("❌ No influencers found")
                return False
                
            print(f"✅ Found {len(influencers)} influencers")
            print("\n📊 Top 3 Influencers:")
            for i, inf in enumerate(influencers[:3], 1):
                print(f"  {i}. {inf.get('title', 'Unknown')} - {inf.get('subs', 'N/A')} subs")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing user: {str(e)}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python process_single_user.py <user_id>")
        print("Example: python process_single_user.py 1")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("❌ User ID must be a number")
        sys.exit(1)
    
    print("🚀 Starting Single User Processing")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    success = process_single_user(user_id)
    
    if success:
        print("\n✅ Processing completed successfully!")
    else:
        print("\n❌ Processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
