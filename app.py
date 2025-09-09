from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from models import db, bcrypt
from auth import auth_bp
import os
from config import config

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    @app.route('/')
    def home():
        """Home endpoint"""
        return jsonify({
            "message": "Dreamwell Influencer Platform API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "auth": "/api/auth",
                "health": "/health"
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "service": "dreamwell-backend"})
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
