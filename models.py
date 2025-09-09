from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

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
    country_code = db.Column(db.String(2), nullable=True)  # ISO 3166-1 alpha-2
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, email, password, company_name=None, website=None, keywords=None, country_code=None):
        self.email = email
        self.password = password  # Store unhashed for testing
        self.company_name = company_name
        self.website = website or ""  # Ensure website is not None
        self.keywords = keywords
        self.country_code = country_code
    
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
            'country_code': self.country_code,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class YouTubeSearchCache(db.Model):
    """Cache for YouTube search results to reduce API calls"""
    __tablename__ = 'youtube_search_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    keywords = db.Column(db.String(500), nullable=False, index=True)
    search_type = db.Column(db.String(50), nullable=False)  # 'channels', 'videos', 'influencers'
    filters_applied = db.Column(db.Text, nullable=True)  # JSON string of filters
    results_data = db.Column(db.Text, nullable=False)  # JSON string of search results
    result_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)  # Cache expiration time
    
    def __init__(self, keywords, search_type, results_data, filters_applied=None, cache_duration_hours=24):
        self.keywords = keywords
        self.search_type = search_type
        self.results_data = results_data
        self.filters_applied = filters_applied
        try:
            parsed = results_data if isinstance(results_data, list) else []
            # If string JSON passed, len(list) will be computed in save path (gems)
            self.result_count = len(parsed)
        except Exception:
            self.result_count = 0
        # Cache expires after specified hours (default 24 hours)
        self.expires_at = datetime.utcnow() + timedelta(hours=cache_duration_hours)
    
    def is_expired(self):
        """Check if cache entry has expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """Convert cache entry to dictionary"""
        return {
            'id': self.id,
            'keywords': self.keywords,
            'search_type': self.search_type,
            'filters_applied': self.filters_applied,
            'result_count': self.result_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }
    
    def __repr__(self):
        return f'<YouTubeSearchCache {self.keywords} ({self.search_type})>'

class VideoCache(db.Model):
    """Cache per-video details and transcript to avoid repeated fetches."""
    __tablename__ = 'video_cache'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    title = db.Column(db.String(512), nullable=True)
    description = db.Column(db.Text, nullable=True)
    channel_id = db.Column(db.String(64), nullable=True, index=True)
    channel_title = db.Column(db.String(256), nullable=True)
    published_at = db.Column(db.String(64), nullable=True)
    thumbnail = db.Column(db.String(512), nullable=True)
    country = db.Column(db.String(8), nullable=True)
    subscriber_count = db.Column(db.Integer, nullable=True)
    view_count = db.Column(db.Integer, nullable=True)
    avg_recent_views = db.Column(db.Integer, nullable=True)
    transcript = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'channel_id': self.channel_id,
            'channel_title': self.channel_title,
            'published_at': self.published_at,
            'thumbnail': self.thumbnail,
            'country': self.country,
            'subscriber_count': self.subscriber_count,
            'view_count': self.view_count,
            'avg_recent_views': self.avg_recent_views,
            'transcript': self.transcript,
        }

class ChannelCache(db.Model):
    """Per-channel cache for derived signals and estimated CPM/RPM."""
    __tablename__ = 'channel_cache'

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    title = db.Column(db.String(256), nullable=True)
    country = db.Column(db.String(8), nullable=True)
    language = db.Column(db.String(8), nullable=True)
    niche = db.Column(db.String(64), nullable=True)
    subscribers = db.Column(db.Integer, nullable=True)
    avg_recent_views = db.Column(db.Integer, nullable=True)
    engagement_rate = db.Column(db.Float, nullable=True)
    cpm_min_usd = db.Column(db.Float, nullable=True)
    cpm_max_usd = db.Column(db.Float, nullable=True)
    rpm_min_usd = db.Column(db.Float, nullable=True)
    rpm_max_usd = db.Column(db.Float, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'channel_id': self.channel_id,
            'title': self.title,
            'country': self.country,
            'language': self.language,
            'niche': self.niche,
            'subscribers': self.subscribers,
            'avg_recent_views': self.avg_recent_views,
            'engagement_rate': self.engagement_rate,
            'cpm_min_usd': self.cpm_min_usd,
            'cpm_max_usd': self.cpm_max_usd,
            'rpm_min_usd': self.rpm_min_usd,
            'rpm_max_usd': self.rpm_max_usd,
        }

class Product(db.Model):
    """User product to drive influencer searches."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    url = db.Column(db.String(1024), nullable=False)
    name = db.Column(db.String(256), nullable=True)
    category = db.Column(db.String(128), nullable=True)
    profit = db.Column(db.Float, nullable=True)
    keywords = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'url': self.url,
            'name': self.name,
            'category': self.category,
            'profit': self.profit,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
