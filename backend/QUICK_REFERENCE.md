# Quick Reference Guide - Project Management API

## 🚀 **Quick Start**

```bash
# Start server
cd backend
python run.py

# Server running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## 📊 **All 29 Endpoints**

### **Authentication (5)**
```
POST   /auth/signup         - Register
POST   /auth/login          - Login
POST   /auth/logout         - Logout
GET    /auth/verify         - Verify token
GET    /auth/me             - Get current user
```

### **Projects (6)**
```
POST   /projects            - Create project
GET    /projects            - Get all projects
GET    /projects/{id}       - Get project
PUT    /projects/{id}       - Update project
DELETE /projects/{id}       - Delete project
GET    /projects/{id}/stats - Project statistics
```

### **Tasks (6)**
```
POST   /projects/{id}/tasks                  - Create task
GET    /projects/{id}/tasks                  - Get all tasks
GET    /projects/{id}/tasks/{tid}            - Get task
PUT    /projects/{id}/tasks/{tid}            - Update task (auto-progress ✨)
PATCH  /projects/{id}/tasks/{tid}/status     - Update status (auto-progress ✨)
DELETE /projects/{id}/tasks/{tid}            - Delete task
```

### **Team Members (6)**
```
POST   /projects/{id}/members                      - Add member
GET    /projects/{id}/members                      - Get all members
GET    /projects/{id}/members/{user}               - Get member
PUT    /projects/{id}/members/{user}               - Update role
DELETE /projects/{id}/members/{user}               - Remove member
GET    /projects/{id}/members/{user}/permissions   - Get permissions
```

### **Analytics (3)**
```
GET    /projects/{id}/analytics                  - Project analytics
GET    /projects/{id}/analytics/timeline         - Progress timeline
GET    /projects/{id}/analytics/member/{user}    - Member analytics
```

### **Dashboard (3)**
```
GET    /dashboard                    - User dashboard
GET    /dashboard/summary            - Quick summary
GET    /dashboard/recent-activity    - Recent activity
```

---

## 🔐 **Permission Matrix**

| Action | Owner | Manager | Developer | Viewer |
|--------|:-----:|:-------:|:---------:|:------:|
| Create Project | ✅ | ❌ | ❌ | ❌ |
| Edit Project | ✅ | ✅ | ❌ | ❌ |
| Delete Project | ✅ | ❌ | ❌ | ❌ |
| Create Task | ✅ | ✅ | ✅ | ❌ |
| Edit Own Task | ✅ | ✅ | ✅ | ❌ |
| Edit Any Task | ✅ | ✅ | ❌ | ❌ |
| Delete Task | ✅ | ✅ | ❌ | ❌ |
| Add Member | ✅ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ❌ | ❌ |

---

## 📝 **Quick Test**

```bash
# 1. Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123","email":"john@example.com"}'

# Save token as: TOKEN="your_token_here"

# 2. Create Project
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"Test"}'

# Save project_id as: PROJECT_ID="project_id_here"

# 3. Create Task
curl -X POST http://localhost:8000/projects/$PROJECT_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Task","priority":"high"}'

# Save task_id as: TASK_ID="task_id_here"

# 4. Complete Task (Watch progress update! ✨)
curl -X PATCH http://localhost:8000/projects/$PROJECT_ID/tasks/$TASK_ID/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'

# 5. Get Analytics
curl -X GET http://localhost:8000/projects/$PROJECT_ID/analytics \
  -H "Authorization: Bearer $TOKEN"

# 6. Get Dashboard
curl -X GET http://localhost:8000/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 **Key Features**

### **1. Auto-Progress Tracking ✨**
```python
# When you update task status:
PATCH /projects/{id}/tasks/{tid}/status

# Progress automatically recalculates:
progress = (completed_tasks / total_tasks) * 100
```

### **2. Comprehensive Analytics**
```python
GET /projects/{id}/analytics

# Returns:
- Total tasks, completed, in progress, todo
- Overall progress (auto-calculated)
- Team size
- Tasks by priority (high/medium/low)
- Tasks by status (todo/in_progress/completed)
- Team productivity (per member)
```

### **3. User Dashboard**
```python
GET /dashboard

# Returns:
- All user's projects (with roles)
- All assigned tasks (across all projects)
- Statistics (projects, tasks, completion rate)
```

---

## 🔧 **File Structure**

```
backend/
├── app/
│   └── main.py                    # FastAPI app + routes
├── routes/
│   ├── auth.py                    # Authentication (5 endpoints)
│   ├── projects.py                # Projects (6 endpoints)
│   ├── tasks.py                   # Tasks (6 endpoints)
│   ├── roles.py                   # Team members (6 endpoints)
│   ├── analytics.py               # Analytics (3 endpoints)
│   └── dashboard.py               # Dashboard (3 endpoints)
├── models/
│   ├── auth.py                    # User models
│   ├── project.py                 # Project/Task models
│   └── role.py                    # Role models
├── utils/
│   ├── analytics.py               # ✨ Progress tracking
│   ├── config.py                  # Supabase config
│   ├── supabase_client.py         # DB wrapper
│   ├── permissions.py             # Role permissions
│   ├── middleware.py              # Auth middleware
│   ├── exceptions.py              # Custom exceptions
│   ├── logger.py                  # ✨ Logging system
│   └── response.py                # ✨ Standardized responses
├── sql/
│   └── create_tables.sql          # Database schema
├── run.py                         # Server starter
└── .env                           # Supabase credentials
```

---

## 📚 **Documentation**

| File | Purpose |
|------|---------|
| `BACKEND_FINALIZED.md` | Complete summary |
| `COMPLETE_BACKEND_TESTING.md` | Full testing guide |
| `QUICK_REFERENCE.md` | This file |
| `README.md` | Backend overview |
| `SETUP_SUPABASE.md` | Database setup |

---

## 🎊 **What's New in This Version**

### **Prompt 4 Additions:**

1. ✨ **Auto-Progress Tracking**
   - Calculates on task status change
   - Updates project table automatically
   - Handles edge cases (0 tasks)

2. 📊 **Analytics Routes (3 new endpoints)**
   - Project analytics
   - Progress timeline
   - Member analytics

3. 📈 **Dashboard Routes (3 new endpoints)**
   - Complete user overview
   - Quick summary
   - Recent activity

4. 📝 **Logging System**
   - Track all user actions
   - System event logging
   - Console output with emojis

5. 🎯 **Standardized Responses**
   - Consistent format
   - Helper functions
   - Timestamp on all responses

6. 💾 **Enhanced Database**
   - Aggregation queries
   - Count with filters
   - Join support

---

## ⚡ **Pro Tips**

### **Testing with Swagger UI**
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer your_token_here`
4. All endpoints now authenticated!

### **Checking Logs**
- All actions logged to console
- Look for emoji indicators:
  - ✅ Success operations
  - 🔄 Status changes
  - 👥 Team changes
  - ❌ Errors
  - 🚫 Permission denials

### **Progress Tracking**
- Progress updates automatically when task status changes
- No need to manually calculate
- Check `project.progress` field or analytics endpoint

---

## 🐛 **Troubleshooting**

### **Issue: 401 Unauthorized**
```bash
# Solution: Include Authorization header
-H "Authorization: Bearer $TOKEN"
```

### **Issue: 403 Forbidden**
```bash
# Solution: Check user role
# Viewers can't create/edit
# Developers can only edit own tasks
# Managers can't add/remove members
# Only owners can delete projects
```

### **Issue: Progress not updating**
```bash
# Solution: Make sure you're updating status
PATCH /projects/{id}/tasks/{tid}/status
# Not just any field update
```

### **Issue: Can't see analytics**
```bash
# Solution: Only owners and managers can view analytics
# Make sure user has correct role
```

---

## 🎯 **Common Workflows**

### **Complete Project Setup**
```bash
1. Signup users (owner, manager, developer, viewer)
2. Owner creates project
3. Owner adds team members
4. Manager/Developer creates tasks
5. Team members update task status
6. Check analytics for progress
7. View dashboard for overview
```

### **Task Management**
```bash
1. Create task with priority
2. Assign to team member
3. Member updates status to "in_progress"
4. Member completes task
5. Progress automatically updates ✨
6. Check analytics to see impact
```

### **Team Collaboration**
```bash
1. Owner adds members with roles
2. Managers assign tasks
3. Developers work on tasks
4. Viewers monitor progress
5. Owner/Manager checks analytics
6. Everyone views their dashboard
```

---

## 🚀 **Ready to Build Frontend?**

Your backend provides everything needed:
- ✅ User authentication
- ✅ Project management
- ✅ Task tracking with auto-progress
- ✅ Team collaboration
- ✅ Analytics & insights
- ✅ User dashboard
- ✅ Role-based permissions

**Next:** Build a React frontend to consume these 29 endpoints!

---

**Happy Coding! 🎉**

