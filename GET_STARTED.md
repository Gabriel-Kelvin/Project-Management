# 🚀 GET STARTED - 3 Simple Steps

## Your Backend is Ready! Here's How to Use It:

---

## Step 1️⃣: Create Your .env File

**Option A: Interactive Setup (Recommended)**
```bash
cd backend
python setup.py
```
Follow the prompts to enter your Supabase credentials.

**Option B: Manual Setup**
```bash
cd backend
copy env_template.txt .env  # Windows
# or
cp env_template.txt .env    # Mac/Linux
```
Then edit `.env` with your Supabase credentials from https://app.supabase.com

---

## Step 2️⃣: Start the Server

```bash
cd backend
python run.py
```

You should see:
```
==================================================
🚀 Starting Project Management API Server
==================================================
📍 Host: 0.0.0.0
🔌 Port: 8000
🔄 Hot-reload: Enabled
📚 Docs: http://localhost:8000/docs
==================================================
```

---

## Step 3️⃣: Test Your API

**Open your browser:**
👉 http://localhost:8000/docs

**Try the signup endpoint:**
1. Click on `POST /auth/signup`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "username": "testuser",
     "password": "password123",
     "email": "test@example.com"
   }
   ```
4. Click "Execute"
5. Copy the token from the response!

**Try a protected endpoint:**
1. Click on `GET /auth/verify`
2. Click "Try it out"
3. Click the 🔒 lock icon
4. Enter: `Bearer YOUR_TOKEN_HERE`
5. Click "Authorize" then "Execute"

---

## 🎉 That's It!

Your authentication system is working! You now have:

✅ Signup endpoint
✅ Login endpoint
✅ Logout endpoint
✅ Token verification
✅ User management
✅ Protected routes
✅ CORS enabled for frontend
✅ Auto-generated API docs

---

## 📚 Need More Help?

- **Quick Guide**: Read `backend/QUICKSTART.md`
- **Full Docs**: Read `backend/README.md`
- **Database Setup**: Read `backend/SUPABASE_SCHEMA.md`
- **Project Overview**: Read `PROJECT_OVERVIEW.md`

---

## 🔥 Testing with cURL

```bash
# Signup
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"john123","email":"john@example.com"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"john123"}'

# Verify (replace YOUR_TOKEN with actual token)
curl -X GET "http://localhost:8000/auth/verify" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Next: Set Up Supabase Database

Once you're ready to store real data:
1. Go to https://app.supabase.com
2. Create a new project
3. Follow instructions in `backend/SUPABASE_SCHEMA.md`
4. Create tables for projects, tasks, and team members

---

**Happy Coding! 🚀**

