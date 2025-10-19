# Project Management System

A comprehensive project management application built with React frontend and FastAPI backend, featuring real-time collaboration, task management, and analytics.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/Gabriel-Kelvin/Project-Management.git
cd Project-Management

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Add your Supabase credentials to backend/.env
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key
# SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Start the application
docker-compose up --build -d

# Verify deployment
curl http://localhost:8010/health
```

### Production Deployment
```bash
# Deploy to production
docker-compose -f docker-compose.yml up --build -d

# Access the application
# Frontend: http://18.234.41.103:3000
# Backend: http://18.234.41.103:8010
# API Docs: http://18.234.41.103:8010/docs
```

## 🛠 Tech Stack

### Frontend
- **React 18** - Modern UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing
- **Zustand** - State management

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Programming language
- **Gunicorn** - WSGI HTTP server
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Database & Services
- **Supabase** - Backend-as-a-Service
- **PostgreSQL** - Database (via Supabase)
- **Redis** - Caching and session storage

### DevOps & Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server for frontend
- **Health Checks** - Application monitoring

## 📚 API Endpoints

### Authentication (5 endpoints)
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/verify` - Verify token
- `GET /auth/me` - Get current user

### Projects (6 endpoints)
- `POST /projects` - Create project
- `GET /projects` - Get all user projects
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `GET /projects/{id}/stats` - Get project statistics

### Tasks (6 endpoints)
- `POST /projects/{id}/tasks` - Create task
- `GET /projects/{id}/tasks` - Get all tasks
- `GET /projects/{id}/tasks/{tid}` - Get task details
- `PUT /projects/{id}/tasks/{tid}` - Update task
- `PATCH /projects/{id}/tasks/{tid}/status` - Update task status
- `DELETE /projects/{id}/tasks/{tid}` - Delete task

### Team Members (6 endpoints)
- `POST /projects/{id}/members` - Add team member
- `GET /projects/{id}/members` - Get all members
- `GET /projects/{id}/members/{user}` - Get member details
- `PUT /projects/{id}/members/{user}` - Update member role
- `DELETE /projects/{id}/members/{user}` - Remove member
- `GET /projects/{id}/members/{user}/permissions` - Get member permissions

### Analytics (3 endpoints)
- `GET /projects/{id}/analytics` - Get project analytics
- `GET /projects/{id}/analytics/timeline` - Get progress timeline
- `GET /projects/{id}/analytics/member/{user}` - Get member analytics

### Dashboard (3 endpoints)
- `GET /dashboard` - Get user dashboard
- `GET /dashboard/summary` - Get quick summary
- `GET /dashboard/recent-activity` - Get recent activity

**Total: 29 Endpoints**

## 🏗 Project Structure

```
project_manager/
├── backend/                 # FastAPI backend
│   ├── app/                # Main application
│   ├── models/             # Data models
│   ├── routes/             # API routes
│   ├── utils/              # Utilities and helpers
│   ├── config/             # Configuration files
│   ├── logs/               # Application logs
│   ├── sql/                # Database scripts
│   ├── Dockerfile          # Backend container
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # React frontend
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # State management
│   │   └── utils/          # Utilities
│   ├── public/             # Static files
│   ├── Dockerfile          # Frontend container
│   ├── package.json        # Node dependencies
│   └── .env.example        # Environment variables template
├── docker-compose.yml      # Multi-container orchestration
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── DEPLOYMENT.md          # Deployment guide
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
BACKEND_PORT=8010
BACKEND_HOST=0.0.0.0
CORS_ORIGINS=http://18.234.41.103:3000,http://localhost:3000
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://18.234.41.103:8010
REACT_APP_ENV=production
```

## 🚀 Deployment

### Local Development
1. Clone the repository
2. Copy `.env.example` files to `.env`
3. Add your Supabase credentials
4. Run `docker-compose up --build -d`

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

## 📊 Features

- **User Authentication** - Secure login/signup with JWT tokens
- **Project Management** - Create, update, and manage projects
- **Task Management** - Kanban board, task creation, and status updates
- **Team Collaboration** - Add members, assign roles, and manage permissions
- **Analytics Dashboard** - Project statistics and performance metrics
- **Real-time Updates** - Live collaboration features
- **Responsive Design** - Mobile-friendly interface
- **Role-based Access** - Owner, Manager, and Member roles

## 🔒 Security

- JWT-based authentication
- Role-based access control
- CORS protection
- Input validation and sanitization
- Secure environment variable handling
- Non-root Docker containers

## 📈 Monitoring

- Health check endpoints
- Application logging
- Performance monitoring
- Error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- Review the API documentation at `/docs` endpoint

---

**Made with ❤️ using React, FastAPI, and Supabase**