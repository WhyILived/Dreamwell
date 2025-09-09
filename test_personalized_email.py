#!/usr/bin/env python3
"""
Test personalized email generation
"""

import os
from dotenv import load_dotenv
from email_service import EmailService

def test_personalized_email():
    load_dotenv()
    
    service = EmailService()
    
    # Sample influencer data (like what would come from the frontend)
    influencer_data = {
        'title': 'Tech Reviewer Pro',
        'subs': 150000,
        'avg_recent_views': 25000,
        'country': 'United States',
        'about_description': 'I review the latest tech gadgets and provide honest, detailed reviews for tech enthusiasts.',
        'recent_videos': [
            {'title': 'iPhone 15 Pro Max Review - Worth the Upgrade?'},
            {'title': 'Best Gaming Laptops 2024 - Complete Buyer\'s Guide'},
            {'title': 'Samsung Galaxy S24 Ultra Camera Test'}
        ],
        'engagement_rate': 0.08,
        'score': 87.5
    }
    
    print("🤖 Testing Personalized Email Generation")
    print("=" * 50)
    
    # Generate personalized content
    personalized_content = service._generate_personalized_email_content(
        influencer_name="Tech Reviewer Pro",
        influencer_email="tech@example.com",
        company_name="Dreamwell Tech",
        product_name="Smart Fitness Tracker",
        custom_message="We'd love to work with you on our new fitness tracker!",
        suggested_pricing="$800 - $1200",
        expected_profit="$3000 - $5000",
        influencer_data=influencer_data
    )
    
    print("📧 Generated Personalized Content:")
    print("-" * 30)
    print(f"Subject: {personalized_content.get('subject', 'N/A')}")
    print(f"Personalized Message: {personalized_content.get('personalized_message', 'N/A')}")
    print(f"Collaboration Details: {personalized_content.get('collaboration_details', 'N/A')}")
    print(f"Information Request: {personalized_content.get('information_request', 'N/A')}")
    print(f"Call to Action: {personalized_content.get('call_to_action', 'N/A')}")
    print("-" * 30)
    
    # Test sending the personalized email
    print("\n📤 Testing Personalized Email Send...")
    success, message = service.send_sponsor_outreach(
        influencer_name="Tech Reviewer Pro",
        influencer_email="tech@example.com",
        company_name="Dreamwell Tech",
        product_name="Smart Fitness Tracker",
        custom_message="We'd love to work with you on our new fitness tracker!",
        suggested_pricing="$800 - $1200",
        expected_profit="$3000 - $5000",
        influencer_data=influencer_data
    )
    
    print(f"Email Send Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Message: {message}")

if __name__ == "__main__":
    test_personalized_email()
