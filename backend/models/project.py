"""
Project-related models and schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enum."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class TeamMemberRole(str, Enum):
    """Team member role enum."""
    OWNER = "owner"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class ProjectCreate(BaseModel):
    """Model for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    progress: int = Field(default=0, ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Website Redesign",
                "description": "Complete redesign of company website",
                "status": "active",
                "progress": 0
            }
        }


class ProjectUpdate(BaseModel):
    """Model for updating an existing project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Website Redesign v2",
                "description": "Updated description",
                "status": "in_progress",
                "progress": 45
            }
        }


class Project(BaseModel):
    """Model for project response."""
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Website Redesign",
                "description": "Complete redesign of company website",
                "owner_id": "testuser",
                "status": "active",
                "progress": 0,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class TeamMember(BaseModel):
    """Model for team member."""
    id: str
    project_id: str
    username: str
    role: str
    assigned_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "role": "developer",
                "assigned_at": "2024-01-01T00:00:00Z"
            }
        }


class TeamMemberAdd(BaseModel):
    """Model for adding a team member."""
    username: str = Field(..., min_length=1)
    role: TeamMemberRole = TeamMemberRole.DEVELOPER
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "role": "developer"
            }
        }


class ProjectWithTeam(Project):
    """Model for project with team members."""
    team_members: List[TeamMember] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Website Redesign",
                "description": "Complete redesign of company website",
                "owner_id": "testuser",
                "status": "active",
                "progress": 0,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "team_members": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "project_id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "john_doe",
                        "role": "developer",
                        "assigned_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }


class ProjectListResponse(BaseModel):
    """Model for list of projects response."""
    projects: List[ProjectWithTeam]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "projects": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Website Redesign",
                        "description": "Complete redesign",
                        "owner_id": "testuser",
                        "status": "active",
                        "progress": 0,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "team_members": []
                    }
                ],
                "total": 1
            }
        }


class TaskStatus(str, Enum):
    """Task status enum."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    """Model for creating a new task."""
    project_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Design homepage mockup",
                "description": "Create mockup for new homepage design",
                "assigned_to": "john_doe",
                "status": "todo",
                "priority": "high"
            }
        }


class TaskUpdate(BaseModel):
    """Model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated task title",
                "description": "Updated description",
                "assigned_to": "jane_doe",
                "status": "in_progress",
                "priority": "high"
            }
        }


class TaskStatusUpdate(BaseModel):
    """Model for updating only task status."""
    status: TaskStatus
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "in_progress"
            }
        }


class Task(BaseModel):
    """Model for task response."""
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Design homepage mockup",
                "description": "Create mockup for new homepage design",
                "assigned_to": "john_doe",
                "status": "todo",
                "priority": "high",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class TaskListResponse(BaseModel):
    """Model for list of tasks response."""
    tasks: List[Task]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "project_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Design homepage mockup",
                        "description": "Create mockup",
                        "assigned_to": "john_doe",
                        "status": "todo",
                        "priority": "high",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1
            }
        }

