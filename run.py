#!/usr/bin/env python3
"""
Run script for the Dreamwell Flask application
"""

from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Dreamwell Backend API on port {port}")
    print(f"Debug mode: {debug}")
    print("Available endpoints:")
    print("  GET  / - API information")
    print("  GET  /health - Health check")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
