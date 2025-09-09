from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from datetime import timedelta
import re
from models import Product, ScoringWeights

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
            identity=str(user.id),
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
            identity=str(user.id),
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
        try:
            user_id = int(user_id)
        except Exception:
            return jsonify({"error": "Invalid token subject"}), 401
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
        try:
            user_id = int(user_id)
        except Exception:
            return jsonify({"error": "Invalid token subject"}), 401
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

        if 'country_code' in data:
            cc = (data.get('country_code') or '').strip().upper()[:2]
            user.country_code = cc or None

        print(f"DEBUG: Updated user data - company_name: {user.company_name}, website: {user.website}, keywords: {user.keywords}, country_code: {user.country_code}")

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

        if 'country_code' in data:
            old_value = getattr(user, 'country_code', None)
            cc = (data.get('country_code') or '').strip().upper()[:2]
            user.country_code = cc or None
            if old_value != user.country_code:
                updated_fields.append('country_code')

        print(f"DEBUG: Updated fields: {updated_fields}")
        print(f"DEBUG: Final values - company_name: {user.company_name}, website: {user.website}, keywords: {user.keywords}, country_code: {getattr(user, 'country_code', None)}")

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
        user_id = data.get('user_id')  # Get user ID to save keywords
        
        if not website:
            return jsonify({"error": "Website URL cannot be empty"}), 400
        
        if not user_id:
            return jsonify({"error": "User ID is required to save keywords"}), 400
        
        # Import scraper here to avoid circular imports
        from scraper import scrape
        
        print(f"DEBUG: Generating keywords for website: {website}")
        
        # Generate keywords using the scraper
        keywords = scrape(website, top_n=5)
        
        print(f"DEBUG: Generated keywords: {keywords}")
        
        # Save keywords to user profile
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Convert keywords list to comma-separated string
        keywords_string = ', '.join(keywords)
        
        # Get existing keywords and add new ones (avoid duplicates)
        existing_keywords = user.keywords.split(', ') if user.keywords else []
        existing_keywords = [k.strip() for k in existing_keywords if k.strip()]
        
        # Add new keywords that don't already exist
        new_keywords = []
        for keyword in keywords:
            if keyword not in existing_keywords:
                new_keywords.append(keyword)
        
        # Combine existing and new keywords
        all_keywords = existing_keywords + new_keywords
        user.keywords = ', '.join(all_keywords)
        
        db.session.commit()
        
        print(f"DEBUG: Saved keywords to user profile: {user.keywords}")
        
        return jsonify({
            "message": "Keywords generated and saved successfully",
            "keywords": keywords,
            "new_keywords": new_keywords,
            "all_keywords": all_keywords,
            "count": len(keywords)
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Error generating keywords: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/generate-values', methods=['POST'])
def generate_values():
    """Generate company values from a website using Gemini and save to user profile (stored in keywords field)."""
    try:
        data = request.get_json()
        if not data or 'website' not in data:
            return jsonify({"error": "Website URL is required"}), 400

        website = data['website'].strip()
        user_id = data.get('user_id')

        if not website:
            return jsonify({"error": "Website URL cannot be empty"}), 400
        if not user_id:
            return jsonify({"error": "User ID is required to save values"}), 400

        # Fetch page HTML
        import requests
        html = ""
        try:
            r = requests.get(website, timeout=10)
            r.raise_for_status()
            html = (r.text or "")[:150000]
        except Exception:
            pass

        # Use Gemini to extract values
        values = []
        try:
            import google.generativeai as genai
            import os
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            You are extracting a company's core values from its website to help score influencer fit.
            URL: {website}
            Webpage HTML (truncated):
            ```
            {html}
            ```

            Extract 5-10 concise company values/principles (e.g., sustainability, innovation, inclusivity, premium quality).
            Respond as a JSON array of strings only, no commentary.
            """
            resp = model.generate_content(prompt)
            txt = (resp.text or "").strip()
            import json as _json
            start = txt.find("[")
            end = txt.rfind("]")
            if start != -1 and end != -1 and end > start:
                arr = _json.loads(txt[start:end+1])
                values = [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            values = []

        # Save to user profile (reuse keywords column)
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        existing = user.keywords.split(',') if user.keywords else []
        existing = [k.strip() for k in existing if k.strip()]
        # Replace with values for now (or merge if desired)
        user.keywords = ', '.join(values) if values else user.keywords
        db.session.commit()

        return jsonify({
            "message": "Company values generated successfully",
            "values": values,
            "count": len(values)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/products/ingest', methods=['POST'])
def ingest_product():
    """Create a product by scraping a URL and extracting details via Gemini."""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        url = (data.get('url') or '').strip()
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        if not url:
            return jsonify({"error": "Product URL is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Extract product details
        from gems import GemsAPI
        gems = GemsAPI()
        extracted = gems.extract_product_from_url(url)

        # Persist
        product = Product(
            user_id=user.id,
            url=url,
            name=extracted.get('name'),
            category=extracted.get('category'),
            keywords=", ".join(extracted.get('keywords') or []),
            is_luxury=None,
        )
        db.session.add(product)
        db.session.commit()

        return jsonify({
            "message": "Product ingested successfully",
            "product": product.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/products', methods=['GET'])
def list_products():
    """List products for a user."""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        products = Product.query.filter_by(user_id=user_id).order_by(Product.created_at.desc()).all()
        return jsonify({
            "products": [p.to_dict() for p in products],
            "count": len(products)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id: int):
    """Update product fields (manual edits)."""
    try:
        data = request.get_json() or {}
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Update editable fields
        if 'name' in data:
            product.name = (data.get('name') or '').strip() or None
        if 'category' in data:
            product.category = (data.get('category') or '').strip() or None
        if 'profit' in data:
            try:
                val = data.get('profit')
                product.profit = float(val) if val is not None else None
            except Exception:
                product.profit = None
        if 'keywords' in data:
            product.keywords = (data.get('keywords') or '').strip() or None
        if 'is_luxury' in data:
            try:
                product.is_luxury = bool(data.get('is_luxury')) if data.get('is_luxury') is not None else None
            except Exception:
                product.is_luxury = None

        db.session.commit()
        return jsonify({"message": "Product updated", "product": product.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
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
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        
        # Import extract here to avoid circular imports
        from extract import search_with_filters
        # pricing temporarily removed; no Gemini imports
        
        print(f"DEBUG: Searching for influencers with keywords: {keywords}")
        
        # Aggregate results: top 5 per keyword
        print("DEBUG: Running filtered search: top 5 per keyword")
        all_rows = []
        for kw in keywords:
            print(f"  → Searching for: {kw}")
            try:
                rows = search_with_filters(kw, max_results=5) or []
                # Tag each row with originating keyword
                for r in rows:
                    r["origin_keyword"] = kw
                all_rows.extend(rows)
            except Exception as e:
                print(f"  ⚠️  Skipping '{kw}' due to error: {e}")

        # Process results with scoring
        # Load user's scoring weights
        user_weights = None
        try:
            if user_id:
                weights_record = ScoringWeights.query.filter_by(user_id=int(user_id)).first()
                if weights_record:
                    user_weights = {
                        'values_weight': weights_record.values_weight,
                        'cultural_weight': weights_record.cultural_weight,
                        'cpm_weight': weights_record.cpm_weight,
                        'rpm_weight': weights_record.rpm_weight,
                        'views_to_subs_weight': weights_record.views_to_subs_weight
                    }
        except Exception:
            pass
        
        # Use default weights if none found
        if not user_weights:
            user_weights = {
                'values_weight': 0.20,
                'cultural_weight': 0.10,
                'cpm_weight': 0.20,
                'rpm_weight': 0.20,
                'views_to_subs_weight': 0.30
            }
        
        # Context defaults
        company_values = locals().get('company_values', [])
        company_country = locals().get('company_country', None)
        is_luxury = locals().get('is_luxury', None)
        processed_influencers = []
        avg_views = 0
        avg_score = 0

        if all_rows:
            # Calculate averages
            def to_int_safe(x):
                try:
                    return int(x)
                except Exception:
                    return 0
            def to_float_safe(x):
                try:
                    return float(x)
                except Exception:
                    return 0.0

            total_views = sum(to_int_safe(r.get('views', 0)) for r in all_rows)
            total_score = sum(to_float_safe(r.get('score', 0)) for r in all_rows)
            avg_views = total_views / len(all_rows) if all_rows else 0
            avg_score = total_score / len(all_rows) if all_rows else 0

            for i, row in enumerate(all_rows[:25]):  # hard cap to avoid overload
                try:
                    pricing = "Price not available"
                    # Helpers
                    def clamp01(v):
                        try:
                            return max(0.0, min(1.0, float(v)))
                        except Exception:
                            return 0.0
                    def score_values_match(about_text: str) -> float:
                        if not about_text or not company_values:
                            return 0.5
                        text = (about_text or '').lower()
                        hits = sum(1 for v in company_values if v and v in text)
                        return clamp01(hits / max(1, len(company_values)))
                    def score_cultural(influencer_country: str) -> float:
                        if not company_country or not influencer_country:
                            return 0.5
                        return 1.0 if (company_country or '').upper() == (influencer_country or '').upper() else 0.5
                    def score_cpm(avg_cpm: float) -> float:
                        if not avg_cpm or avg_cpm <= 0:
                            return 0.5
                        if avg_cpm <= 5: return 1.0
                        if avg_cpm >= 40: return 0.0
                        return clamp01((40 - avg_cpm) / 35)
                    def score_rpm(avg_rpm: float) -> float:
                        if not avg_rpm or avg_rpm <= 0:
                            return 0.5
                        if is_luxury:
                            if avg_rpm <= 2: return 0.0
                            if avg_rpm >= 20: return 1.0
                            return clamp01((avg_rpm - 2) / 18)
                        else:
                            if avg_rpm <= 2: return 1.0
                            if avg_rpm >= 20: return 0.0
                            return clamp01((20 - avg_rpm) / 18)
                    def score_ratio(avg_views: float, subs: float) -> float:
                        try:
                            subs = float(subs)
                            if subs <= 0: return 0.5
                            ratio = float(avg_views or 0) / subs
                            return clamp01(ratio / 0.2)
                        except Exception:
                            return 0.5

                    # CPM/RPM from ChannelCache
                    cpm_avg = None
                    rpm_avg = None
                    try:
                        from models import ChannelCache
                        ch = ChannelCache.query.filter_by(channel_id=row.get('channel_id')).first()
                        if ch:
                            if ch.cpm_min_usd is not None and ch.cpm_max_usd is not None:
                                cpm_avg = (float(ch.cpm_min_usd) + float(ch.cpm_max_usd)) / 2.0
                            if ch.rpm_min_usd is not None and ch.rpm_max_usd is not None:
                                rpm_avg = (float(ch.rpm_min_usd) + float(ch.rpm_max_usd)) / 2.0
                    except Exception:
                        pass

                    s_values = score_values_match(row.get('about_description') or row.get('description'))
                    s_culture = score_cultural(row.get('country'))
                    s_cpm = score_cpm(cpm_avg if cpm_avg is not None else 0)
                    s_rpm = score_rpm(rpm_avg if rpm_avg is not None else 0)
                    s_ratio = score_ratio(row.get('avg_recent_views') or 0, row.get('subs') or 0)

                    # Use user's custom weights
                    weighted = (
                        s_values * user_weights['values_weight'] +
                        s_culture * user_weights['cultural_weight'] +
                        s_cpm * user_weights['cpm_weight'] +
                        s_rpm * user_weights['rpm_weight'] +
                        s_ratio * user_weights['views_to_subs_weight']
                    )
                    final_score_100 = round(weighted * 100, 1)

                    processed_influencers.append({
                        "id": i + 1,
                        "title": row.get('title', 'Unknown'),
                        "subs": row.get('subs', 'Unknown'),
                        "views": row.get('views', 'Unknown'),
                        "avg_recent_views": row.get('avg_recent_views'),
                        "score": final_score_100,
                        "country": row.get('country'),
                        "score_components": {
                            "values": round(s_values * 100, 1),
                            "cultural": round(s_culture * 100, 1),
                            "cpm": round(s_cpm * 100, 1),
                            "rpm": round(s_rpm * 100, 1),
                            "views_to_subs": round(s_ratio * 100, 1)
                        },
                        "cpm_avg": cpm_avg,
                        "rpm_avg": rpm_avg,
                        "pricing": pricing,
                        "url": row.get('url', ''),
                        "description": row.get('description', ''),
                        "origin_keyword": row.get('origin_keyword', '')
                    })
                except Exception as e:
                    print(f"DEBUG: Error scoring influencer {i}: {str(e)}")
                    processed_influencers.append({
                        "id": i + 1,
                        "title": row.get('title', 'Unknown'),
                        "subs": row.get('subs', 'Unknown'),
                        "views": row.get('views', 'Unknown'),
                        "avg_recent_views": row.get('avg_recent_views'),
                        "score": row.get('score', 'Unknown'),
                        "country": row.get('country'),
                        "pricing": "Price not available",
                        "url": row.get('url', ''),
                        "description": row.get('description', ''),
                        "origin_keyword": row.get('origin_keyword', '')
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

@auth_bp.route('/scoring-weights', methods=['GET'])
def get_scoring_weights():
    """Get user's scoring weight preferences"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        weights = ScoringWeights.query.filter_by(user_id=user_id).first()
        if not weights:
            # Create default weights if none exist
            weights = ScoringWeights(
                user_id=user_id,
                values_weight=0.20,
                cultural_weight=0.10,
                cpm_weight=0.20,
                rpm_weight=0.20,
                views_to_subs_weight=0.30
            )
            db.session.add(weights)
            db.session.commit()
        
        return jsonify({
            "weights": weights.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/scoring-weights', methods=['POST'])
def update_scoring_weights():
    """Update user's scoring weight preferences"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Validate weights sum to 1.0 (100%)
        total_weight = sum([
            data.get('values_weight', 0),
            data.get('cultural_weight', 0),
            data.get('cpm_weight', 0),
            data.get('rpm_weight', 0),
            data.get('views_to_subs_weight', 0)
        ])
        
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            return jsonify({"error": "Weights must sum to 100%"}), 400
        
        # Get or create weights record
        weights = ScoringWeights.query.filter_by(user_id=user_id).first()
        if not weights:
            weights = ScoringWeights(user_id=user_id)
            db.session.add(weights)
        
        # Update weights
        weights.values_weight = data.get('values_weight', 0.20)
        weights.cultural_weight = data.get('cultural_weight', 0.10)
        weights.cpm_weight = data.get('cpm_weight', 0.20)
        weights.rpm_weight = data.get('rpm_weight', 0.20)
        weights.views_to_subs_weight = data.get('views_to_subs_weight', 0.30)
        
        db.session.commit()
        
        return jsonify({
            "message": "Scoring weights updated successfully",
            "weights": weights.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
