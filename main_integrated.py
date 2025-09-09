#!/usr/bin/env python3
"""
Integrated Main Script
- Scrapes company websites for keywords
- Finds YouTube influencers based on those keywords
- Saves results to database
- Connects with the Flask app database
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
from flask import Flask

def get_user_websites():
    """Get all user websites from the database"""
    app = create_app()
    
    with app.app_context():
        users = User.query.filter(User.website.isnot(None), User.website != '').all()
        return [(user.id, user.company_name, user.website) for user in users]

def save_influencer_results(user_id, keywords, influencers):
    """Save influencer results to database (you can extend this later)"""
    print(f"Found {len(influencers)} influencers for user {user_id}")
    print(f"Keywords used: {', '.join(keywords[:5])}...")  # Show first 5 keywords
    print(f"Top influencer: {influencers[0].get('title', 'Unknown') if influencers else 'None'}")
    
    # TODO: Create an Influencer model and save results
    # For now, just print the results
    return True

def process_user(user_id, company_name, website):
    """Process a single user's website and find influencers"""
    print(f"\n{'='*60}")
    print(f"Processing: {company_name}")
    print(f"Website: {website}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Scrape website for keywords
        print("Step 1: Scraping website for keywords...")
        keywords = scrape(website, top_n=10)  # Get top 10 keywords
        
        if not keywords:
            print("❌ No keywords found from website")
            return False
            
        print(f"✅ Found {len(keywords)} keywords: {', '.join(keywords[:5])}...")
        
        # Step 2: Search for influencers using those keywords
        print("\nStep 2: Searching for YouTube influencers...")
        keyword_string = ', '.join(keywords[:5])  # Use top 5 keywords for search
        influencers = search(keyword_string)
        
        if not influencers:
            print("❌ No influencers found")
            return False
            
        print(f"✅ Found {len(influencers)} influencers")
        
        # Step 3: Save results
        print("\nStep 3: Saving results...")
        save_influencer_results(user_id, keywords, influencers)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {company_name}: {str(e)}")
        return False

def main():
    """Main function to process all users"""
    print("🚀 Starting Influencer Search Process")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get all users with websites
    print("📊 Fetching users from database...")
    users = get_user_websites()
    
    if not users:
        print("❌ No users with websites found in database")
        print("💡 Make sure users have registered and added their website URLs")
        return
    
    print(f"✅ Found {len(users)} users with websites")
    
    # Process each user
    successful = 0
    failed = 0
    
    for user_id, company_name, website in users:
        if process_user(user_id, company_name, website):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 PROCESSING COMPLETE")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(users)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
