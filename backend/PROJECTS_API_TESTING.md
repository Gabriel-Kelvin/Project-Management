# Projects API Testing Guide

Complete guide to testing all Project Management API endpoints with examples.

## Prerequisites

1. **Start the server**:
   ```bash
   cd backend
   python run.py
   ```

2. **Create Supabase tables**:
   - Run the SQL script in `sql/create_tables.sql` in your Supabase SQL Editor

3. **Get an authentication token**:
   - First signup/login to get a token
   - Use this token in the `Authorization` header for all project endpoints

---

## Authentication (Required First)

### 1. Signup
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
  "token": "abc123xyz789...",
  "user": {
    "id": "user_abc123",
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**⚠️ Save the token! You'll need it for all project requests.**

---

## Projects API Endpoints

### 1. Create Project

**POST** `/projects`

Create a new project. The authenticated user becomes the owner.

**Request:**
```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "description": "Complete redesign of company website",
    "status": "active",
    "progress": 0
  }'
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "owner_id": "testuser",
  "status": "active",
  "progress": 0,
  "created_at": "2024-01-01T10:30:00Z",
  "updated_at": "2024-01-01T10:30:00Z"
}
```

---

### 2. Get All Projects

**GET** `/projects`

Get all projects where you're the owner or a team member.

**Request:**
```bash
curl -X GET "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Website Redesign",
      "description": "Complete redesign of company website",
      "owner_id": "testuser",
      "status": "active",
      "progress": 0,
      "created_at": "2024-01-01T10:30:00Z",
      "updated_at": "2024-01-01T10:30:00Z",
      "team_members": []
    }
  ],
  "total": 1
}
```

---

### 3. Get Single Project

**GET** `/projects/{project_id}`

Get detailed information about a specific project.

**Request:**
```bash
curl -X GET "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "owner_id": "testuser",
  "status": "active",
  "progress": 0,
  "created_at": "2024-01-01T10:30:00Z",
  "updated_at": "2024-01-01T10:30:00Z",
  "team_members": [
    {
      "id": "tm_123",
      "project_id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "john_doe",
      "role": "developer",
      "assigned_at": "2024-01-01T11:00:00Z"
    }
  ]
}
```

---

### 4. Update Project

**PUT** `/projects/{project_id}`

Update project details. Only the owner can update.

**Request:**
```bash
curl -X PUT "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign v2",
    "status": "active",
    "progress": 45
  }'
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Website Redesign v2",
  "description": "Complete redesign of company website",
  "owner_id": "testuser",
  "status": "active",
  "progress": 45,
  "created_at": "2024-01-01T10:30:00Z",
  "updated_at": "2024-01-01T15:30:00Z"
}
```

---

### 5. Delete Project

**DELETE** `/projects/{project_id}`

Delete a project. Only the owner can delete. This also deletes all tasks and team members.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response (204 No Content):**
```
(Empty response body)
```

---

## Team Management Endpoints

### 6. Add Team Member

**POST** `/projects/{project_id}/team`

Add a user to the project team. Only the owner can add members.

**Request:**
```bash
curl -X POST "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000/team" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "role": "developer"
  }'
```

**Response (201 Created):**
```json
{
  "id": "tm_123abc",
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "john_doe",
  "role": "developer",
  "assigned_at": "2024-01-01T11:00:00Z"
}
```

**Available Roles:**
- `owner` - Full control
- `manager` - Can manage project and assign tasks
- `developer` - Can edit and work on tasks
- `viewer` - Read-only access

---

### 7. Get Team Members

**GET** `/projects/{project_id}/team`

Get all team members for a project.

**Request:**
```bash
curl -X GET "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000/team" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
[
  {
    "id": "tm_123abc",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "role": "developer",
    "assigned_at": "2024-01-01T11:00:00Z"
  },
  {
    "id": "tm_456def",
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "jane_smith",
    "role": "manager",
    "assigned_at": "2024-01-01T11:30:00Z"
  }
]
```

---

### 8. Remove Team Member

**DELETE** `/projects/{project_id}/team/{member_id}`

Remove a team member from the project. Only the owner can remove members.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000/team/tm_123abc" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response (204 No Content):**
```
(Empty response body)
```

---

### 9. Get Project Statistics

**GET** `/projects/{project_id}/stats`

Get comprehensive statistics for a project.

**Request:**
```bash
curl -X GET "http://localhost:8000/projects/123e4567-e89b-12d3-a456-426614174000/stats" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response (200 OK):**
```json
{
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "project_name": "Website Redesign",
  "total_tasks": 12,
  "tasks_by_status": {
    "todo": 5,
    "in_progress": 4,
    "completed": 3
  },
  "tasks_by_priority": {
    "low": 3,
    "medium": 6,
    "high": 3
  },
  "team_member_count": 4,
  "progress": 45,
  "status": "active"
}
```

---

## Testing with Postman

### Setup Postman Environment

1. Create a new environment called "Project Management API"
2. Add variables:
   - `base_url`: `http://localhost:8000`
   - `token`: (leave empty for now)

### Test Flow

1. **Signup/Login**:
   - POST `{{base_url}}/auth/signup`
   - Copy token from response
   - Set `token` variable in environment

2. **Create Project**:
   - POST `{{base_url}}/projects`
   - Headers: `Authorization: Bearer {{token}}`
   - Body: JSON with project details
   - Save `project_id` from response

3. **Get Projects**:
   - GET `{{base_url}}/projects`
   - Headers: `Authorization: Bearer {{token}}`

4. **Update Project**:
   - PUT `{{base_url}}/projects/{{project_id}}`
   - Headers: `Authorization: Bearer {{token}}`
   - Body: JSON with fields to update

5. **Add Team Member**:
   - POST `{{base_url}}/projects/{{project_id}}/team`
   - Headers: `Authorization: Bearer {{token}}`
   - Body: `{"username": "colleague", "role": "developer"}`

6. **Get Statistics**:
   - GET `{{base_url}}/projects/{{project_id}}/stats`
   - Headers: `Authorization: Bearer {{token}}`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid data provided"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authorization header is missing"
}
```

### 403 Forbidden
```json
{
  "detail": "Only project owner can perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Project with id '123...' not found"
}
```

### 409 Conflict
```json
{
  "detail": "User 'john_doe' is already a team member"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database operation failed",
  "message": "Connection timeout"
}
```

---

## Testing Checklist

### Basic CRUD
- [ ] Create a project
- [ ] Get all projects
- [ ] Get single project by ID
- [ ] Update project name
- [ ] Update project status
- [ ] Update project progress
- [ ] Delete project

### Team Management
- [ ] Add team member as owner
- [ ] Try to add duplicate team member (should fail)
- [ ] Get team members list
- [ ] Remove team member as owner
- [ ] Try to add member as non-owner (should fail)

### Authorization
- [ ] Try to access project without token (should fail)
- [ ] Try to update project as non-owner (should fail)
- [ ] Try to delete project as non-owner (should fail)
- [ ] Try to add team member as non-owner (should fail)

### Edge Cases
- [ ] Create project with minimal data (just name)
- [ ] Create project with all fields
- [ ] Update project with empty request body (should fail)
- [ ] Get non-existent project (should fail)
- [ ] Delete non-existent project (should fail)

---

## Interactive API Documentation

Once the server is running, you can test all endpoints interactively:

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

### Using Swagger UI:

1. Click on any endpoint
2. Click "Try it out"
3. For authenticated endpoints:
   - Click the 🔒 lock icon
   - Enter: `Bearer YOUR_TOKEN`
   - Click "Authorize"
4. Fill in parameters/body
5. Click "Execute"
6. View response

---

## Sample Test Scenario

Complete workflow example:

```bash
# 1. Signup
TOKEN=$(curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","email":"admin@example.com"}' \
  | jq -r '.token')

# 2. Create Project
PROJECT_ID=$(curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My First Project","description":"Testing","status":"active"}' \
  | jq -r '.id')

# 3. Get All Projects
curl -X GET "http://localhost:8000/projects" \
  -H "Authorization: Bearer $TOKEN"

# 4. Update Project
curl -X PUT "http://localhost:8000/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"progress":50,"status":"active"}'

# 5. Add Team Member
curl -X POST "http://localhost:8000/projects/$PROJECT_ID/team" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"developer1","role":"developer"}'

# 6. Get Stats
curl -X GET "http://localhost:8000/projects/$PROJECT_ID/stats" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### "Authorization header is missing"
- Make sure you include the `Authorization` header
- Format: `Authorization: Bearer YOUR_TOKEN`

### "Project with id '...' not found"
- Verify the project ID exists
- Check you have access to the project
- Ensure the project wasn't deleted

### "Only project owner can perform this action"
- Only the user who created the project can update/delete it
- Make sure you're authenticated as the correct user

### "Database operation failed"
- Check Supabase credentials in `.env`
- Verify tables are created in Supabase
- Check Supabase project is active

---

## Next Steps

After testing projects API:
1. Create tasks API endpoints
2. Add filtering and sorting to project list
3. Implement search functionality
4. Add pagination for large project lists
5. Create analytics endpoints
6. Build the frontend interface

