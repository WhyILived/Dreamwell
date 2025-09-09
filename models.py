from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """User model for companies"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)  # Storing unhashed for testing
    company_name = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=False)  # Website is now required
    keywords = db.Column(db.Text, nullable=True)  # Company keywords
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, email, password, company_name=None, website=None, keywords=None):
        self.email = email
        self.password = password  # Store unhashed for testing
        self.company_name = company_name
        self.website = website or ""  # Ensure website is not None
        self.keywords = keywords
    
    def set_password(self, password):
        """Set password (unhashed for testing)"""
        self.password = password
    
    def check_password(self, password):
        """Check if provided password matches (simple comparison for testing)"""
        return self.password == password
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'email': self.email,
            'company_name': self.company_name,
            'website': self.website,
            'keywords': self.keywords,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
