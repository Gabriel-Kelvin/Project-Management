"""
Dashboard API routes for user overview and summary.
"""
from fastapi import APIRouter, Depends
from typing import List, Dict

from models.auth import User
from utils.middleware import get_current_user
from utils.supabase_client import get_db, SupabaseDB
from utils.permissions import get_user_role_in_project
from utils.analytics import get_user_all_tasks, get_user_statistics


# Create router
router = APIRouter(
    tags=["Dashboard"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"}
    }
)


@router.get("/dashboard")
async def get_user_dashboard(current_user: User = Depends(get_current_user)):
    """
    Get comprehensive dashboard overview for authenticated user.
    
    Returns:
    - User's projects with progress and role
    - Tasks assigned to user across all projects
    - Overall statistics
    
    This endpoint provides everything needed for a user's dashboard view.
    """
    db: SupabaseDB = get_db()
    
    # Get projects where user is owner
    owned_projects = await db.select_where("projects", "owner_id", current_user.username)
    
    # Get projects where user is team member
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
    
    # Enrich projects with additional info
    user_projects = []
    for project in unique_projects:
        project_id = project["id"]
        
        # Get user's role in this project
        user_role = await get_user_role_in_project(current_user.username, project_id)
        
        # Get team size
        team_members = await db.select_where("team_members", "project_id", project_id)
        team_size = len(team_members) + 1  # +1 for owner
        
        # Get task count
        tasks = await db.select_where("tasks", "project_id", project_id)
        task_count = len(tasks)
        
        user_projects.append({
            "id": project_id,
            "name": project.get("name"),
            "progress": project.get("progress", 0),
            "role": user_role,
            "team_size": team_size,
            "task_count": task_count,
            "status": project.get("status"),
            "description": project.get("description")
        })
    
    # Get all tasks assigned to user
    my_tasks_raw = await get_user_all_tasks(current_user.username)
    
    # Format tasks for dashboard
    my_tasks = []
    for task in my_tasks_raw:
        my_tasks.append({
            "id": task.get("id"),
            "title": task.get("title"),
            "status": task.get("status"),
            "priority": task.get("priority"),
            "project_id": task.get("project_id"),
            "project_name": task.get("project_name"),
            "description": task.get("description"),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at")
        })
    
    # Get user statistics
    statistics = await get_user_statistics(current_user.username)
    
    return {
        "user_projects": user_projects,
        "my_tasks": my_tasks,
        "statistics": statistics
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    """
    Get quick summary statistics for user dashboard.
    
    Returns condensed version with just the key metrics.
    """
    # Get user statistics
    statistics = await get_user_statistics(current_user.username)
    
    return {
        "username": current_user.username,
        "email": current_user.email,
        **statistics
    }


@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get recent activity for the user.
    
    Query Parameters:
    - limit: Number of recent items to return (default: 10)
    
    Returns recently updated tasks and projects.
    """
    db: SupabaseDB = get_db()
    
    # Get user's projects
    owned_projects = await db.select_where("projects", "owner_id", current_user.username)
    team_memberships = await db.select_where("team_members", "username", current_user.username)
    
    all_project_ids = set([p["id"] for p in owned_projects])
    all_project_ids.update([tm["project_id"] for tm in team_memberships])
    
    # Get recent tasks from user's projects
    recent_tasks = []
    for project_id in all_project_ids:
        tasks = await db.select_where("tasks", "project_id", project_id)
        recent_tasks.extend(tasks)
    
    # Sort by updated_at and limit
    recent_tasks.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    recent_tasks = recent_tasks[:limit]
    
    # Format activity
    activity = []
    for task in recent_tasks:
        project = await db.select_by_id("projects", task.get("project_id"))
        activity.append({
            "type": "task_updated",
            "task_id": task.get("id"),
            "task_title": task.get("title"),
            "task_status": task.get("status"),
            "project_id": task.get("project_id"),
            "project_name": project.get("name") if project else "Unknown",
            "updated_at": task.get("updated_at")
        })
    
    return {
        "recent_activity": activity,
        "count": len(activity)
    }

