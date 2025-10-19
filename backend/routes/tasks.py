"""
Tasks management API routes.
"""
from fastapi import APIRouter, Depends, status
from typing import List

from models.auth import User
from models.project import (
    Task, TaskCreate, TaskUpdate, TaskStatusUpdate, TaskListResponse
)
from utils.middleware import get_current_user
from utils.supabase_client import get_db, SupabaseDB
from utils.permissions import (
    get_user_role_in_project, is_project_member, 
    can_edit_task, can_delete_task, can_assign_task,
    Permission, check_permission
)
from utils.exceptions import (
    ProjectNotFoundException, TaskNotFoundException,
    UnauthorizedAccessException, InvalidDataException,
    InsufficientPermissionsException
)
from utils.helpers import log_task_assignment


# Create router
router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Project or task doesn't exist"}
    }
)


async def verify_project_access(project_id: str, username: str) -> None:
    """
    Verify that project exists and user has access to it.
    
    Args:
        project_id: Project UUID
        username: Username to check
        
    Raises:
        ProjectNotFoundException: If project doesn't exist
        UnauthorizedAccessException: If user doesn't have access
    """
    db: SupabaseDB = get_db()
    
    # Check if project exists
    project = await db.select_by_id("projects", project_id)
    if not project:
        raise ProjectNotFoundException(project_id)
    
    # Check if user is a member
    if not await is_project_member(username, project_id):
        raise UnauthorizedAccessException("You don't have access to this project")


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task in a project.
    
    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **assigned_to**: Username to assign task to (optional)
    - **status**: Task status (default: todo)
    - **priority**: Task priority (default: medium)
    
    User must be a member of the project to create tasks.
    Only users with CREATE_TASK permission can create tasks.
    """
    db: SupabaseDB = get_db()
    
    # Verify project access
    await verify_project_access(project_id, current_user.username)
    
    # Check permission
    user_role = await get_user_role_in_project(current_user.username, project_id)
    if not check_permission(user_role, Permission.CREATE_TASK):
        raise InsufficientPermissionsException("create tasks")
    
    # If assigning to someone, verify they exist and are a project member
    if task_data.assigned_to:
        if not await is_project_member(task_data.assigned_to, project_id):
            raise InvalidDataException(
                f"User '{task_data.assigned_to}' is not a member of this project"
            )
        
        # Check if user can assign tasks
        if task_data.assigned_to != current_user.username:
            if not await can_assign_task(current_user.username, project_id):
                raise InsufficientPermissionsException("assign tasks to others")
    
    # Prepare task data
    task_dict = task_data.model_dump()
    task_dict["project_id"] = project_id
    
    # Create task
    created_task = await db.insert("tasks", task_dict)
    
    # Log assignment if task is assigned
    if task_data.assigned_to:
        await log_task_assignment(
            task_id=created_task["id"],
            assigned_to=task_data.assigned_to,
            assigned_by=current_user.username,
            project_id=project_id
        )
    
    return Task(**created_task)


@router.get("", response_model=TaskListResponse)
async def get_all_tasks(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all tasks in a project.
    
    Returns all tasks for users who have access to the project.
    Only users with VIEW_TASK permission can view tasks.
    """
    db: SupabaseDB = get_db()
    
    # Verify project access
    await verify_project_access(project_id, current_user.username)
    
    # Check permission
    user_role = await get_user_role_in_project(current_user.username, project_id)
    if not check_permission(user_role, Permission.VIEW_TASK):
        raise InsufficientPermissionsException("view tasks")
    
    # Get all tasks for this project
    tasks = await db.select_where("tasks", "project_id", project_id)
    
    return TaskListResponse(
        tasks=[Task(**task) for task in tasks],
        total=len(tasks)
    )


@router.get("/{task_id}", response_model=Task)
async def get_task(
    project_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a single task by ID.
    
    Returns detailed task information.
    Only users with VIEW_TASK permission can view tasks.
    """
    db: SupabaseDB = get_db()
    
    # Verify project access
    await verify_project_access(project_id, current_user.username)
    
    # Check permission
    user_role = await get_user_role_in_project(current_user.username, project_id)
    if not check_permission(user_role, Permission.VIEW_TASK):
        raise InsufficientPermissionsException("view tasks")
    
    # Get task
    task = await db.select_by_id("tasks", task_id)
    
    if not task:
        raise TaskNotFoundException(task_id)
    
    # Verify task belongs to this project
    if task["project_id"] != project_id:
        raise TaskNotFoundException(task_id)
    
    return Task(**task)


@router.put("/{task_id}", response_model=Task)
async def update_task(
    project_id: str,
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a task.
    
    - **title**: New task title (optional)
    - **description**: New description (optional)
    - **assigned_to**: New assignee (optional)
    - **status**: New status (optional)
    - **priority**: New priority (optional)
    
    Permissions:
    - Owners and Managers can edit any task
    - Developers can only edit their own tasks
    - Users with ASSIGN_TASK permission can change assigned_to
    """
    db: SupabaseDB = get_db()
    
    # Verify project access
    await verify_project_access(project_id, current_user.username)
    
    # Get existing task
    task = await db.select_by_id("tasks", task_id)
    
    if not task:
        raise TaskNotFoundException(task_id)
    
    # Verify task belongs to this project
    if task["project_id"] != project_id:
        raise TaskNotFoundException(task_id)
    
    # Get task creator/owner (could be assigned_to or we track separately)
    # For now, we'll check if user can edit this task
    task_owner = task.get("assigned_to")
    
    # Check if user can edit this task
    if not await can_edit_task(current_user.username, project_id, task_owner):
        raise InsufficientPermissionsException("edit this task")
    
    # Get only fields that were provided
    update_data = task_data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise InvalidDataException("No fields to update")
    
    # If changing assignment, verify permissions and target user
    if "assigned_to" in update_data and update_data["assigned_to"] != task_owner:
        if not await can_assign_task(current_user.username, project_id):
            raise InsufficientPermissionsException("assign tasks")
        
        # Verify new assignee is a project member
        if update_data["assigned_to"]:
            if not await is_project_member(update_data["assigned_to"], project_id):
                raise InvalidDataException(
                    f"User '{update_data['assigned_to']}' is not a member of this project"
                )
            
            # Log new assignment
            await log_task_assignment(
                task_id=task_id,
                assigned_to=update_data["assigned_to"],
                assigned_by=current_user.username,
                project_id=project_id
            )
    
    # Update task
    updated_task = await db.update("tasks", task_id, update_data)
    
    # If status was updated, recalculate project progress
    if "status" in update_data:
        from utils.analytics import calculate_project_progress
        new_progress = await calculate_project_progress(project_id)
        updated_task["project_progress"] = new_progress
    
    return Task(**updated_task)


@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    project_id: str,
    task_id: str,
    status_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update only the status of a task.
    
    Quick endpoint for status changes.
    
    - **status**: New status (todo, in_progress, completed)
    
    Users with UPDATE_TASK_STATUS permission can update status.
    This includes owners, managers, developers, and assigned users.
    """
    db: SupabaseDB = get_db()
    
    # Verify project access
    await verify_project_access(project_id, current_user.username)
    
    # Get existing task
    task = await db.select_by_id("tasks", task_id)
    
    if not task:
        raise TaskNotFoundException(task_id)
    
    # Verify task belongs to this project
    if task["project_id"] != project_id:
        raise TaskNotFoundException(task_id)
    
    # Check permission
    user_role = await get_user_role_in_project(current_user.username, project_id)
    task_owner = task.get("assigned_to")
    
    # Allow status update if user has permission OR is the assigned user
    has_permission = check_permission(user_role, Permission.UPDATE_TASK_STATUS)
    is_assigned = task_owner == current_user.username
    
    if not (has_permission or is_assigned):
        raise InsufficientPermissionsException("update task status")
    
    # Update status
    updated_task = await db.update("tasks", task_id, {"status": status_data.status})
    
    # Recalculate project progress after status change
    from utils.analytics import calculate_project_progress
    new_progress = await calculate_project_progress(project_id)
    updated_task["project_progress"] = new_progress
    
    return Task(**updated_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    project_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    
    Only project owners and managers can delete tasks.
    Users must have DELETE_TASK permission.
    """
    db: SupabaseDB = get_db()
    
    # Verify project access
    await verify_project_access(project_id, current_user.username)
    
    # Get existing task
    task = await db.select_by_id("tasks", task_id)
    
    if not task:
        raise TaskNotFoundException(task_id)
    
    # Verify task belongs to this project
    if task["project_id"] != project_id:
        raise TaskNotFoundException(task_id)
    
    # Check if user can delete this task
    task_owner = task.get("assigned_to")
    if not await can_delete_task(current_user.username, project_id, task_owner):
        raise InsufficientPermissionsException("delete tasks")
    
    # Delete task
    await db.delete("tasks", task_id)
    
    return None

