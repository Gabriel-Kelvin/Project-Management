# Supabase Database Schema Setup

This document outlines the database schema needed for the Project Management application. Create these tables in your Supabase dashboard.

## Prerequisites

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project or select an existing one
3. Navigate to the SQL Editor

## Database Tables

### 1. Projects Table

Stores information about projects.

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    owner_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    start_date DATE,
    end_date DATE,
    color VARCHAR(7) DEFAULT '#3B82F6'
);

-- Create index for faster queries
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Enable Row Level Security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
```

**Fields:**
- `id`: Unique project identifier (UUID)
- `name`: Project name
- `description`: Detailed project description
- `status`: Project status (active, completed, archived)
- `owner_id`: ID of the user who owns the project
- `created_at`: Project creation timestamp
- `updated_at`: Last update timestamp
- `start_date`: Project start date
- `end_date`: Project end date
- `color`: Color code for project display

---

### 2. Tasks Table

Stores tasks associated with projects.

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo',
    priority VARCHAR(50) DEFAULT 'medium',
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for faster queries
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Enable Row Level Security
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
```

**Fields:**
- `id`: Unique task identifier (UUID)
- `title`: Task title
- `description`: Detailed task description
- `status`: Task status (todo, in_progress, review, completed)
- `priority`: Task priority (low, medium, high, urgent)
- `project_id`: Reference to the parent project
- `assigned_to`: ID of the user assigned to this task
- `created_by`: ID of the user who created the task
- `created_at`: Task creation timestamp
- `updated_at`: Last update timestamp
- `due_date`: Task due date
- `completed_at`: Task completion timestamp

---

### 3. Team Members Table

Stores team members associated with projects.

```sql
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    role_id UUID REFERENCES roles(id),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

-- Create indexes for faster queries
CREATE INDEX idx_team_members_project_id ON team_members(project_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
CREATE INDEX idx_team_members_role_id ON team_members(role_id);

-- Enable Row Level Security
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
```

**Fields:**
- `id`: Unique team member record identifier (UUID)
- `project_id`: Reference to the project
- `user_id`: ID of the user (from authentication system)
- `role_id`: Reference to the user's role in the project
- `joined_at`: When the user joined the project

**Constraints:**
- Unique constraint on (project_id, user_id) to prevent duplicate memberships

---

### 4. Roles Table

Defines roles for team members in projects.

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_roles_name ON roles(name);

-- Enable Row Level Security
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;

-- Insert default roles
INSERT INTO roles (name, description, permissions) VALUES
    ('Owner', 'Full control over the project', '["read", "write", "delete", "manage_members", "manage_settings"]'),
    ('Admin', 'Can manage project and members', '["read", "write", "delete", "manage_members"]'),
    ('Member', 'Can view and edit project content', '["read", "write"]'),
    ('Viewer', 'Can only view project content', '["read"]');
```

**Fields:**
- `id`: Unique role identifier (UUID)
- `name`: Role name (Owner, Admin, Member, Viewer)
- `description`: Role description
- `permissions`: JSON array of permissions
- `created_at`: Role creation timestamp

**Default Roles:**
- **Owner**: Full control over the project
- **Admin**: Can manage project and members
- **Member**: Can view and edit project content
- **Viewer**: Can only view project content

---

## Additional Useful Tables (Optional)

### 5. Comments Table

Store comments on tasks.

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);

ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
```

### 6. Activity Log Table

Track all activities in projects.

```sql
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_log_project_id ON activity_log(project_id);
CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);

ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
```

---

## Row Level Security (RLS) Policies

After creating the tables, you'll need to set up RLS policies. Here are basic examples:

### Projects Policies

```sql
-- Allow users to read projects they own or are members of
CREATE POLICY "Users can view their projects"
ON projects FOR SELECT
USING (
    owner_id = current_setting('app.user_id', true)::VARCHAR
    OR id IN (
        SELECT project_id FROM team_members 
        WHERE user_id = current_setting('app.user_id', true)::VARCHAR
    )
);

-- Allow users to create projects
CREATE POLICY "Users can create projects"
ON projects FOR INSERT
WITH CHECK (owner_id = current_setting('app.user_id', true)::VARCHAR);

-- Allow owners to update their projects
CREATE POLICY "Owners can update their projects"
ON projects FOR UPDATE
USING (owner_id = current_setting('app.user_id', true)::VARCHAR);

-- Allow owners to delete their projects
CREATE POLICY "Owners can delete their projects"
ON projects FOR DELETE
USING (owner_id = current_setting('app.user_id', true)::VARCHAR);
```

### Tasks Policies

```sql
-- Allow users to view tasks in their projects
CREATE POLICY "Users can view tasks in their projects"
ON tasks FOR SELECT
USING (
    project_id IN (
        SELECT id FROM projects 
        WHERE owner_id = current_setting('app.user_id', true)::VARCHAR
        OR id IN (
            SELECT project_id FROM team_members 
            WHERE user_id = current_setting('app.user_id', true)::VARCHAR
        )
    )
);

-- Allow users to create tasks in their projects
CREATE POLICY "Users can create tasks in their projects"
ON tasks FOR INSERT
WITH CHECK (
    project_id IN (
        SELECT id FROM projects 
        WHERE owner_id = current_setting('app.user_id', true)::VARCHAR
        OR id IN (
            SELECT project_id FROM team_members 
            WHERE user_id = current_setting('app.user_id', true)::VARCHAR
        )
    )
);
```

---

## Setup Instructions

1. **Open Supabase SQL Editor**
   - Go to your Supabase project dashboard
   - Click on "SQL Editor" in the left sidebar

2. **Create Tables**
   - Copy and paste each CREATE TABLE statement
   - Execute them in order (roles → projects → tasks → team_members)

3. **Set Up RLS Policies**
   - Copy and paste the RLS policy statements
   - Execute them after all tables are created

4. **Verify Setup**
   - Check the "Table Editor" to see all tables
   - Verify the columns and relationships

---

## Notes

- **User IDs**: The authentication system uses in-memory storage with user IDs like `user_abc123`. These IDs are stored as VARCHAR in Supabase tables.
- **Row Level Security**: RLS policies use `current_setting('app.user_id', true)` which you'll set in your application code when making Supabase queries.
- **Timestamps**: All timestamps use `TIMESTAMP WITH TIME ZONE` for proper timezone handling.
- **UUIDs**: Primary keys use UUID v4 for better distribution and security.

---

## Migration to Production

When moving to production:

1. Consider using a proper authentication system (e.g., Supabase Auth)
2. Hash passwords instead of storing plain text
3. Implement proper session management
4. Add more comprehensive RLS policies
5. Set up database backups
6. Monitor database performance and add indexes as needed

