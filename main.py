#!/usr/bin/env python3
"""
Main Script - Integrated with Database
- Scrapes a website for keywords
- Finds YouTube influencers based on those keywords
- Can be used standalone or with database integration
"""

import os
import sys
from dotenv import load_dotenv
from extract import search
from scraper import scrape

def main():
    """Main function for standalone keyword scraping and influencer search"""
    print("🚀 Starting Keyword Scraping and Influencer Search")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Default website (you can change this)
    website = "https://www.dreamwell.ai"
    
    try:
        # Step 1: Scrape website for keywords
        print(f"📝 Step 1: Scraping website: {website}")
        keywords = scrape(website, top_n=10)
        
        if not keywords:
            print("❌ No keywords found from website")
            return
            
        print(f"✅ Found {len(keywords)} keywords: {', '.join(keywords[:5])}...")
        
        # Step 2: Search for influencers using those keywords
        print(f"\n🔍 Step 2: Searching for YouTube influencers...")
        keyword_string = ', '.join(keywords[:5])  # Use top 5 keywords
        influencers = search(keyword_string)
        
        if not influencers:
            print("❌ No influencers found")
            return
            
        print(f"✅ Found {len(influencers)} influencers")
        print("\n📊 Top 5 Influencers:")
        for i, inf in enumerate(influencers[:5], 1):
            print(f"  {i}. {inf.get('title', 'Unknown')} - {inf.get('subs', 'N/A')} subs")
        
        print(f"\n💾 Results saved to: influencers.csv")
        print("✅ Processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

if __name__ == "__main__":
    main()