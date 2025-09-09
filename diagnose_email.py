#!/usr/bin/env python3
"""
Email System Diagnostic Tool
Run this to troubleshoot email delivery issues
"""

import os
from dotenv import load_dotenv
from email_service import EmailService

def main():
    print("🔍 Dreamwell Email System Diagnostic")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("📋 Environment Variables Check:")
    print(f"EMAIL_SERVICE: {os.getenv('EMAIL_SERVICE', 'NOT_SET')}")
    print(f"RESEND_API_KEY: {'SET' if os.getenv('RESEND_API_KEY') else 'NOT_SET'}")
    print(f"TO_EMAIL: {os.getenv('TO_EMAIL', 'NOT_SET')}")
    print(f"FROM_EMAIL: {os.getenv('FROM_EMAIL', 'NOT_SET')}")
    print()
    
    # Initialize email service
    service = EmailService()
    
    # Test 1: Basic configuration
    print("🧪 Test 1: Basic Configuration")
    print(f"✅ Service Type: {service.email_service}")
    print(f"✅ API Key Present: {'Yes' if service.resend_api_key else 'No'}")
    print(f"✅ To Email: {service.to_email}")
    print(f"✅ From Email: {service.from_email}")
    print()
    
    # Test 2: Resend API verification
    print("🧪 Test 2: Resend API Verification")
    is_valid, message = service.verify_resend_setup()
    print(f"Result: {'✅ PASS' if is_valid else '❌ FAIL'}")
    print(f"Details: {message}")
    print()
    
    # Test 3: Send test email
    print("🧪 Test 3: Send Test Email")
    print("Sending test email...")
    
    success, result_message = service.send_sponsor_outreach(
        influencer_name="Test User",
        influencer_email="test@example.com",
        company_name="Dreamwell Test",
        product_name="Test Product",
        custom_message="This is a test email to verify delivery.",
        suggested_pricing="$100 - $200",
        expected_profit="$500 - $1000"
    )
    
    print(f"Email Send Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Message: {result_message}")
    print()
    
    # Test 4: Troubleshooting tips
    print("🔧 Troubleshooting Tips:")
    print("1. Check your spam/junk folder")
    print("2. Verify the FROM_EMAIL domain is verified in Resend")
    print("3. Check Resend dashboard for delivery status")
    print("4. Ensure TO_EMAIL is correct and accessible")
    print("5. Check if your email provider blocks automated emails")
    print()
    
    # Test 5: Resend dashboard info
    print("📊 Resend Dashboard Information:")
    print("- Log into your Resend dashboard")
    print("- Check the 'Emails' section for delivery status")
    print("- Look for any error messages or bounces")
    print("- Verify your domain is properly configured")
    print()
    
    print("✅ Diagnostic complete!")
    print("If emails still don't arrive, check the Resend dashboard for detailed logs.")

if __name__ == "__main__":
    main()
