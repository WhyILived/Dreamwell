# Configuration example for Dreamwell Deep Search
# Copy this to your .env file or set as environment variables

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///dreamwell.db
JWT_SECRET_KEY=your-jwt-secret-here

# Twelve Labs Configuration
TWELVE_LABS_API_KEY=your-twelve-labs-api-key-here

# To use this configuration:
# 1. Set the TWELVE_LABS_API_KEY environment variable
# 2. Or modify the deep_search_service.py file to include your API key directly
