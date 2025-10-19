# Supabase Setup Guide

Step-by-step guide to set up your Supabase database for the Project Management API.

## 📋 Prerequisites

- A Supabase account (free tier works fine)
- Your `.env` file configured with Supabase credentials

---

## Step 1: Create a Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in:
   - **Name**: Project Management App (or your choice)
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to you
4. Click "Create new project"
5. Wait for the project to be created (~2 minutes)

---

## Step 2: Get Your API Credentials

1. In your Supabase project dashboard, go to **Settings** (gear icon in sidebar)
2. Click **API** in the settings menu
3. You'll see two important values:

### Project URL
```
https://xxxxxxxxxxxxx.supabase.co
```
Copy this to your `.env` file as `SUPABASE_URL`

### API Keys
- **anon/public key**: Copy to `.env` as `SUPABASE_KEY`
- **service_role key**: Copy to `.env` as `SUPABASE_SERVICE_ROLE_KEY`

Your `.env` should look like:
```env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## Step 3: Create Database Tables

1. In your Supabase project, click **SQL Editor** in the sidebar
2. Click **New query**
3. Copy the entire contents of `sql/create_tables.sql`
4. Paste into the SQL editor
5. Click **Run** or press `Ctrl+Enter`

You should see:
```
Success. No rows returned
```

---

## Step 4: Verify Tables Were Created

### Check Tables
1. Click **Table Editor** in sidebar
2. You should see 4 tables:
   - `projects`
   - `tasks`
   - `team_members`
   - `roles`

### Verify Roles Data
1. Click on the `roles` table
2. You should see 4 default roles:
   - owner
   - manager
   - developer
   - viewer

---

## Step 5: Test the Connection

1. Start your backend server:
   ```bash
   cd backend
   python run.py
   ```

2. The server should start without errors

3. If you see connection errors:
   - Check your `.env` file
   - Verify credentials are correct
   - Ensure Supabase project is active

---

## Step 6: Test Database Operations

### Create a test project via API:

```bash
# 1. First, get an auth token (signup/login)
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123",
    "email": "test@example.com"
  }'

# 2. Use the token to create a project
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Testing Supabase connection"
  }'
```

### Verify in Supabase:
1. Go to **Table Editor**
2. Click on `projects` table
3. You should see your test project!

---

## Table Schemas Reference

### Projects Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| name | TEXT | Project name |
| description | TEXT | Project description |
| owner_id | TEXT | Username of project owner |
| status | TEXT | active, completed, or on_hold |
| progress | INTEGER | 0-100 |
| created_at | TIMESTAMP | Auto-set on creation |
| updated_at | TIMESTAMP | Auto-updated on changes |

### Tasks Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| project_id | UUID | Foreign key to projects |
| title | TEXT | Task title |
| description | TEXT | Task description |
| assigned_to | TEXT | Username assigned to |
| status | TEXT | todo, in_progress, completed |
| priority | TEXT | low, medium, high |
| created_at | TIMESTAMP | Auto-set on creation |
| updated_at | TIMESTAMP | Auto-updated on changes |

### Team Members Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| project_id | UUID | Foreign key to projects |
| username | TEXT | Username of team member |
| role | TEXT | owner, manager, developer, viewer |
| assigned_at | TIMESTAMP | When member was added |

### Roles Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| role_name | TEXT | Unique role name |
| permissions | JSONB | Array of permission strings |

---

## Database Features

### Automatic Timestamps
- `created_at` is automatically set when a record is created
- `updated_at` is automatically updated when a record is modified
- Uses PostgreSQL triggers (already configured)

### Cascade Deletes
When a project is deleted:
- All tasks for that project are deleted
- All team member assignments are deleted
- This is handled by PostgreSQL `ON DELETE CASCADE`

### Constraints
- Project status must be: active, completed, or on_hold
- Task status must be: todo, in_progress, or completed
- Task priority must be: low, medium, or high
- Team member role must be: owner, manager, developer, or viewer
- Progress must be between 0 and 100
- Each user can only be added once per project (unique constraint)

---

## Optional: Row Level Security (RLS)

For production, you may want to enable Row Level Security:

```sql
-- Enable RLS on projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create policy for users to see their own projects
CREATE POLICY "Users can view their projects"
ON projects FOR SELECT
USING (
  owner_id = current_setting('request.jwt.claims', true)::json->>'username'
  OR id IN (
    SELECT project_id FROM team_members 
    WHERE username = current_setting('request.jwt.claims', true)::json->>'username'
  )
);
```

Note: RLS is optional for development but recommended for production.

---

## Troubleshooting

### "Failed to insert record"
- Check table schema matches the data being inserted
- Verify all required fields are provided
- Check for constraint violations (e.g., invalid status value)

### "Connection timeout"
- Verify your Supabase project is active
- Check your API keys are correct
- Ensure your internet connection is stable

### "Project not found in Supabase dashboard"
- Make sure you're looking at the correct project
- Check the region (should match where you created it)
- Refresh the page

### "Duplicate key violation"
- You're trying to add a team member who's already on the project
- Check the unique constraints on your tables

---

## Database Management

### Backup Your Data
Supabase automatically backs up your database, but you can also:
1. Go to **Database** > **Backups** in Supabase dashboard
2. Click "Download backup" to get a copy

### View Database Logs
1. Go to **Database** > **Logs**
2. View real-time database queries and errors

### Monitor Performance
1. Go to **Database** > **Reports**
2. View query performance and usage statistics

---

## Next Steps

✅ Tables created
✅ Connection tested
✅ Test data inserted

Now you can:
1. Test all API endpoints (see `PROJECTS_API_TESTING.md`)
2. Build your frontend
3. Add more features (tasks, comments, etc.)

---

## Useful SQL Queries

### View all projects
```sql
SELECT * FROM projects ORDER BY created_at DESC;
```

### View projects with team member count
```sql
SELECT 
  p.*,
  COUNT(tm.id) as team_size
FROM projects p
LEFT JOIN team_members tm ON p.id = tm.project_id
GROUP BY p.id;
```

### View projects with task statistics
```sql
SELECT 
  p.name,
  COUNT(t.id) as total_tasks,
  COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
  COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) as in_progress_tasks
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, p.name;
```

### Delete test data
```sql
-- Delete all projects (will cascade to tasks and team_members)
DELETE FROM projects WHERE owner_id = 'testuser';
```

---

**✨ Your Supabase database is now ready to use!**

