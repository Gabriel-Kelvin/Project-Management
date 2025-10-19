"""
Helper functions for various operations.
"""
from datetime import datetime
from typing import Optional
from utils.supabase_client import get_db, SupabaseDB


async def log_task_assignment(
    task_id: str,
    assigned_to: str,
    assigned_by: str,
    project_id: str
) -> None:
    """
    Log task assignment for tracking purposes.
    
    This creates a simple log that can be used by the frontend
    to show notifications and track assignment history.
    
    Args:
        task_id: UUID of the task
        assigned_to: Username of the assignee
        assigned_by: Username who made the assignment
        project_id: UUID of the project
    """
    # For now, this is a placeholder function that could log to a separate table
    # or tracking system in the future
    
    # You could create an "activity_log" or "task_assignments" table to track this
    # For now, we'll just pass - the assignment is stored in the task itself
    
    # Future enhancement: Store in activity_log table
    # activity_data = {
    #     "project_id": project_id,
    #     "task_id": task_id,
    #     "action": "task_assigned",
    #     "actor": assigned_by,
    #     "target_user": assigned_to,
    #     "timestamp": datetime.now().isoformat()
    # }
    # db = get_db()
    # await db.insert("activity_log", activity_data)
    
    pass


async def log_project_activity(
    project_id: str,
    user: str,
    action: str,
    details: Optional[dict] = None
) -> None:
    """
    Log project activity for audit trail.
    
    Args:
        project_id: UUID of the project
        user: Username who performed the action
        action: Action performed (e.g., "created_task", "updated_project")
        details: Additional details about the action
    """
    # Placeholder for activity logging
    # Future: Store in activity_log table
    pass


async def send_task_notification(
    task_id: str,
    recipient_username: str,
    notification_type: str,
    message: str
) -> None:
    """
    Send notification to a user about a task.
    
    This is a placeholder for future notification system.
    Could integrate with:
    - Email
    - WebSocket for real-time notifications
    - Push notifications
    - In-app notification center
    
    Args:
        task_id: UUID of the task
        recipient_username: Username to notify
        notification_type: Type of notification (e.g., "assigned", "status_changed")
        message: Notification message
    """
    # Placeholder for notification system
    # Future: Store in notifications table or send via external service
    pass


def format_task_summary(task: dict) -> str:
    """
    Format a task into a human-readable summary.
    
    Args:
        task: Task dictionary
        
    Returns:
        Formatted task summary
    """
    title = task.get("title", "Untitled")
    status = task.get("status", "unknown")
    priority = task.get("priority", "medium")
    assigned_to = task.get("assigned_to", "unassigned")
    
    return f"Task '{title}' [{status}] - Priority: {priority}, Assigned to: {assigned_to}"


def format_project_summary(project: dict) -> str:
    """
    Format a project into a human-readable summary.
    
    Args:
        project: Project dictionary
        
    Returns:
        Formatted project summary
    """
    name = project.get("name", "Untitled")
    status = project.get("status", "unknown")
    progress = project.get("progress", 0)
    owner = project.get("owner_id", "unknown")
    
    return f"Project '{name}' [{status}] - {progress}% complete, Owner: {owner}"


async def calculate_project_progress(project_id: str) -> int:
    """
    Calculate project progress based on completed tasks.
    
    Args:
        project_id: UUID of the project
        
    Returns:
        Progress percentage (0-100)
    """
    db: SupabaseDB = get_db()
    
    # Get all tasks for the project
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    if not tasks or len(tasks) == 0:
        return 0
    
    # Count completed tasks
    completed = sum(1 for task in tasks if task.get("status") == "completed")
    
    # Calculate percentage
    progress = int((completed / len(tasks)) * 100)
    
    return progress


async def get_user_task_count(username: str, project_id: Optional[str] = None) -> dict:
    """
    Get task count for a user.
    
    Args:
        username: Username to check
        project_id: Optional project ID to filter by
        
    Returns:
        Dictionary with task counts by status
    """
    db: SupabaseDB = get_db()
    
    # Get tasks assigned to user
    if project_id:
        # Filter by both username and project
        tasks = await db.select_with_filters(
            "tasks",
            {"assigned_to": username, "project_id": project_id}
        )
    else:
        # All tasks for user across all projects
        tasks = await db.select_where("tasks", "assigned_to", username)
    
    # Count by status
    counts = {
        "total": len(tasks),
        "todo": sum(1 for t in tasks if t.get("status") == "todo"),
        "in_progress": sum(1 for t in tasks if t.get("status") == "in_progress"),
        "completed": sum(1 for t in tasks if t.get("status") == "completed")
    }
    
    return counts


async def get_project_member_count(project_id: str) -> int:
    """
    Get the number of team members in a project.
    
    Args:
        project_id: UUID of the project
        
    Returns:
        Number of team members (including owner)
    """
    db: SupabaseDB = get_db()
    
    # Get team members count
    members = await db.select_where("team_members", "project_id", project_id)
    
    # Add 1 for the owner (who isn't in team_members table)
    return len(members) + 1


def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation
    if not username or len(username) < 3 or len(username) > 50:
        return False
    
    # Could add more validation (alphanumeric, special chars, etc.)
    return True


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation (Pydantic handles this better)
    if not email or "@" not in email or "." not in email:
        return False
    
    return True

