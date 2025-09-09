#!/usr/bin/env python3
"""
Test script for the email system
Run with: python test_email.py
"""

import os
from dotenv import load_dotenv
from email_service import test_email_service

# Load environment variables
load_dotenv()

def main():
    print("🧪 Testing Dreamwell Email System (DEMO MODE)")
    print("=" * 60)
    
    # Check environment variables
    print("📋 Environment Check:")
    print(f"EMAIL_SERVICE: {os.getenv('EMAIL_SERVICE', 'NOT_SET')}")
    print(f"RESEND_API_KEY: {'SET' if os.getenv('RESEND_API_KEY') else 'NOT_SET'}")
    print(f"TO_EMAIL: {os.getenv('TO_EMAIL', 'NOT_SET')}")
    print(f"FROM_EMAIL: {os.getenv('FROM_EMAIL', 'NOT_SET')}")
    print()
    
    print("🎭 DEMO MODE ACTIVE:")
    print("- All emails will be sent to your test email address")
    print("- Intended recipients will be logged in console")
    print("- Email subjects will be prefixed with [DEMO]")
    print("- Perfect for demonstrations without spamming real influencers!")
    print()
    
    # Test email service
    print("📧 Testing Email Service:")
    test_email_service()
    
    print("\n✅ Email system test completed!")
    print("\n🎯 Demo Mode Features:")
    print("1. All emails redirected to your test email")
    print("2. Console logs show intended recipients")
    print("3. Email subjects clearly marked as [DEMO]")
    print("4. Perfect for live demonstrations!")
    print("\nTo use the email system:")
    print("1. Add your Resend API key to .env file")
    print("2. Set EMAIL_SERVICE=resend in .env")
    print("3. Configure TO_EMAIL and FROM_EMAIL in .env")
    print("4. Restart your Flask server")

if __name__ == "__main__":
    main()
