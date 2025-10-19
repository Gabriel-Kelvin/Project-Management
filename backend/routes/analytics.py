"""
Analytics API routes for project metrics and insights.
"""
from fastapi import APIRouter, Depends, status

from models.auth import User
from utils.middleware import get_current_user
from utils.supabase_client import get_db, SupabaseDB
from utils.permissions import get_user_role_in_project, check_permission, Permission
from utils.exceptions import (
    ProjectNotFoundException, UnauthorizedAccessException,
    InsufficientPermissionsException
)
from utils.analytics import (
    calculate_task_completion_rate, get_tasks_by_priority,
    get_team_productivity, get_project_timeline, get_member_analytics
)


# Create router
router = APIRouter(
    prefix="/projects/{project_id}/analytics",
    tags=["Analytics"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Project doesn't exist"}
    }
)


async def verify_analytics_access(project_id: str, username: str) -> None:
    """
    Verify user has access to analytics (owner or manager).
    
    Args:
        project_id: Project UUID
        username: Username to check
        
    Raises:
        ProjectNotFoundException: If project doesn't exist
        InsufficientPermissionsException: If user lacks permission
    """
    db: SupabaseDB = get_db()
    
    # Check if project exists
    project = await db.select_by_id("projects", project_id)
    if not project:
        raise ProjectNotFoundException(project_id)
    
    # Get user's role
    user_role = await get_user_role_in_project(username, project_id)
    
    # Check if user has VIEW_ANALYTICS permission
    if not check_permission(user_role, Permission.VIEW_ANALYTICS):
        raise InsufficientPermissionsException("view analytics (owner or manager only)")


@router.get("")
async def get_project_analytics(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive project analytics.
    
    Returns:
    - Project overview (name, progress)
    - Task counts by status and priority
    - Team size and productivity metrics
    - Overall project health indicators
    
    Only accessible to project owners and managers.
    """
    # Verify access
    await verify_analytics_access(project_id, current_user.username)
    
    db: SupabaseDB = get_db()
    
    # Get project details
    project = await db.select_by_id("projects", project_id)
    
    # Get task completion rate
    task_completion = await calculate_task_completion_rate(project_id)
    
    # Get tasks by priority
    tasks_by_priority = await get_tasks_by_priority(project_id)
    
    # Get team size
    team_members = await db.select_where("team_members", "project_id", project_id)
    team_size = len(team_members) + 1  # +1 for owner
    
    # Get team productivity
    team_productivity = await get_team_productivity(project_id)
    
    return {
        "project_id": project_id,
        "project_name": project.get("name"),
        "total_tasks": task_completion["total_tasks"],
        "completed_tasks": task_completion["completed_tasks"],
        "in_progress_tasks": task_completion["in_progress_tasks"],
        "todo_tasks": task_completion["todo_tasks"],
        "overall_progress": project.get("progress", 0),
        "team_size": team_size,
        "tasks_by_priority": tasks_by_priority,
        "tasks_by_status": {
            "todo": task_completion["todo_tasks"],
            "in_progress": task_completion["in_progress_tasks"],
            "completed": task_completion["completed_tasks"]
        },
        "team_productivity": team_productivity
    }


@router.get("/timeline")
async def get_analytics_timeline(
    project_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """
    Get project progress over time.
    
    Returns completion data grouped by date for the last N days.
    
    Query Parameters:
    - days: Number of days to look back (default: 30)
    
    Only accessible to project owners and managers.
    """
    # Verify access
    await verify_analytics_access(project_id, current_user.username)
    
    # Get timeline data
    timeline = await get_project_timeline(project_id, days)
    
    return timeline


@router.get("/member/{username}")
async def get_member_analytics_endpoint(
    project_id: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics for a specific team member.
    
    Returns:
    - Member's task distribution
    - Completion rate
    - Work progress metrics
    
    Accessible to:
    - Project owners
    - Managers
    - The member themselves
    """
    db: SupabaseDB = get_db()
    
    # Check if project exists
    project = await db.select_by_id("projects", project_id)
    if not project:
        raise ProjectNotFoundException(project_id)
    
    # Get current user's role
    user_role = await get_user_role_in_project(current_user.username, project_id)
    
    # Check access: owner, manager, or the member themselves
    is_owner_or_manager = check_permission(user_role, Permission.VIEW_ANALYTICS)
    is_self = current_user.username == username
    
    if not (is_owner_or_manager or is_self):
        raise InsufficientPermissionsException(
            "view member analytics (owner, manager, or self only)"
        )
    
    # Get member analytics
    analytics = await get_member_analytics(project_id, username)
    
    return analytics

