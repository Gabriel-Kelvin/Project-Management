# Project Management API - Backend

A FastAPI-based backend application with simple authentication and Supabase integration for project management.

## 🚀 Features

- ✅ FastAPI framework with automatic API documentation
- ✅ Simple authentication system (signup, login, logout, verify)
- ✅ In-memory session management
- ✅ Token-based authentication
- ✅ Supabase integration ready
- ✅ CORS enabled for React frontend
- ✅ Hot-reload for development
- ✅ Comprehensive API documentation

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application entry point
├── routes/
│   ├── __init__.py
│   └── auth.py              # Authentication endpoints
├── models/
│   ├── __init__.py
│   └── auth.py              # User models and in-memory storage
├── utils/
│   ├── __init__.py
│   ├── config.py            # Environment configuration
│   ├── auth.py              # Authentication utilities
│   └── middleware.py        # Token verification middleware
├── run.py                   # Server run script
├── env_template.txt         # Environment variables template
├── SUPABASE_SCHEMA.md       # Database schema documentation
└── README.md                # This file
```

## 🛠️ Setup Instructions

### 1. Create Virtual Environment

Already done! If you need to activate it again:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies

Already installed! But if needed:
```bash
pip install fastapi uvicorn supabase python-dotenv
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` folder using the template:

```bash
cd backend
copy env_template.txt .env  # Windows
# or
cp env_template.txt .env    # Linux/Mac
```

Edit `.env` and add your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 4. Set Up Supabase Database

Follow the instructions in `SUPABASE_SCHEMA.md` to create the necessary tables in your Supabase project.

### 5. Run the Server

From the backend directory:
```bash
python run.py
```

The server will start on `http://localhost:8000` with hot-reload enabled.

## 📚 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication Endpoints

### POST `/auth/signup`
Register a new user.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "password123",
  "email": "johndoe@example.com"
}
```

**Response:**
```json
{
  "token": "abc123xyz789",
  "user": {
    "id": "user_abc123",
    "username": "johndoe",
    "email": "johndoe@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### POST `/auth/login`
Authenticate a user.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "abc123xyz789",
  "user": {
    "id": "user_abc123",
    "username": "johndoe",
    "email": "johndoe@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### POST `/auth/logout`
Logout the current user (invalidate token).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

### GET `/auth/verify`
Verify if the token is valid.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "user_abc123",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

### GET `/auth/me`
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "user_abc123",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

## 🧪 Testing with Postman/Thunder Client

### 1. Signup
- Method: POST
- URL: `http://localhost:8000/auth/signup`
- Body (JSON):
```json
{
  "username": "testuser",
  "password": "test123",
  "email": "test@example.com"
}
```

### 2. Login
- Method: POST
- URL: `http://localhost:8000/auth/login`
- Body (JSON):
```json
{
  "username": "testuser",
  "password": "test123"
}
```
- Save the token from the response

### 3. Verify Token
- Method: GET
- URL: `http://localhost:8000/auth/verify`
- Headers:
```
Authorization: Bearer <your_token_here>
```

### 4. Logout
- Method: POST
- URL: `http://localhost:8000/auth/logout`
- Headers:
```
Authorization: Bearer <your_token_here>
```

## 🔧 Development

### Hot Reload
The server runs with hot-reload enabled. Any changes to Python files will automatically restart the server.

### Adding New Routes
1. Create a new router file in `routes/`
2. Import it in `app/main.py`
3. Register it with `app.include_router(your_router)`

### Using Supabase
```python
from utils.config import get_supabase_client

# Get Supabase client
supabase = get_supabase_client()

# Example: Query projects
result = supabase.table('projects').select('*').execute()
```

## 🚨 Important Notes

### Security Considerations (Current Implementation)
- ⚠️ Passwords are stored in **plain text** (for simplicity)
- ⚠️ Tokens are **simple UUIDs** (no JWT)
- ⚠️ User data is stored **in-memory** (lost on restart)
- ⚠️ No rate limiting or brute-force protection

### For Production
Before deploying to production, implement:
- ✅ Password hashing (bcrypt, argon2)
- ✅ JWT tokens with expiration
- ✅ Database storage for users
- ✅ Rate limiting
- ✅ Input validation and sanitization
- ✅ HTTPS enforcement
- ✅ Environment-based CORS configuration
- ✅ Logging and monitoring
- ✅ Error tracking (e.g., Sentry)

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SUPABASE_URL | Your Supabase project URL | Yes |
| SUPABASE_KEY | Supabase anon/public key | Yes |
| SUPABASE_SERVICE_ROLE_KEY | Supabase service role key | No* |
| APP_HOST | Server host | No (default: 0.0.0.0) |
| APP_PORT | Server port | No (default: 8000) |

*Service role key is only needed for admin operations

## 🐛 Troubleshooting

### Import Errors
If you get import errors, make sure you're running the server from the backend directory:
```bash
cd backend
python run.py
```

### Supabase Connection Issues
- Verify your `.env` file has the correct credentials
- Check if your Supabase project is active
- Ensure you're using the correct API keys from Supabase dashboard

### CORS Issues
If the frontend can't connect:
- Check that the frontend URL is in the `origins` list in `app/main.py`
- Verify the frontend is running on the correct port

## 📖 Next Steps

1. ✅ Set up Supabase database tables (see `SUPABASE_SCHEMA.md`)
2. ⏭️ Create project management endpoints (CRUD for projects)
3. ⏭️ Create task management endpoints (CRUD for tasks)
4. ⏭️ Implement team member management
5. ⏭️ Add WebSocket support for real-time updates
6. ⏭️ Build the React frontend

## 📄 License

This project is created for educational purposes.

## 🤝 Support

For issues or questions, please check the API documentation at `/docs` or review the code comments.

