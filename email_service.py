#!/usr/bin/env python3
"""
Email Service Module
Handles email sending for sponsor outreach and notifications
"""

import os
import smtplib
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    """Email service for sending sponsor outreach emails"""
    
    def __init__(self):
        """Initialize email service configuration"""
        self.email_service = os.getenv('EMAIL_SERVICE', 'resend')
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        self.to_email = os.getenv('TO_EMAIL', 'shadhin.mushfiqur@gmail.com')
        self.from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
        
        # Initialize Gemini for personalized content generation
        self._init_gemini()
        
        print(f"📧 Email service initialized: {self.email_service}")
    
    def _init_gemini(self):
        """Initialize Gemini API client for personalized content generation"""
        try:
            import google.generativeai as genai
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini API initialized for email personalization")
            else:
                print("⚠️  GEMINI_API_KEY not found - using fallback content")
                self.gemini_model = None
        except ImportError:
            print("⚠️  google-generativeai not installed - using fallback content")
            self.gemini_model = None
        except Exception as e:
            print(f"⚠️  Error initializing Gemini: {e} - using fallback content")
            self.gemini_model = None
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return bool(re.match(email_regex, email))
    
    def send_sponsor_outreach(self, 
                            influencer_name: str, 
                            influencer_email: str, 
                            company_name: str, 
                            product_name: str,
                            custom_message: str = "",
                            suggested_pricing: str = "",
                            expected_profit: str = "",
                            influencer_data: dict = None) -> Tuple[bool, str]:
        """
        Send sponsor outreach email to influencer
        
        Args:
            influencer_name: Name of the influencer
            influencer_email: Email of the influencer
            company_name: Name of the company
            product_name: Name of the product
            custom_message: Custom message from company
            suggested_pricing: Suggested pricing range
            expected_profit: Expected profit range
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate email
            if not self.validate_email(influencer_email):
                return False, "Invalid email format"
            
            # DEMO MODE: Log intended recipient and send to test email instead
            print("🎭 DEMO MODE: Email redirection active")
            print(f"📧 Intended recipient: {influencer_name} <{influencer_email}>")
            print(f"📤 Actually sending to: {self.to_email}")
            print("=" * 60)
            
            # Generate personalized email content using AI
            print("🤖 Generating personalized email content...")
            personalized_content = self._generate_personalized_email_content(
                influencer_name, influencer_email, company_name, product_name,
                custom_message, suggested_pricing, expected_profit, influencer_data
            )
            
            # Create email content with demo notice
            subject = f"[DEMO] {personalized_content.get('subject', f'Partnership Opportunity - {product_name}')} (for {influencer_name})"
            html_content = self._create_sponsor_email_html(
                influencer_name, company_name, product_name, 
                custom_message, suggested_pricing, expected_profit, 
                demo_mode=True, personalized_content=personalized_content
            )
            
            # Send email based on configured service (always to test email)
            if self.email_service == 'resend' and self.resend_api_key:
                return self._send_with_resend(self.to_email, subject, html_content)
            else:
                return self._log_to_console(influencer_name, influencer_email, subject, html_content)
                
        except Exception as e:
            print(f"❌ Error sending sponsor outreach email: {e}")
            return False, f"Failed to send email: {str(e)}"
    
    def send_notification_email(self, 
                              subject: str, 
                              message: str, 
                              influencer_count: int = 0) -> Tuple[bool, str]:
        """
        Send notification email to company about search results
        
        Args:
            subject: Email subject
            message: Email message
            influencer_count: Number of influencers found
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            html_content = self._create_notification_email_html(subject, message, influencer_count)
            
            if self.email_service == 'resend' and self.resend_api_key:
                return self._send_with_resend(self.to_email, subject, html_content)
            else:
                return self._log_to_console("Company", self.to_email, subject, html_content)
                
        except Exception as e:
            print(f"❌ Error sending notification email: {e}")
            return False, f"Failed to send email: {str(e)}"
    
    def _generate_personalized_email_content(self, 
                                           influencer_name: str,
                                           influencer_email: str,
                                           company_name: str,
                                           product_name: str,
                                           custom_message: str,
                                           suggested_pricing: str,
                                           expected_profit: str,
                                           influencer_data: dict = None) -> dict:
        """Generate personalized email content using AI"""
        try:
            if not self.gemini_model:
                # Fallback to basic content if Gemini not available
                return {
                    "subject": f"Partnership Inquiry - {product_name}",
                    "personalized_message": custom_message or f"Hi {influencer_name}, we'd like to discuss a potential collaboration on our {product_name}.",
                    "collaboration_details": f"We're interested in collaborating with you on our {product_name} and would like to understand your preferences.",
                    "information_request": f"We'd appreciate learning about your collaboration preferences and availability for this type of partnership.",
                    "call_to_action": "Please let us know if you're interested in discussing this opportunity further."
                }
            
            # Prepare influencer context
            influencer_context = ""
            if influencer_data:
                influencer_context = f"""
                Influencer Details:
                - Channel: {influencer_data.get('title', 'Unknown')}
                - Subscribers: {influencer_data.get('subs', 'Unknown')}
                - Average Views: {influencer_data.get('avg_recent_views', 'Unknown')}
                - Country: {influencer_data.get('country', 'Unknown')}
                - Channel Description: {influencer_data.get('about_description', 'No description available')}
                - Recent Content: {influencer_data.get('recent_videos', [])[:3] if influencer_data.get('recent_videos') else 'No recent videos available'}
                - Engagement Rate: {influencer_data.get('engagement_rate', 'Unknown')}
                - Score: {influencer_data.get('score', 'Unknown')}
                """
            
            # Extract lower bound pricing for initial offer
            initial_offer = "To be discussed"
            if suggested_pricing and "-" in suggested_pricing:
                try:
                    lower_bound = suggested_pricing.split("-")[0].strip()
                    initial_offer = lower_bound
                except:
                    initial_offer = suggested_pricing
            elif suggested_pricing:
                initial_offer = suggested_pricing

            prompt = f"""
            You are a professional business development manager writing a partnership inquiry email. Create a professional, informative email that seeks to understand the influencer's collaboration preferences and availability.

            Company: {company_name}
            Product: {product_name}
            Influencer: {influencer_name} ({influencer_email})
            Custom Prompt: {custom_message or 'No specific prompt provided'}
            Initial Offer: {initial_offer}

            {influencer_context}

            Create a professional email with:
            1. A clear, professional subject line (max 60 characters)
            2. A brief, personalized introduction that shows you're familiar with their work
            3. A clear explanation of the collaboration opportunity
            4. Questions to understand their preferences and availability
            5. Professional tone throughout
            6. Clear next steps for discussion

            IMPORTANT: You must respond with ONLY valid JSON in this exact format:
            {{
                "subject": "Professional subject line",
                "personalized_message": "Main email content with professional tone",
                "collaboration_details": "Clear explanation of the opportunity and what we're looking for",
                "information_request": "Questions to understand their preferences and availability",
                "call_to_action": "Professional closing with next steps"
            }}

            Keep it professional, concise, and focused on gathering information about their collaboration preferences. Avoid being overly salesy or pushy. Do not include any text outside the JSON structure. Do NOT mention revenue projections, expected profit, financial impact, or any internal business metrics - only discuss the collaboration opportunity and compensation offer.
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text.strip()
            
            # Parse JSON response
            import json
            try:
                # Extract JSON from response - look for ```json blocks first
                if '```json' in content:
                    start = content.find('```json') + 7
                    end = content.find('```', start)
                    if end > start:
                        json_content = content[start:end].strip()
                    else:
                        # Fallback to regular JSON extraction
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        json_content = content[start:end] if start != -1 and end > start else content
                else:
                    # Regular JSON extraction
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_content = content[start:end] if start != -1 and end > start else content
                
                if json_content:
                    parsed = json.loads(json_content)
                    print(f"✅ Successfully parsed AI response with {len(parsed)} fields")
                    return parsed
            except Exception as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw content: {content[:200]}...")
                pass
            
            # Fallback if JSON parsing fails
            return {
                "subject": f"Partnership Inquiry - {product_name}",
                "personalized_message": content[:500] + "..." if len(content) > 500 else content,
                "collaboration_details": f"We're interested in collaborating with you on our {product_name}.",
                "information_request": f"We'd like to understand your collaboration preferences and availability.",
                "call_to_action": "Please let us know if you're interested in discussing this opportunity."
            }
            
        except Exception as e:
            print(f"Error generating personalized content: {e}")
            # Fallback to basic content
            return {
                "subject": f"Partnership Inquiry - {product_name}",
                "personalized_message": custom_message or f"Hi {influencer_name}, we'd like to discuss a potential collaboration on our {product_name}.",
                "collaboration_details": f"We're interested in collaborating with you on our {product_name} and would like to understand your preferences.",
                "information_request": f"We'd appreciate learning about your collaboration preferences and availability for this type of partnership.",
                "call_to_action": "Please let us know if you're interested in discussing this opportunity further."
            }

    def _create_sponsor_email_html(self, 
                                 influencer_name: str, 
                                 company_name: str, 
                                 product_name: str,
                                 custom_message: str,
                                 suggested_pricing: str,
                                 expected_profit: str,
                                 demo_mode: bool = False,
                                 personalized_content: dict = None) -> str:
        """Create HTML content for sponsor outreach email"""
        
        # Use personalized content if available, otherwise fallback to basic content
        if personalized_content:
            subject = personalized_content.get('subject', f"Partnership Inquiry - {product_name}")
            personalized_message = personalized_content.get('personalized_message', custom_message or f"Hi {influencer_name}, we'd like to discuss a potential collaboration.")
            collaboration_details = personalized_content.get('collaboration_details', f"We're interested in collaborating with you on our {product_name}.")
            information_request = personalized_content.get('information_request', f"We'd like to understand your collaboration preferences and availability.")
            call_to_action = personalized_content.get('call_to_action', "Please let us know if you're interested in discussing this opportunity.")
        else:
            subject = f"Partnership Inquiry - {product_name}"
            personalized_message = custom_message or f"Hi {influencer_name}, we'd like to discuss a potential collaboration on our {product_name}."
            collaboration_details = f"We're interested in collaborating with you on our {product_name} and would like to understand your preferences."
            information_request = f"We'd appreciate learning about your collaboration preferences and availability for this type of partnership."
            call_to_action = "Please let us know if you're interested in discussing this opportunity further."
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .content {{ background: #fff; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ margin-top: 5px; }}
                .highlight {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d; }}
                .cta {{ background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }}
                .personalized {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; white-space: pre-line; }}
            </style>
        </head>
        <body>
            <div class="container">
                {f'<div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;"><strong>🎭 DEMO MODE:</strong> This email was intended for <strong>{influencer_name}</strong> but redirected to you for testing purposes.</div>' if demo_mode else ''}
                <div class="header">
                    <h2>🤝 Partnership Opportunity</h2>
                    <p>Hello {influencer_name}!</p>
                </div>
                
                <div class="content">
                    <div class="personalized">
                        {personalized_message}
                    </div>
                    
                    <div class="field">
                        <div class="label">From:</div>
                        <div class="value">{company_name}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">Product:</div>
                        <div class="value">{product_name}</div>
                    </div>
                    
                    {f'<div class="field"><div class="label">Initial Offer:</div><div class="value">{suggested_pricing}</div></div>' if suggested_pricing else ''}
                    
                    {f'<div class="field"><div class="label">Expected Revenue Impact:</div><div class="value">{expected_profit}</div></div>' if expected_profit else ''}
                    
                    <div class="highlight">
                        <strong>Collaboration Opportunity:</strong><br>
                        {collaboration_details}
                    </div>
                    
                    <div class="highlight">
                        <strong>We'd like to understand:</strong><br>
                        {information_request}
                    </div>
                    
                    <p>{call_to_action}</p>
                    
                    <a href="mailto:{self.from_email}?subject=Re: {subject}" class="cta">Reply to Discuss Partnership</a>
                </div>
                
                <div class="footer">
                    <p>This message was sent from Dreamwell Influencer Platform.</p>
                    <p>Timestamp: {self._get_current_timestamp()}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_notification_email_html(self, subject: str, message: str, influencer_count: int) -> str:
        """Create HTML content for notification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .content {{ background: #fff; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px; }}
                .stats {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📊 Dreamwell Search Results</h2>
                    <p>Your influencer search has completed!</p>
                </div>
                
                <div class="content">
                    <div class="stats">
                        <strong>Search Summary:</strong><br>
                        Found {influencer_count} potential influencers
                    </div>
                    
                    <p>{message}</p>
                    
                    <p>You can view the detailed results and contact influencers directly from your Dreamwell dashboard.</p>
                </div>
                
                <div class="footer">
                    <p>This notification was sent from Dreamwell Influencer Platform.</p>
                    <p>Timestamp: {self._get_current_timestamp()}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _send_with_resend(self, to_email: str, subject: str, html_content: str) -> Tuple[bool, str]:
        """Send email using Resend API"""
        try:
            import requests
            
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "replyTo": to_email  # Add replyTo field
            }
            
            print(f"🌐 Sending email via Resend to {to_email}")
            print(f"📧 Email details: From={self.from_email}, Subject={subject}")
            response = requests.post(url, headers=headers, json=data)
            
            print(f"📊 Resend API Response: Status {response.status_code}")
            print(f"📄 Response Body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                email_id = result.get('id', 'Unknown ID')
                print(f"✅ Email sent successfully via Resend!")
                print(f"📧 Email ID: {email_id}")
                print(f"📬 Status: {result.get('status', 'Unknown')}")
                print(f"📅 Created: {result.get('created_at', 'Unknown')}")
                return True, f"Email sent successfully (ID: {email_id})"
            else:
                error_detail = response.text
                print(f"❌ Resend API error: {response.status_code}")
                print(f"❌ Error details: {error_detail}")
                return False, f"Resend API error {response.status_code}: {error_detail}"
                
        except Exception as e:
            print(f"❌ Resend email error: {e}")
            return False, f"Resend error: {str(e)}"
    
    def _log_to_console(self, name: str, email: str, subject: str, html_content: str) -> Tuple[bool, str]:
        """Log email to console (development mode)"""
        try:
            print("📧 Email (Console Mode):")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"To: {name} <{email}>")
            print(f"Subject: {subject}")
            print(f"Content: [HTML content generated]")
            print(f"Timestamp: {self._get_current_timestamp()}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Also log the intended recipient for demo mode
            if "[DEMO]" in subject:
                print("🎭 DEMO MODE: This email was redirected for testing")
                print(f"📧 Intended recipient: {name} <{email}>")
                print(f"📤 Actually sent to: {self.to_email}")
            
            return True, "Email logged to console"
            
        except Exception as e:
            print(f"Console logging error: {e}")
            return False, f"Console error: {str(e)}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def verify_resend_setup(self) -> Tuple[bool, str]:
        """Verify Resend API setup and domain configuration"""
        try:
            if not self.resend_api_key:
                return False, "RESEND_API_KEY not set"
            
            import requests
            
            # Check API key validity by getting domains
            url = "https://api.resend.com/domains"
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                domains = response.json().get('data', [])
                print(f"✅ Resend API key is valid")
                print(f"📧 Available domains: {[d.get('name') for d in domains]}")
                
                # Check if FROM_EMAIL domain is verified
                from_domain = self.from_email.split('@')[1] if '@' in self.from_email else None
                verified_domains = [d.get('name') for d in domains if d.get('status') == 'verified']
                
                if from_domain and from_domain in verified_domains:
                    return True, f"Domain {from_domain} is verified and ready to send"
                else:
                    return False, f"Domain {from_domain} is not verified. Verified domains: {verified_domains}"
            else:
                return False, f"API key invalid or error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"Error verifying Resend setup: {str(e)}"

# Convenience functions
def send_sponsor_outreach(influencer_name: str, 
                         influencer_email: str, 
                         company_name: str, 
                         product_name: str,
                         custom_message: str = "",
                         suggested_pricing: str = "",
                         expected_profit: str = "",
                         influencer_data: dict = None) -> Tuple[bool, str]:
    """Convenience function to send sponsor outreach email"""
    service = EmailService()
    return service.send_sponsor_outreach(
        influencer_name, influencer_email, company_name, product_name,
        custom_message, suggested_pricing, expected_profit, influencer_data
    )

def send_notification_email(subject: str, message: str, influencer_count: int = 0) -> Tuple[bool, str]:
    """Convenience function to send notification email"""
    service = EmailService()
    return service.send_notification_email(subject, message, influencer_count)

# Test function
def test_email_service():
    """Test the email service"""
    print("🧪 Testing email service...")
    
    # Test Resend API connection first
    print("\n🔍 Testing Resend API connection...")
    service = EmailService()
    
    if not service.resend_api_key:
        print("❌ RESEND_API_KEY not found in environment variables")
        return
    
    if not service.to_email:
        print("❌ TO_EMAIL not found in environment variables")
        return
        
    print(f"✅ API Key: {'SET' if service.resend_api_key else 'NOT SET'}")
    print(f"✅ To Email: {service.to_email}")
    print(f"✅ From Email: {service.from_email}")
    print(f"✅ Service: {service.email_service}")
    
    # Verify Resend setup
    print("\n🔍 Verifying Resend domain setup...")
    is_valid, message = service.verify_resend_setup()
    print(f"Domain verification: {'✅' if is_valid else '❌'} {message}")
    
    if not is_valid:
        print("\n⚠️  Resend setup issue detected. This may cause emails to fail.")
        print("Please check your Resend dashboard and domain verification.")
    
    # Test sponsor outreach
    print("\n📧 Testing sponsor outreach email...")
    success, message = send_sponsor_outreach(
        influencer_name="Test Influencer",
        influencer_email="test@example.com",
        company_name="Test Company",
        product_name="Test Product",
        custom_message="We'd love to work with you!",
        suggested_pricing="$500 - $1000",
        expected_profit="$2000 - $5000"
    )
    
    print(f"Sponsor outreach test: {'✅' if success else '❌'} {message}")
    
    # Test notification
    print("\n📧 Testing notification email...")
    success, message = send_notification_email(
        subject="Test Notification",
        message="This is a test notification",
        influencer_count=5
    )
    
    print(f"Notification test: {'✅' if success else '❌'} {message}")
    
    print("\n💡 If emails show as sent but you don't receive them:")
    print("1. Check your spam/junk folder")
    print("2. Verify the FROM_EMAIL is authorized in Resend")
    print("3. Check Resend dashboard for delivery status")
    print("4. Ensure TO_EMAIL is correct")

if __name__ == "__main__":
    test_email_service()
