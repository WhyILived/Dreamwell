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
        
        # Validate email
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
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
            website=website if website else None
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
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update allowed fields
        if 'company_name' in data:
            user.company_name = data['company_name'].strip() if data['company_name'] else None
        
        if 'website' in data:
            user.website = data['website'].strip() if data['website'] else None
        
        db.session.commit()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
