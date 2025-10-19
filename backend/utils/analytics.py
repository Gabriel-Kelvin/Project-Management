"""
Analytics and progress tracking utilities.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from utils.supabase_client import get_db, SupabaseDB


async def calculate_project_progress(project_id: str) -> int:
    """
    Calculate project progress as percentage of completed tasks.
    
    Formula: (completed_tasks / total_tasks) * 100
    
    Args:
        project_id: Project UUID
        
    Returns:
        Progress percentage (0-100)
    """
    db: SupabaseDB = get_db()
    
    # Get all tasks for the project
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    # If no tasks exist, progress is 0
    if not tasks or len(tasks) == 0:
        return 0
    
    # Count completed tasks
    completed = sum(1 for task in tasks if task.get("status") == "completed")
    
    # Calculate percentage
    progress = int((completed / len(tasks)) * 100)
    
    # Update project progress in database
    await db.update("projects", project_id, {"progress": progress})
    
    return progress


async def calculate_task_completion_rate(project_id: str) -> Dict[str, int]:
    """
    Calculate task completion rate for a project.
    
    Args:
        project_id: Project UUID
        
    Returns:
        Dictionary with task counts by status
    """
    db: SupabaseDB = get_db()
    
    # Get all tasks for the project
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    # Count tasks by status
    result = {
        "total_tasks": len(tasks),
        "completed_tasks": sum(1 for t in tasks if t.get("status") == "completed"),
        "in_progress_tasks": sum(1 for t in tasks if t.get("status") == "in_progress"),
        "todo_tasks": sum(1 for t in tasks if t.get("status") == "todo")
    }
    
    return result


async def get_member_workload(project_id: str, username: str) -> Dict[str, int]:
    """
    Get workload for a specific team member.
    
    Args:
        project_id: Project UUID
        username: Username to check
        
    Returns:
        Dictionary with task counts by status
    """
    db: SupabaseDB = get_db()
    
    # Get tasks assigned to this user in this project
    tasks = await db.select_with_filters(
        "tasks",
        {"project_id": project_id, "assigned_to": username}
    )
    
    # Count tasks by status
    result = {
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t.get("status") == "completed"),
        "in_progress": sum(1 for t in tasks if t.get("status") == "in_progress"),
        "todo": sum(1 for t in tasks if t.get("status") == "todo")
    }
    
    return result


async def get_tasks_by_priority(project_id: str) -> Dict[str, int]:
    """
    Get task counts grouped by priority.
    
    Args:
        project_id: Project UUID
        
    Returns:
        Dictionary with task counts by priority
    """
    db: SupabaseDB = get_db()
    
    # Get all tasks for the project
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    # Count tasks by priority
    result = {
        "high": sum(1 for t in tasks if t.get("priority") == "high"),
        "medium": sum(1 for t in tasks if t.get("priority") == "medium"),
        "low": sum(1 for t in tasks if t.get("priority") == "low")
    }
    
    return result


async def get_team_productivity(project_id: str) -> List[Dict]:
    """
    Calculate productivity metrics for all team members.
    
    Args:
        project_id: Project UUID
        
    Returns:
        List of team member productivity metrics
    """
    db: SupabaseDB = get_db()
    
    # Get all team members
    team_members = await db.select_where("team_members", "project_id", project_id)
    
    # Get project owner
    project = await db.select_by_id("projects", project_id)
    owner_id = project.get("owner_id") if project else None
    
    # Add owner to team members list
    all_members = []
    if owner_id:
        all_members.append({"username": owner_id, "role": "owner"})
    all_members.extend([{"username": tm["username"], "role": tm["role"]} for tm in team_members])
    
    # Calculate productivity for each member
    productivity = []
    for member in all_members:
        username = member["username"]
        
        # Get tasks assigned to this member
        tasks = await db.select_with_filters(
            "tasks",
            {"project_id": project_id, "assigned_to": username}
        )
        
        tasks_assigned = len(tasks)
        tasks_completed = sum(1 for t in tasks if t.get("status") == "completed")
        
        # Calculate completion rate
        completion_rate = (tasks_completed / tasks_assigned * 100) if tasks_assigned > 0 else 0
        
        # Calculate average completion time
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        if completed_tasks:
            total_days = 0
            valid_tasks = 0
            
            for task in completed_tasks:
                created_at = task.get("created_at")
                updated_at = task.get("updated_at")
                
                if created_at and updated_at:
                    try:
                        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                        days = (updated - created).days
                        if days >= 0:
                            total_days += days
                            valid_tasks += 1
                    except (ValueError, TypeError):
                        continue
            
            average_completion_time = round(total_days / valid_tasks, 1) if valid_tasks > 0 else 0.0
        else:
            average_completion_time = 0.0
        
        productivity.append({
            "username": username,
            "tasks_assigned": tasks_assigned,
            "tasks_completed": tasks_completed,
            "completion_rate": round(completion_rate, 2),
            "average_completion_time": average_completion_time,
            "last_active": datetime.now().isoformat()  # Mock last active time
        })
    
    return productivity


async def get_project_timeline(project_id: str, days: int = 30) -> List[Dict]:
    """
    Get project progress timeline for the last N days.
    
    Args:
        project_id: Project UUID
        days: Number of days to look back (default: 30)
        
    Returns:
        List of daily progress metrics
    """
    db: SupabaseDB = get_db()
    
    # Get all tasks for the project
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Group tasks by completion date
    timeline = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Count tasks completed by this date
        completed_by_date = sum(
            1 for t in tasks
            if t.get("status") == "completed" and
            t.get("updated_at") and
            datetime.fromisoformat(t["updated_at"].replace("Z", "+00:00")).date() <= current_date.date()
        )
        
        total_tasks = len(tasks)
        progress = int((completed_by_date / total_tasks * 100)) if total_tasks > 0 else 0
        
        timeline.append({
            "date": date_str,
            "completed": completed_by_date,
            "total": total_tasks,
            "progress": progress
        })
        
        current_date += timedelta(days=1)
    
    return timeline


async def get_member_analytics(project_id: str, username: str) -> Dict:
    """
    Get comprehensive analytics for a specific team member.
    
    Args:
        project_id: Project UUID
        username: Username to analyze
        
    Returns:
        Dictionary with member analytics
    """
    from utils.permissions import get_user_role_in_project
    
    db: SupabaseDB = get_db()
    
    # Get user's role
    role = await get_user_role_in_project(username, project_id)
    
    # Get tasks assigned to this user
    tasks = await db.select_with_filters(
        "tasks",
        {"project_id": project_id, "assigned_to": username}
    )
    
    # Count tasks by status
    total_assigned = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
    todo = sum(1 for t in tasks if t.get("status") == "todo")
    
    # Calculate completion rate
    completion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
    
    # Calculate average completion time
    completed_tasks = [t for t in tasks if t.get("status") == "completed"]
    if completed_tasks:
        total_days = 0
        valid_tasks = 0
        
        for task in completed_tasks:
            created_at = task.get("created_at")
            updated_at = task.get("updated_at")
            
            if created_at and updated_at:
                try:
                    # Parse dates
                    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    
                    # Calculate days between creation and completion
                    days = (updated - created).days
                    if days >= 0:  # Only count positive durations
                        total_days += days
                        valid_tasks += 1
                except (ValueError, TypeError):
                    continue
        
        average_completion_time = round(total_days / valid_tasks, 1) if valid_tasks > 0 else 0.0
    else:
        average_completion_time = 0.0
    
    return {
        "username": username,
        "role": role or "none",
        "total_assigned": total_assigned,
        "completed": completed,
        "in_progress": in_progress,
        "todo": todo,
        "completion_rate": round(completion_rate, 2),
        "average_completion_time": average_completion_time
    }


async def get_user_all_tasks(username: str) -> List[Dict]:
    """
    Get all tasks assigned to a user across all projects.
    
    Args:
        username: Username to check
        
    Returns:
        List of tasks with project information
    """
    db: SupabaseDB = get_db()
    
    # Get all tasks assigned to user
    tasks = await db.select_where("tasks", "assigned_to", username)
    
    # Enrich with project information
    enriched_tasks = []
    for task in tasks:
        project_id = task.get("project_id")
        project = await db.select_by_id("projects", project_id)
        
        enriched_task = {
            **task,
            "project_name": project.get("name") if project else "Unknown"
        }
        enriched_tasks.append(enriched_task)
    
    return enriched_tasks


async def get_user_statistics(username: str) -> Dict:
    """
    Get overall statistics for a user.
    
    Args:
        username: Username to analyze
        
    Returns:
        Dictionary with user statistics
    """
    from utils.permissions import get_user_role_in_project
    
    db: SupabaseDB = get_db()
    
    # Get projects where user is owner
    owned_projects = await db.select_where("projects", "owner_id", username)
    
    # Get projects where user is team member
    team_memberships = await db.select_where("team_members", "username", username)
    member_projects = []
    for membership in team_memberships:
        project = await db.select_by_id("projects", membership["project_id"])
        if project:
            member_projects.append(project)
    
    # Total unique projects
    all_project_ids = set()
    for project in owned_projects + member_projects:
        all_project_ids.add(project["id"])
    
    total_projects = len(all_project_ids)
    
    # Get all tasks assigned to user
    all_tasks = await db.select_where("tasks", "assigned_to", username)
    
    total_assigned_tasks = len(all_tasks)
    completed_tasks_by_me = sum(1 for t in all_tasks if t.get("status") == "completed")
    in_progress_tasks_by_me = sum(1 for t in all_tasks if t.get("status") == "in_progress")
    
    return {
        "total_projects": total_projects,
        "total_assigned_tasks": total_assigned_tasks,
        "completed_tasks_by_me": completed_tasks_by_me,
        "in_progress_tasks_by_me": in_progress_tasks_by_me
    }

