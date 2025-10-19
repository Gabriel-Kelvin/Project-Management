# Project Management API Documentation

## Overview

This is a comprehensive REST API for a project management application built with FastAPI, Python, and Supabase. The API provides endpoints for user authentication, project management, task tracking, team collaboration, and analytics.

**Base URL:** `http://localhost:8000` (development)  
**API Version:** v1  
**Authentication:** Bearer Token (JWT)

## Table of Contents

1. [Authentication](#authentication)
2. [Projects](#projects)
3. [Tasks](#tasks)
4. [Team Members](#team-members)
5. [Analytics](#analytics)
6. [Dashboard](#dashboard)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)

---

## Authentication

### Sign Up
Create a new user account.

**Endpoint:** `POST /auth/signup`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "john_doe",
    "email": "john@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "created_at": "2025-01-19T10:30:00Z"
  }
}
```

**Validation Rules:**
- Username: 3-20 characters, alphanumeric and underscore only
- Email: Valid email format
- Password: Minimum 6 characters

---

### Login
Authenticate user and receive access token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2025-01-19T10:30:00Z"
    }
  }
}
```

---

### Logout
Invalidate user session.

**Endpoint:** `POST /auth/logout`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### Verify Token
Verify if token is valid and get user info.

**Endpoint:** `GET /auth/verify`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-01-19T10:30:00Z"
  }
}
```

---

## Projects

### Create Project
Create a new project.

**Endpoint:** `POST /projects`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "My New Project",
  "description": "A project for managing our team's tasks"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "My New Project",
    "description": "A project for managing our team's tasks",
    "owner_id": "john_doe",
    "created_at": "2025-01-19T10:30:00Z",
    "updated_at": "2025-01-19T10:30:00Z",
    "progress": 0
  }
}
```

---

### Get All Projects
Get all projects the user has access to.

**Endpoint:** `GET /projects`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `sort_by` (optional): Sort field (name, created_at, updated_at)
- `sort_order` (optional): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "My New Project",
      "description": "A project for managing our team's tasks",
      "owner_id": "john_doe",
      "role": "owner",
      "created_at": "2025-01-19T10:30:00Z",
      "updated_at": "2025-01-19T10:30:00Z",
      "progress": 45,
      "task_count": 10,
      "team_size": 3
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### Get Project by ID
Get detailed information about a specific project.

**Endpoint:** `GET /projects/{project_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "My New Project",
    "description": "A project for managing our team's tasks",
    "owner_id": "john_doe",
    "role": "owner",
    "created_at": "2025-01-19T10:30:00Z",
    "updated_at": "2025-01-19T10:30:00Z",
    "progress": 45,
    "task_count": 10,
    "team_size": 3,
    "members": [
      {
        "username": "john_doe",
        "role": "owner",
        "joined_at": "2025-01-19T10:30:00Z"
      }
    ]
  }
}
```

---

### Update Project
Update project information.

**Endpoint:** `PUT /projects/{project_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated project description"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Updated Project Name",
    "description": "Updated project description",
    "owner_id": "john_doe",
    "updated_at": "2025-01-19T11:00:00Z",
    "progress": 45
  }
}
```

---

### Delete Project
Delete a project (owner only).

**Endpoint:** `DELETE /projects/{project_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

---

## Tasks

### Create Task
Create a new task in a project.

**Endpoint:** `POST /projects/{project_id}/tasks`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Add login and signup functionality",
  "priority": "high",
  "due_date": "2025-01-25T23:59:59Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "title": "Implement user authentication",
    "description": "Add login and signup functionality",
    "status": "todo",
    "priority": "high",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "assigned_to": null,
    "created_by": "john_doe",
    "due_date": "2025-01-25T23:59:59Z",
    "created_at": "2025-01-19T10:30:00Z",
    "updated_at": "2025-01-19T10:30:00Z"
  }
}
```

---

### Get Project Tasks
Get all tasks in a project.

**Endpoint:** `GET /projects/{project_id}/tasks`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `status` (optional): Filter by status (todo, in_progress, completed)
- `priority` (optional): Filter by priority (low, medium, high)
- `assigned_to` (optional): Filter by assigned user
- `sort_by` (optional): Sort field (title, created_at, due_date, priority)
- `sort_order` (optional): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "title": "Implement user authentication",
      "description": "Add login and signup functionality",
      "status": "todo",
      "priority": "high",
      "project_id": "123e4567-e89b-12d3-a456-426614174000",
      "assigned_to": "jane_smith",
      "created_by": "john_doe",
      "due_date": "2025-01-25T23:59:59Z",
      "created_at": "2025-01-19T10:30:00Z",
      "updated_at": "2025-01-19T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### Get Task by ID
Get detailed information about a specific task.

**Endpoint:** `GET /projects/{project_id}/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "title": "Implement user authentication",
    "description": "Add login and signup functionality",
    "status": "todo",
    "priority": "high",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "assigned_to": "jane_smith",
    "created_by": "john_doe",
    "due_date": "2025-01-25T23:59:59Z",
    "created_at": "2025-01-19T10:30:00Z",
    "updated_at": "2025-01-19T10:30:00Z"
  }
}
```

---

### Update Task
Update task information.

**Endpoint:** `PUT /projects/{project_id}/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "priority": "medium",
  "assigned_to": "jane_smith",
  "due_date": "2025-01-30T23:59:59Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "title": "Updated task title",
    "description": "Updated task description",
    "status": "todo",
    "priority": "medium",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "assigned_to": "jane_smith",
    "created_by": "john_doe",
    "due_date": "2025-01-30T23:59:59Z",
    "updated_at": "2025-01-19T11:00:00Z"
  }
}
```

---

### Update Task Status
Update only the status of a task.

**Endpoint:** `PATCH /projects/{project_id}/tasks/{task_id}/status`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "status": "in_progress"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "status": "in_progress",
    "updated_at": "2025-01-19T11:00:00Z"
  }
}
```

---

### Delete Task
Delete a task.

**Endpoint:** `DELETE /projects/{project_id}/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

---

## Team Members

### Add Team Member
Add a user to a project team.

**Endpoint:** `POST /projects/{project_id}/members`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "username": "jane_smith",
  "role": "developer"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "jane_smith",
    "role": "developer",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "joined_at": "2025-01-19T10:30:00Z"
  }
}
```

---

### Get Team Members
Get all team members of a project.

**Endpoint:** `GET /projects/{project_id}/members`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "username": "john_doe",
      "role": "owner",
      "joined_at": "2025-01-19T10:30:00Z"
    },
    {
      "username": "jane_smith",
      "role": "developer",
      "joined_at": "2025-01-19T10:35:00Z"
    }
  ]
}
```

---

### Update Team Member Role
Update a team member's role.

**Endpoint:** `PUT /projects/{project_id}/members/{username}`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "role": "manager"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "jane_smith",
    "role": "manager",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "updated_at": "2025-01-19T11:00:00Z"
  }
}
```

---

### Remove Team Member
Remove a user from a project team.

**Endpoint:** `DELETE /projects/{project_id}/members/{username}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Team member removed successfully"
}
```

---

## Analytics

### Get Project Analytics
Get comprehensive analytics for a project.

**Endpoint:** `GET /projects/{project_id}/analytics`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "total_tasks": 25,
    "completed_tasks": 15,
    "in_progress_tasks": 7,
    "todo_tasks": 3,
    "progress_percentage": 60,
    "priority_breakdown": {
      "high": 5,
      "medium": 12,
      "low": 8
    },
    "team_productivity": [
      {
        "username": "john_doe",
        "tasks_assigned": 10,
        "tasks_completed": 8,
        "completion_rate": 80.0,
        "average_completion_time": 2.5
      }
    ]
  }
}
```

---

### Get Timeline Analytics
Get task completion timeline data.

**Endpoint:** `GET /projects/{project_id}/analytics/timeline`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `days` (optional): Number of days to include (default: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "timeline": [
      {
        "date": "2025-01-19",
        "tasks_completed": 3,
        "tasks_created": 2
      },
      {
        "date": "2025-01-20",
        "tasks_completed": 5,
        "tasks_created": 1
      }
    ]
  }
}
```

---

### Get Member Analytics
Get detailed analytics for a specific team member.

**Endpoint:** `GET /projects/{project_id}/analytics/member/{username}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "jane_smith",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "tasks_assigned": 8,
    "tasks_completed": 6,
    "tasks_in_progress": 2,
    "completion_rate": 75.0,
    "average_completion_time": 3.2,
    "recent_tasks": [
      {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "title": "Task title",
        "status": "completed",
        "completed_at": "2025-01-19T10:30:00Z"
      }
    ]
  }
}
```

---

## Dashboard

### Get Dashboard Summary
Get user dashboard summary data.

**Endpoint:** `GET /dashboard`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_projects": 3,
      "total_assigned_tasks": 15,
      "completed_tasks_by_me": 8,
      "in_progress_tasks_by_me": 4
    },
    "user_projects": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "My Project",
        "description": "Project description",
        "role": "owner",
        "progress": 60,
        "task_count": 10,
        "team_size": 3,
        "created_at": "2025-01-19T10:30:00Z",
        "updated_at": "2025-01-19T11:00:00Z"
      }
    ],
    "my_tasks": [
      {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "title": "My Task",
        "status": "in_progress",
        "priority": "high",
        "project_name": "My Project",
        "due_date": "2025-01-25T23:59:59Z"
      }
    ],
    "recent_activities": [
      {
        "type": "task_completed",
        "username": "john_doe",
        "task_title": "Task title",
        "project_name": "My Project",
        "created_at": "2025-01-19T10:30:00Z"
      }
    ]
  }
}
```

---

## Error Handling

### Error Response Format
All errors follow a consistent format:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Examples

**Validation Error:**
```json
{
  "success": false,
  "error": "Validation error: Username must be at least 3 characters",
  "detail": "The provided username does not meet the minimum length requirement",
  "code": "VALIDATION_ERROR"
}
```

**Authentication Error:**
```json
{
  "success": false,
  "error": "Authentication failed",
  "detail": "Invalid username or password",
  "code": "AUTH_ERROR"
}
```

**Permission Error:**
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "detail": "You don't have permission to perform this action",
  "code": "PERMISSION_ERROR"
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **General endpoints:** 100 requests per minute per IP
- **Authentication endpoints:** 5 login attempts, 3 signup attempts per minute per IP
- **Rate limit headers:** Included in responses when approaching limits

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Examples

### Complete User Flow

1. **Sign up:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "password123"}'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "password123"}'
```

3. **Create project:**
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "My Project", "description": "Project description"}'
```

4. **Add team member:**
```bash
curl -X POST http://localhost:8000/projects/{project_id}/members \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"username": "jane_smith", "role": "developer"}'
```

5. **Create task:**
```bash
curl -X POST http://localhost:8000/projects/{project_id}/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "Implement feature", "priority": "high"}'
```

### JavaScript/Fetch Examples

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'password123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.data.token;

// Create project
const projectResponse = await fetch('http://localhost:8000/projects', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: 'My Project',
    description: 'Project description'
  })
});

const projectData = await projectResponse.json();
```

---

## Testing

### Test Credentials
For testing purposes, you can use these credentials:
- **Username:** `testuser`
- **Password:** `password123`
- **Email:** `test@example.com`

### Postman Collection
Import the provided Postman collection for easy API testing.

### API Documentation
Interactive API documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Support

For API support and questions:
- **Documentation:** This file
- **Issues:** GitHub Issues
- **Email:** support@example.com

---

*Last updated: January 19, 2025*
