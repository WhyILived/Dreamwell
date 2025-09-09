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
        for i, kw in enumerate(keywords):
            print(f"  → Searching for: {kw}")
            try:
                rows = search_with_filters(kw, max_results=5) or []
                print(f"  → Found {len(rows)} results for '{kw}'")
                # Tag each row with originating keyword
                for r in rows:
                    r["origin_keyword"] = kw
                all_rows.extend(rows)
                
                # Add delay between keyword searches to avoid rate limits
                if i < len(keywords) - 1:
                    print(f"  → Waiting 1 second before next keyword search...")
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                print(f"  ⚠️  Skipping '{kw}' due to error: {e}")
        
        print(f"DEBUG: Total rows found: {len(all_rows)}")

        # Process results with scoring
        # Load user and product data for scoring context
        company_values = []
        company_country = None
        is_luxury = False
        
        try:
            if user_id:
                from models import User, Product
                user = User.query.get(int(user_id))
                if user and user.keywords:
                    company_values = [k.strip() for k in user.keywords.split(',') if k.strip()]
                company_country = user.country_code if user else None
                
                if product_id:
                    product = Product.query.get(int(product_id))
                    if product:
                        is_luxury = product.is_luxury or False
        except Exception as e:
            print(f"DEBUG: Error loading user/product data: {e}")
        
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
        
        print(f"DEBUG: Company context - Values: {company_values}, Country: {company_country}, Luxury: {is_luxury}")
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
                    # Get CPM/RPM and suggested pricing from ChannelCache
                    cpm_avg = None
                    rpm_avg = None
                    pricing = "Price not available"
                    try:
                        from models import ChannelCache
                        ch = ChannelCache.query.filter_by(channel_id=row.get('channel_id')).first()
                        if ch:
                            if ch.cpm_min_usd is not None and ch.cpm_max_usd is not None:
                                cpm_avg = (float(ch.cpm_min_usd) + float(ch.cpm_max_usd)) / 2.0
                            if ch.rpm_min_usd is not None and ch.rpm_max_usd is not None:
                                rpm_avg = (float(ch.rpm_min_usd) + float(ch.rpm_max_usd)) / 2.0
                            # Use suggested pricing if available
                            if ch.suggested_pricing_min_usd is not None and ch.suggested_pricing_max_usd is not None:
                                pricing = f"${ch.suggested_pricing_min_usd:.0f} - ${ch.suggested_pricing_max_usd:.0f}"
                    except Exception:
                        pass
                    
                    # Calculate expected profit if product has profit value
                    expected_profit = "Profit N/A"
                    if product_id:
                        try:
                            from models import Product
                            from cpm import calculate_expected_profit
                            product = Product.query.get(int(product_id))
                            if product and product.profit and product.profit > 0:
                                if ch and ch.cpm_min_usd and ch.cpm_max_usd and ch.rpm_min_usd and ch.rpm_max_usd:
                                    profit_min, profit_max = calculate_expected_profit(
                                        product_profit=product.profit,
                                        cpm_min=ch.cpm_min_usd,
                                        cpm_max=ch.cpm_max_usd,
                                        rpm_min=ch.rpm_min_usd,
                                        rpm_max=ch.rpm_max_usd,
                                        avg_recent_views=ch.avg_recent_views or 0,
                                        subscribers=ch.subscribers or 0,
                                        engagement_rate=ch.engagement_rate,
                                        suggested_pricing_min=ch.suggested_pricing_min_usd,
                                        suggested_pricing_max=ch.suggested_pricing_max_usd
                                    )
                                    expected_profit = f"${profit_min:.0f} - ${profit_max:.0f}"
                        except Exception as e:
                            print(f"DEBUG: Error calculating expected profit: {e}")
                            pass

                    # Call AI scoring API (no delay needed for Gemini)
                    try:
                        import requests
                        print(f"DEBUG: Calling AI scoring for influencer {i + 1}/{len(all_rows[:25])}")
                        scoring_response = requests.post('http://localhost:5000/api/auth/score-influencer', 
                            json={
                                'influencer_data': {
                                    'channel_id': row.get('channel_id', ''),
                                    'title': row.get('title', ''),
                                    'about_description': row.get('about_description', ''),
                                    'description': row.get('description', ''),
                                    'country': row.get('country', ''),
                                    'avg_recent_views': row.get('avg_recent_views', 0),
                                    'subs': row.get('subs', 0),
                                    'cpm_avg': cpm_avg,
                                    'rpm_avg': rpm_avg
                                },
                                'company_values': company_values,
                                'company_country': company_country,
                                'is_luxury': is_luxury,
                                'user_weights': user_weights
                            },
                            timeout=30
                        )
                        
                        if scoring_response.status_code == 200:
                            scoring_data = scoring_response.json()
                            raw_scores = scoring_data.get('raw_scores', {})
                            reasoning = scoring_data.get('reasoning', {})
                            
                            # Apply user weights to calculate final score
                            final_score = (
                                raw_scores.get('values', 50) * user_weights.get('values_weight', 0.20) +
                                raw_scores.get('cultural', 50) * user_weights.get('cultural_weight', 0.10) +
                                raw_scores.get('cpm', 50) * user_weights.get('cpm_weight', 0.20) +
                                raw_scores.get('rpm', 50) * user_weights.get('rpm_weight', 0.20) +
                                raw_scores.get('engagement', 50) * user_weights.get('views_to_subs_weight', 0.30)
                            )
                            
                            component_scores = {
                                "values": raw_scores.get('values', 50),
                                "cultural": raw_scores.get('cultural', 50),
                                "cpm": raw_scores.get('cpm', 50),
                                "rpm": raw_scores.get('rpm', 50),
                                "views_to_subs": raw_scores.get('engagement', 50)
                            }
                        else:
                            # Fallback to simple scoring if AI fails
                            final_score = 50.0
                            component_scores = {"values": 50, "cultural": 50, "cpm": 50, "rpm": 50, "views_to_subs": 50}
                            reasoning = {}
                            
                    except Exception as e:
                        print(f"DEBUG: Error calling AI scoring for influencer {i}: {e}")
                        # Fallback to simple scoring
                        final_score = 50.0
                        component_scores = {"values": 50, "cultural": 50, "cpm": 50, "rpm": 50, "views_to_subs": 50}
                        reasoning = {}

                    processed_influencers.append({
                        "id": i + 1,
                        "title": row.get('title', 'Unknown'),
                        "subs": row.get('subs', 'Unknown'),
                        "views": row.get('views', 'Unknown'),
                        "avg_recent_views": row.get('avg_recent_views'),
                        "score": final_score,
                        "country": row.get('country'),
                        "channel_id": row.get('channel_id', ''),
                        "score_components": {
                            "values": component_scores.get('values', 50),
                            "cultural": component_scores.get('cultural', 50),
                            "cpm": component_scores.get('cpm', 50),
                            "rpm": component_scores.get('rpm', 50),
                            "views_to_subs": component_scores.get('engagement', 50)
                        },
                        "reasoning": reasoning,
                        "cpm_avg": cpm_avg,
                        "rpm_avg": rpm_avg,
                        "pricing": pricing,
                        "expected_profit": expected_profit,
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
                        "expected_profit": "Profit N/A",
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

@auth_bp.route('/score-influencer', methods=['POST'])
def score_influencer():
    """Score a single influencer using Gemini AI for accurate evaluation with caching"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Required fields
        influencer_data = data.get('influencer_data', {})
        company_values = data.get('company_values', [])
        company_country = data.get('company_country')
        is_luxury = data.get('is_luxury', False)
        user_weights = data.get('user_weights', {})
        
        print(f"DEBUG: AI Scoring API received - Company Values: {company_values}, Country: {company_country}, Luxury: {is_luxury}")
        
        if not influencer_data:
            return jsonify({"error": "Influencer data is required"}), 400
        
        # Check cache first
        channel_id = influencer_data.get('channel_id') or influencer_data.get('title', '')
        if channel_id:
            import hashlib
            import json
            from models import AIScoreCache
            
            # Create cache key from company values
            values_str = json.dumps(sorted(company_values), sort_keys=True) if company_values else ""
            values_hash = hashlib.md5(values_str.encode()).hexdigest()
            
            # Check if we have cached results
            cached = AIScoreCache.query.filter_by(
                channel_id=channel_id,
                company_values_hash=values_hash,
                company_country=company_country,
                is_luxury=is_luxury
            ).first()
            
            if cached:
                print(f"DEBUG: Using cached AI scores for channel {channel_id}")
                return jsonify(cached.to_dict()), 200
        
        # Prepare context for Gemini
        channel_title = influencer_data.get('title', '')
        channel_description = influencer_data.get('about_description', '') or influencer_data.get('description', '')
        channel_country = influencer_data.get('country', '')
        avg_views = influencer_data.get('avg_recent_views', 0)
        subscribers = influencer_data.get('subs', 0)
        cpm_avg = influencer_data.get('cpm_avg')
        rpm_avg = influencer_data.get('rpm_avg')
        
        # Create comprehensive prompt for Gemini
        prompt = f"""
You are an expert influencer marketing analyst with 10+ years of experience. Score this YouTube channel for brand partnership potential on a scale of 0-100. Be highly discriminating and provide varied, nuanced scores that reflect real differences between channels.

CHANNEL DETAILS:
- Name: {channel_title}
- Description: {channel_description}
- Country: {channel_country}
- Average Views per Video: {avg_views:,}
- Subscribers: {subscribers:,}
- CPM (Cost Per Mille): ${cpm_avg if cpm_avg else 'Unknown'}
- RPM (Revenue Per Mille): ${rpm_avg if rpm_avg else 'Unknown'}

COMPANY CONTEXT:
- Company Values: {', '.join(company_values) if company_values else 'Not specified'}
- Company Country: {company_country or 'Not specified'}
- Product Type: {'Luxury' if is_luxury else 'Regular'}

SCORING CRITERIA (provide scores 0-100 for each - BE DISCRIMINATING):

1. VALUES ALIGNMENT (0-100): Analyze the channel's content themes, values, and audience demographics against the company's values. Consider:
   - Content themes and messaging alignment
   - Audience demographics and psychographics
   - Brand safety and reputation fit
   - Authenticity of potential partnership
   - Score 90-100 for perfect alignment, 70-89 for good fit, 50-69 for moderate fit, 30-49 for poor fit, 0-29 for no alignment

2. CULTURAL FIT (0-100): Evaluate cultural compatibility between channel and company target market:
   - Geographic and cultural audience overlap
   - Language and communication style
   - Cultural values and norms alignment
   - Market penetration potential
   - Score 90-100 for same culture/region, 70-89 for similar cultures, 50-69 for different but compatible, 30-49 for challenging, 0-29 for incompatible

3. COST EFFICIENCY (0-100): Rate cost-effectiveness based on CPM and reach:
   - CPM value relative to channel size and engagement
   - Cost per actual engaged viewer
   - ROI potential based on audience quality
   - Market rate competitiveness
   - Score 90-100 for excellent value, 70-89 for good value, 50-69 for fair value, 30-49 for poor value, 0-29 for terrible value

4. REVENUE POTENTIAL (0-100): Assess revenue generation potential:
   - For luxury products: Higher RPM = higher score (premium audience)
   - For regular products: Moderate RPM = higher score (mass market appeal)
   - Audience purchasing power and intent
   - Conversion likelihood based on content type
   - Score 90-100 for high conversion potential, 70-89 for good potential, 50-69 for moderate, 30-49 for low, 0-29 for very low

5. ENGAGEMENT QUALITY (0-100): Evaluate audience engagement and content quality:
   - Views-to-subscribers ratio (higher = better)
   - Content consistency and quality
   - Audience loyalty and retention
   - Community engagement level
   - Score 90-100 for exceptional engagement, 70-89 for strong engagement, 50-69 for moderate, 30-49 for weak, 0-29 for very poor

IMPORTANT: Provide varied, realistic scores that reflect genuine differences. Avoid clustering scores around 50-80. Use the full 0-100 range meaningfully.

For reasoning fields, keep each analysis to 20 words or less - be concise and direct.

Respond with ONLY a JSON object in this exact format:
{{
  "values_score": 85,
  "cultural_score": 70,
  "cpm_score": 90,
  "rpm_score": 75,
  "engagement_score": 80,
  "reasoning": {{
    "values": "Brief values alignment analysis (max 20 words)",
    "cultural": "Concise cultural fit assessment (max 20 words)",
    "cpm": "Short cost efficiency summary (max 20 words)",
    "rpm": "Brief revenue potential note (max 20 words)",
    "engagement": "Concise engagement quality summary (max 20 words)"
  }}
}}
"""
        
        # Call Gemini API
        try:
            import google.generativeai as genai
            import os
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            import json
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                scores_data = json.loads(response_text[start:end])
            else:
                raise ValueError("Invalid JSON response from Gemini")
                
        except Exception as e:
            print(f"DEBUG: Error calling Gemini for scoring: {e}")
            # Fallback to internal scoring if Gemini fails
            return jsonify({"error": "Scoring service unavailable"}), 500
        
        # Cache the results
        if channel_id:
            try:
                from models import AIScoreCache, db
                
                # Create new cache entry
                cache_entry = AIScoreCache(
                    channel_id=channel_id,
                    company_values_hash=values_hash,
                    company_country=company_country,
                    is_luxury=is_luxury,
                    values_score=scores_data.get('values_score', 50),
                    cultural_score=scores_data.get('cultural_score', 50),
                    cpm_score=scores_data.get('cpm_score', 50),
                    rpm_score=scores_data.get('rpm_score', 50),
                    engagement_score=scores_data.get('engagement_score', 50),
                    reasoning=json.dumps(scores_data.get('reasoning', {}))
                )
                
                db.session.add(cache_entry)
                db.session.commit()
                print(f"DEBUG: Cached AI scores for channel {channel_id}")
                
            except Exception as e:
                print(f"DEBUG: Error caching AI scores: {e}")
                # Continue without caching if there's an error
        
        # Return raw scores without applying weights
        return jsonify({
            "raw_scores": {
                "values": scores_data.get('values_score', 50),
                "cultural": scores_data.get('cultural_score', 50),
                "cpm": scores_data.get('cpm_score', 50),
                "rpm": scores_data.get('rpm_score', 50),
                "engagement": scores_data.get('engagement_score', 50)
            },
            "reasoning": scores_data.get('reasoning', {})
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Error in score-influencer: {str(e)}")
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
