# Dreamwell - Influencer Platform Backend

A Flask-based backend API for the Dreamwell influencer search platform where companies can find and connect with influencers.

## Features

- 🚀 Flask REST API with PostgreSQL database
- 🔐 JWT-based authentication for companies
- 👥 User management (company registration/login)
- 📡 JSON API responses
- 🏥 Health check endpoint
- ⚙️ Configurable settings

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- PostgreSQL 12+ (with pgAdmin)
- Git

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Dreamwell
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
   - Install PostgreSQL and pgAdmin
   - Create a database named `dreamwell`
   - Update database credentials in `.env` file

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. Initialize the database:
```bash
python init_db.py
```

7. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### GET /
Returns API information and available endpoints.

### GET /health
Health check endpoint.

### POST /api/auth/register
Register a new company user.

**Request Body:**
```json
{
  "email": "company@example.com",
  "password": "SecurePassword123",
  "company_name": "My Company",
  "website": "https://mycompany.com"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "company@example.com",
    "company_name": "My Company",
    "website": "https://mycompany.com",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST /api/auth/login
Login with company credentials.

**Request Body:**
```json
{
  "email": "company@example.com",
  "password": "SecurePassword123"
}
```

### GET /api/auth/profile
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

### PUT /api/auth/profile
Update user profile (requires authentication).

**Request Body:**
```json
{
  "company_name": "Updated Company Name",
  "website": "https://newwebsite.com"
}
```


## Configuration

The application uses environment variables for configuration:

- `FLASK_ENV`: Set to `development` for debug mode
- `PORT`: Port to run the server on (default: 5000)
- `SECRET_KEY`: Secret key for Flask sessions
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `DB_HOST`: PostgreSQL host (default: localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name (default: dreamwell)
- `DB_USER`: Database username (default: postgres)
- `DB_PASSWORD`: Database password

## Development

### Project Structure

```
Dreamwell/
├── app.py                 # Main Flask application
├── run.py                 # Application runner
├── config.py              # Configuration settings
├── models.py              # Database models
├── auth.py                # Authentication routes
├── init_db.py             # Database initialization
├── test_auth.py           # Authentication testing
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md
```

### Testing

```bash
# Test the API endpoints
curl http://localhost:5000/
curl http://localhost:5000/health

# Test authentication
python test_auth.py
```

### Database Setup with pgAdmin

1. **Install PostgreSQL and pgAdmin**
2. **Create Database:**
   - Open pgAdmin
   - Right-click "Databases" → "Create" → "Database"
   - Name: `dreamwell`
   - Click "Save"

3. **Update .env file:**
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=dreamwell
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   ```

4. **Initialize tables:**
   ```bash
   python init_db.py
   ```

## Next Steps

- [ ] Add product management endpoints
- [ ] Implement influencer search and scraping
- [ ] Add brand analysis functionality
- [ ] Create influencer matching algorithm
- [ ] Add pricing calculation system
- [ ] Implement email automation
- [ ] Add request validation middleware
- [ ] Create a frontend interface
- [ ] Add logging and monitoring

## License

This project is licensed under the MIT License.
