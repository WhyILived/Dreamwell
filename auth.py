from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_website(website):
    """Validate website URL format"""
    if not website:
        return False, "Website URL is required"
    
    # Basic URL validation
    pattern = r'^https?:\/\/.+\..+'
    if not re.match(pattern, website):
        return False, "Please enter a valid website URL (e.g., https://yourcompany.com)"
    
    return True, "Valid website URL"

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new company user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        company_name = data.get('company_name', '').strip()
        website = data.get('website', '').strip()
        keywords = data.get('keywords', '').strip()
        
        # Validate email
        if not email:
            return jsonify({"error": "Email is required, die"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate website
        website = data.get('website', '').strip()
        if not website:
            return jsonify({"error": "Website URL is required"}), 400
        
        is_valid_website, website_message = validate_website(website)
        if not is_valid_website:
            return jsonify({"error": website_message}), 400
        
        # Validate password
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            return jsonify({"error": password_message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409
        
        # Create new user
        user = User(
            email=email,
            password=password,
            company_name=company_name if company_name else None,
            website=website,  # Website is now required
            keywords=keywords if keywords else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict(),
            "access_token": access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 401
        
        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        print(f"DEBUG: User ID from JWT: {user_id}")

        user = User.query.get(user_id)

        if not user:
            print(f"DEBUG: User not found for ID: {user_id}")
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        print(f"DEBUG: Received data: {data}")

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update allowed fields
        if 'company_name' in data:
            user.company_name = data['company_name'].strip() if data['company_name'] else None

        if 'website' in data:
            user.website = data['website'].strip() if data['website'] else None

        if 'keywords' in data:
            user.keywords = data['keywords'].strip() if data['keywords'] else None

        print(f"DEBUG: Updated user data - company_name: {user.company_name}, website: {user.website}, keywords: {user.keywords}")

        db.session.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error in update_profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile/simple', methods=['PUT'])
def update_profile_simple():
    """Update user profile without JWT validation (for testing)"""
    try:
        data = request.get_json()
        print(f"DEBUG: Simple update received data: {data}")

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get user by ID (simple approach)
        user_id = data.get('id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Track what fields are being updated
        updated_fields = []
        
        # Update allowed fields only if they exist in the request
        if 'company_name' in data:
            old_value = user.company_name
            user.company_name = data['company_name'].strip() if data['company_name'] else None
            if old_value != user.company_name:
                updated_fields.append('company_name')

        if 'website' in data:
            old_value = user.website
            user.website = data['website'].strip() if data['website'] else None
            if old_value != user.website:
                updated_fields.append('website')

        if 'keywords' in data:
            old_value = user.keywords
            user.keywords = data['keywords'].strip() if data['keywords'] else None
            if old_value != user.keywords:
                updated_fields.append('keywords')

        print(f"DEBUG: Updated fields: {updated_fields}")
        print(f"DEBUG: Final values - company_name: {user.company_name}, website: {user.website}, keywords: {user.keywords}")

        db.session.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict(),
            "updated_fields": updated_fields
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error in simple update: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/generate-keywords', methods=['POST'])
def generate_keywords():
    """Generate keywords from a website using the scraper"""
    try:
        data = request.get_json()
        if not data or 'website' not in data:
            return jsonify({"error": "Website URL is required"}), 400
        
        website = data['website'].strip()
        if not website:
            return jsonify({"error": "Website URL cannot be empty"}), 400
        
        # Import scraper here to avoid circular imports
        from scraper import scrape
        
        print(f"DEBUG: Generating keywords for website: {website}")
        
        # Generate keywords using the scraper (same as main.py)
        keywords = scrape(website, top_n=5)
        
        print(f"DEBUG: Generated keywords: {keywords}")
        
        return jsonify({
            "message": "Keywords generated successfully",
            "keywords": keywords,
            "count": len(keywords)
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Error generating keywords: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/search-influencers', methods=['POST'])
def search_influencers():
    """Search for YouTube influencers based on keywords and get pricing"""
    try:
        data = request.get_json()
        if not data or 'keywords' not in data:
            return jsonify({"error": "Keywords are required"}), 400
        
        keywords = data['keywords']
        if not keywords or len(keywords) == 0:
            return jsonify({"error": "At least one keyword is required"}), 400
        
        # Import extract here to avoid circular imports
        from extract import search
        import csv
        import os
        import google.generativeai as genai
        
        print(f"DEBUG: Searching for influencers with keywords: {keywords}")
        
        # Use the first keyword for the search
        first_keyword = keywords[0] if keywords else "influencer marketing"
        
        # Search for influencers (this generates the CSV)
        print(f"DEBUG: Running search with keyword: {first_keyword}")
        search(first_keyword)  # This generates influencers.csv
        
        print(f"DEBUG: Search completed, now reading CSV data")
        
        # Process CSV results and get pricing
        processed_influencers = []
        csv_file = "influencers.csv"
        
        if os.path.exists(csv_file):
            # Read CSV and calculate averages
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
                
                if rows:
                    # Calculate averages
                    total_views = sum(int(row.get('views', 0)) for row in rows if row.get('views', '').isdigit())
                    total_score = sum(float(row.get('score', 0)) for row in rows if row.get('score', '').replace('.', '').isdigit())
                    avg_views = total_views / len(rows) if rows else 0
                    avg_score = total_score / len(rows) if rows else 0
                    
                    # Get Gemini API pricing for each influencer
                    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                    model = genai.GenerativeModel('gemini-pro')
                    
                    for i, row in enumerate(rows[:10]):  # Process top 10 influencers
                        try:
                            # Get pricing from Gemini
                            prompt = f"""
                            Based on this YouTube influencer's stats, estimate the sponsorship value in USD:
                            - Channel: {row.get('title', 'Unknown')}
                            - Subscribers: {row.get('subs', 'Unknown')}
                            - Views: {row.get('views', 'Unknown')}
                            - Score: {row.get('score', 'Unknown')}
                            
                            Provide a realistic sponsorship price range in USD (e.g., "$500-$2000" or "$100-$500").
                            Consider factors like subscriber count, engagement, and niche relevance.
                            """
                            
                            response = model.generate_content(prompt)
                            pricing = response.text.strip() if response.text else "Price not available"
                            
                            processed_influencers.append({
                                "id": i + 1,
                                "title": row.get('title', 'Unknown'),
                                "subs": row.get('subs', 'Unknown'),
                                "views": row.get('views', 'Unknown'),
                                "score": row.get('score', 'Unknown'),
                                "pricing": pricing,
                                "url": row.get('url', ''),
                                "description": row.get('description', '')
                            })
                        except Exception as e:
                            print(f"DEBUG: Error getting pricing for influencer {i}: {str(e)}")
                            processed_influencers.append({
                                "id": i + 1,
                                "title": row.get('title', 'Unknown'),
                                "subs": row.get('subs', 'Unknown'),
                                "views": row.get('views', 'Unknown'),
                                "score": row.get('score', 'Unknown'),
                                "pricing": "Price not available",
                                "url": row.get('url', ''),
                                "description": row.get('description', '')
                            })
        
        return jsonify({
            "message": "Influencer search completed",
            "influencers": processed_influencers,
            "count": len(processed_influencers),
            "averages": {
                "avg_views": avg_views,
                "avg_score": avg_score
            }
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Error searching influencers: {str(e)}")
        return jsonify({"error": str(e)}), 500
