"""
Project management API routes.
"""
from fastapi import APIRouter, Depends, status
from typing import List

from models.auth import User, UserResponse
from models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectWithTeam,
    ProjectListResponse, TeamMember, TeamMemberAdd
)
from utils.middleware import get_current_user, verify_auth_token
from utils.supabase_client import get_db, SupabaseDB
from utils.exceptions import (
    ProjectNotFoundException, UnauthorizedAccessException,
    InvalidDataException, DatabaseException
)


# Create router
router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Project doesn't exist"}
    }
)


async def check_project_access(
    project_id: str,
    username: str,
    db: SupabaseDB,
    require_owner: bool = False
) -> dict:
    """
    Check if user has access to a project.
    
    Args:
        project_id: Project UUID
        username: Username to check
        db: Database instance
        require_owner: If True, user must be the owner
        
    Returns:
        Project dictionary
        
    Raises:
        ProjectNotFoundException: If project doesn't exist
        UnauthorizedAccessException: If user doesn't have access
    """
    # Get project
    project = await db.select_by_id("projects", project_id)
    
    if not project:
        raise ProjectNotFoundException(project_id)
    
    # Check if user is owner
    is_owner = project["owner_id"] == username
    
    if require_owner and not is_owner:
        raise UnauthorizedAccessException("Only project owner can perform this action")
    
    # Check if user has access (owner or team member)
    if not is_owner:
        team_members = await db.select_where("team_members", "project_id", project_id)
        is_team_member = any(tm["username"] == username for tm in team_members)
        
        if not is_team_member:
            raise UnauthorizedAccessException("You don't have access to this project")
    
    return project


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project.
    
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **status**: Project status (default: active)
    - **progress**: Project progress 0-100 (default: 0)
    
    Returns the created project with generated ID and timestamps.
    """
    db = get_db()
    
    # Prepare project data
    project_dict = project_data.model_dump()
    project_dict["owner_id"] = current_user.username
    
    # Insert into database
    created_project = await db.insert("projects", project_dict)
    
    return Project(**created_project)


@router.get("", response_model=ProjectListResponse)
async def get_all_projects(
    current_user: User = Depends(get_current_user)
):
    """
    Get all projects for the authenticated user.
    
    Returns projects where the user is either:
    - The project owner
    - A team member
    
    Each project includes its team members and the authenticated user's role in the project.
    """
    from utils.permissions import get_user_role_in_project
    
    db = get_db()
    
    # Get projects owned by user
    owned_projects = await db.select_where("projects", "owner_id", current_user.username)
    
    # Get projects where user is a team member
    team_memberships = await db.select_where("team_members", "username", current_user.username)
    team_project_ids = [tm["project_id"] for tm in team_memberships]
    
    # Get team projects
    team_projects = []
    for project_id in team_project_ids:
        project = await db.select_by_id("projects", project_id)
        if project:
            team_projects.append(project)
    
    # Combine all projects (remove duplicates)
    all_projects = owned_projects + team_projects
    seen_ids = set()
    unique_projects = []
    for project in all_projects:
        if project["id"] not in seen_ids:
            seen_ids.add(project["id"])
            unique_projects.append(project)
    
    # Add team members and user role to each project
    projects_with_teams = []
    for project in unique_projects:
        team_members = await db.select_where("team_members", "project_id", project["id"])
        
        # Get current user's role in this project
        user_role = await get_user_role_in_project(current_user.username, project["id"])
        
        # Create project with additional info
        project_data = {**project, "user_role": user_role}
        project_with_team = ProjectWithTeam(
            **project,
            team_members=[TeamMember(**tm) for tm in team_members]
        )
        projects_with_teams.append(project_with_team)
    
    return ProjectListResponse(
        projects=projects_with_teams,
        total=len(projects_with_teams)
    )


@router.get("/{project_id}", response_model=ProjectWithTeam)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a single project by ID.
    
    Returns full project details including:
    - All team members and their roles
    - Authenticated user's role in the project
    
    User must be either the project owner or a team member.
    """
    from utils.permissions import get_user_role_in_project
    
    db = get_db()
    
    # Check access
    project = await check_project_access(project_id, current_user.username, db)
    
    # Get team members
    team_members = await db.select_where("team_members", "project_id", project_id)
    
    # Get current user's role
    user_role = await get_user_role_in_project(current_user.username, project_id)
    
    # Add user role to response (could extend ProjectWithTeam model to include this)
    project_with_role = {**project, "user_role": user_role}
    
    return ProjectWithTeam(
        **project,
        team_members=[TeamMember(**tm) for tm in team_members]
    )


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a project.
    
    Only the project owner can update the project.
    
    - **name**: New project name (optional)
    - **description**: New description (optional)
    - **status**: New status (optional)
    - **progress**: New progress value (optional)
    
    The `updated_at` timestamp is automatically updated.
    """
    db = get_db()
    
    # Check owner access
    await check_project_access(project_id, current_user.username, db, require_owner=True)
    
    # Get only fields that were provided
    update_data = project_data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise InvalidDataException("No fields to update")
    
    # Update project
    updated_project = await db.update("projects", project_id, update_data)
    
    return Project(**updated_project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project.
    
    Only the project owner can delete the project.
    
    This will also delete:
    - All tasks associated with the project (CASCADE)
    - All team member assignments (CASCADE)
    """
    db = get_db()
    
    # Check owner access
    await check_project_access(project_id, current_user.username, db, require_owner=True)
    
    # Delete project (CASCADE will handle related records)
    await db.delete("projects", project_id)
    
    return None


@router.post("/{project_id}/team", response_model=TeamMember, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    project_id: str,
    team_member: TeamMemberAdd,
    current_user: User = Depends(get_current_user)
):
    """
    Add a team member to a project.
    
    Only the project owner can add team members.
    
    - **username**: Username of the user to add
    - **role**: Role to assign (owner, manager, developer, viewer)
    """
    db = get_db()
    
    # Check owner access
    await check_project_access(project_id, current_user.username, db, require_owner=True)
    
    # Check if user is already a team member
    existing = await db.select_with_filters(
        "team_members",
        {"project_id": project_id, "username": team_member.username}
    )
    
    if existing:
        raise InvalidDataException(f"User '{team_member.username}' is already a team member")
    
    # Add team member
    member_data = {
        "project_id": project_id,
        "username": team_member.username,
        "role": team_member.role
    }
    
    created_member = await db.insert("team_members", member_data)
    
    return TeamMember(**created_member)


@router.delete("/{project_id}/team/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    project_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a team member from a project.
    
    Only the project owner can remove team members.
    """
    db = get_db()
    
    # Check owner access
    await check_project_access(project_id, current_user.username, db, require_owner=True)
    
    # Delete team member
    await db.delete("team_members", member_id)
    
    return None


@router.get("/{project_id}/team", response_model=List[TeamMember])
async def get_team_members(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all team members for a project.
    
    User must have access to the project.
    """
    db = get_db()
    
    # Check access
    await check_project_access(project_id, current_user.username, db)
    
    # Get team members
    team_members = await db.select_where("team_members", "project_id", project_id)
    
    return [TeamMember(**tm) for tm in team_members]


@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics for a project.
    
    Returns:
    - Total tasks
    - Tasks by status
    - Tasks by priority
    - Team member count
    - Project progress
    """
    db = get_db()
    
    # Check access
    project = await check_project_access(project_id, current_user.username, db)
    
    # Get all tasks
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    # Count tasks by status
    status_counts = {
        "todo": 0,
        "in_progress": 0,
        "completed": 0
    }
    
    # Count tasks by priority
    priority_counts = {
        "low": 0,
        "medium": 0,
        "high": 0
    }
    
    for task in tasks:
        status = task.get("status", "todo")
        priority = task.get("priority", "medium")
        
        if status in status_counts:
            status_counts[status] += 1
        if priority in priority_counts:
            priority_counts[priority] += 1
    
    # Get team member count
    team_members = await db.select_where("team_members", "project_id", project_id)
    
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "total_tasks": len(tasks),
        "tasks_by_status": status_counts,
        "tasks_by_priority": priority_counts,
        "team_member_count": len(team_members),
        "progress": project["progress"],
        "status": project["status"]
    }

