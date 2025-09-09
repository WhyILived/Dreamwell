# Database Setup Guide for SQLite

## 🗄️ **Step 1: No Database Server Needed!**

SQLite is a file-based database, so you don't need to set up any database server. The database file will be created automatically in your project directory.

## ⚙️ **Step 2: Optional Environment File**

You can create a `.env` file in your project root for custom configuration:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
PORT=5000

# Optional: Custom database location
DATABASE_URL=sqlite:///dreamwell.db
```

**Note**: If you don't create a `.env` file, the app will use default settings and create `dreamwell.db` in your project directory.

## 🚀 **Step 3: Setup Database Tables**

Run the setup script:

```bash
python setup_database.py
```

This will:
- ✅ Create the SQLite database file (`dreamwell.db`)
- ✅ Create all database tables
- ✅ Set up the users table for companies
- ✅ Create a test user account

## 🧪 **Step 4: Test the Setup**

1. **Start the backend**:
   ```bash
   python run.py
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd my-app
   npm install
   npm run dev
   ```

3. **Test registration** at `http://localhost:3000/register`

## 🔧 **Troubleshooting**

### Database Connection Issues:
- ✅ Make sure you have write permissions in the project directory
- ✅ Check that no other process is using the database file
- ✅ Verify the `dreamwell.db` file is created after running setup

### Frontend Issues:
- ✅ Run `npm install` in the `my-app` directory
- ✅ Make sure the backend is running on port 5000

## 📊 **Database Schema**

The setup creates one main table:

### `users` table:
- `id` - Primary key
- `email` - Unique email address
- `password_hash` - Hashed password
- `company_name` - Company name
- `website` - Company website (required)
- `is_active` - Account status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## 🎯 **Test User Account**

After setup, you can use this test account:
- **Email**: test@dreamwell.com
- **Password**: TestPassword123
- **Company**: Test Company
- **Website**: https://testcompany.com
