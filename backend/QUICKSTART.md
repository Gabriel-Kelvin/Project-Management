# Quick Start Guide

Get your Project Management API up and running in 5 minutes!

## ⚡ Quick Setup

### Step 1: Create .env file
```bash
cd backend
copy env_template.txt .env
```

Edit `.env` with your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
APP_HOST=0.0.0.0
APP_PORT=8000
```

### Step 2: Start the server
```bash
python run.py
```

### Step 3: Open API docs
Visit: http://localhost:8000/docs

## 🧪 Test the API

### 1. Create a user (Signup)
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
  }'
```

**Response:**
```json
{
  "token": "abc123...",
  "user": {
    "id": "user_abc123",
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Save the token for next steps!**

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 3. Verify token
```bash
curl -X GET "http://localhost:8000/auth/verify" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Get current user
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Logout
```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 Using Postman / Thunder Client

1. **Import into Postman:**
   - Open Postman
   - Go to File > Import
   - Import from URL: `http://localhost:8000/openapi.json`

2. **Test Signup:**
   - Method: POST
   - URL: `http://localhost:8000/auth/signup`
   - Body: Select "raw" and "JSON"
   - Paste:
   ```json
   {
     "username": "john",
     "password": "john123",
     "email": "john@example.com"
   }
   ```
   - Click Send
   - Copy the token from response

3. **Test Protected Endpoint:**
   - Method: GET
   - URL: `http://localhost:8000/auth/verify`
   - Headers tab:
     - Key: `Authorization`
     - Value: `Bearer YOUR_TOKEN`
   - Click Send

## 🗄️ Set Up Supabase (Optional but recommended)

1. Go to https://app.supabase.com
2. Create a new project
3. Copy your credentials to `.env`
4. Follow `SUPABASE_SCHEMA.md` to create database tables
5. You're ready to store real data!

## 🎉 You're All Set!

Your backend is now running with:
- ✅ Authentication endpoints
- ✅ Token-based security
- ✅ CORS enabled for frontend
- ✅ Hot-reload for development
- ✅ Auto-generated API docs

## 📖 Next Steps

- Read `README.md` for detailed documentation
- Check `SUPABASE_SCHEMA.md` for database setup
- Start building your frontend!
- Add more endpoints for projects and tasks

## ❓ Troubleshooting

**Server won't start?**
- Make sure you're in the `backend` directory
- Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Can't connect from frontend?**
- Check CORS settings in `app/main.py`
- Make sure your frontend URL is in the `origins` list
- Verify the server is running on port 8000

**Import errors?**
- Run from the backend directory: `cd backend && python run.py`
- Check Python version (Python 3.8+ required)

## 🆘 Need Help?

- Check the interactive docs: http://localhost:8000/docs
- Read the full README.md
- Review the code comments

