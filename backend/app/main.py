"""
FastAPI main application with CORS configuration and route registration.

=============================================================================
COMPLETE API ENDPOINTS
=============================================================================

Authentication (5 endpoints):
  POST   /auth/signup                      - Register new user
  POST   /auth/login                       - Login user
  POST   /auth/logout                      - Logout user (auth required)
  GET    /auth/verify                      - Verify token (auth required)
  GET    /auth/me                          - Get current user (auth required)

Projects (6 endpoints):
  POST   /projects                         - Create project (auth required)
  GET    /projects                         - Get all user projects (auth required)
  GET    /projects/{id}                    - Get project details (auth required)
  PUT    /projects/{id}                    - Update project (owner only)
  DELETE /projects/{id}                    - Delete project (owner only)
  GET    /projects/{id}/stats              - Get project statistics (auth required)

Tasks (6 endpoints):
  POST   /projects/{id}/tasks              - Create task (auth required)
  GET    /projects/{id}/tasks              - Get all tasks (auth required)
  GET    /projects/{id}/tasks/{tid}        - Get task details (auth required)
  PUT    /projects/{id}/tasks/{tid}        - Update task (role-based)
  PATCH  /projects/{id}/tasks/{tid}/status - Update task status (role-based)
  DELETE /projects/{id}/tasks/{tid}        - Delete task (owner/manager)

Team Members (6 endpoints):
  POST   /projects/{id}/members            - Add team member (owner only)
  GET    /projects/{id}/members            - Get all members (auth required)
  GET    /projects/{id}/members/{user}     - Get member details (auth required)
  PUT    /projects/{id}/members/{user}     - Update member role (owner only)
  DELETE /projects/{id}/members/{user}     - Remove member (owner only)
  GET    /projects/{id}/members/{user}/permissions - Get member permissions

Analytics (3 endpoints):
  GET    /projects/{id}/analytics          - Get project analytics (owner/manager)
  GET    /projects/{id}/analytics/timeline - Get progress timeline (owner/manager)
  GET    /projects/{id}/analytics/member/{user} - Get member analytics

Dashboard (3 endpoints):
  GET    /dashboard                        - Get user dashboard (auth required)
  GET    /dashboard/summary                - Get quick summary (auth required)
  GET    /dashboard/recent-activity        - Get recent activity (auth required)

Total: 29 Endpoints
=============================================================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.auth import router as auth_router
from routes.projects import router as projects_router
from routes.tasks import router as tasks_router
from routes.roles import router as roles_router
from routes.analytics import router as analytics_router
from routes.dashboard import router as dashboard_router
from utils.exceptions import (
    ProjectNotFoundException, UnauthorizedAccessException,
    InvalidDataException, DatabaseException, TaskNotFoundException,
    TeamMemberNotFoundException, DuplicateEntryException,
    MemberAlreadyExistsException, InvalidRoleException,
    CannotRemoveOwnerException, UserNotFoundException,
    InsufficientPermissionsException
)

# Create FastAPI application
app = FastAPI(
    title="Project Management API",
    description="A comprehensive project management API with authentication and Supabase integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Configure CORS to allow requests from React frontend
from utils.config import CORS_ORIGINS
origins = CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies and authorization headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Register routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(roles_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Project Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Global health check endpoint."""
    return {
        "status": "healthy",
        "api": "project_management",
        "version": "1.0.0"
    }

# Custom exception handlers
@app.exception_handler(ProjectNotFoundException)
async def project_not_found_handler(request, exc):
    """Handle project not found exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(UnauthorizedAccessException)
async def unauthorized_access_handler(request, exc):
    """Handle unauthorized access exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(InvalidDataException)
async def invalid_data_handler(request, exc):
    """Handle invalid data exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(DatabaseException)
async def database_exception_handler(request, exc):
    """Handle database exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(TaskNotFoundException)
async def task_not_found_handler(request, exc):
    """Handle task not found exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(TeamMemberNotFoundException)
async def team_member_not_found_handler(request, exc):
    """Handle team member not found exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(DuplicateEntryException)
async def duplicate_entry_handler(request, exc):
    """Handle duplicate entry exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(MemberAlreadyExistsException)
async def member_already_exists_handler(request, exc):
    """Handle member already exists exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(InvalidRoleException)
async def invalid_role_handler(request, exc):
    """Handle invalid role exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(CannotRemoveOwnerException)
async def cannot_remove_owner_handler(request, exc):
    """Handle cannot remove owner exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request, exc):
    """Handle user not found exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(InsufficientPermissionsException)
async def insufficient_permissions_handler(request, exc):
    """Handle insufficient permissions exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    print(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run tasks on application startup."""
    from utils.logger import log_startup
    log_startup()
    print("=" * 80)
    print("🚀 PROJECT MANAGEMENT API - READY")
    print("=" * 80)
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 ReDoc Documentation: http://localhost:8000/redoc")
    print("=" * 80)
    print("📊 Total Endpoints: 29")
    print("  - Authentication: 5")
    print("  - Projects: 6")
    print("  - Tasks: 6")
    print("  - Team Members: 6")
    print("  - Analytics: 3")
    print("  - Dashboard: 3")
    print("=" * 80)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run tasks on application shutdown."""
    from utils.logger import log_shutdown
    log_shutdown()
    print("=" * 80)
    print("👋 Project Management API - Shutdown Complete")
    print("=" * 80)

