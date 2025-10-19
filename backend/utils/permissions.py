"""
Role-based access control (RBAC) system for project permissions.
"""
from typing import List, Optional
from enum import Enum

from utils.supabase_client import get_db, SupabaseDB


class Permission(str, Enum):
    """Available permissions in the system."""
    # Project permissions
    CREATE_PROJECT = "create_project"
    EDIT_PROJECT = "edit_project"
    DELETE_PROJECT = "delete_project"
    VIEW_PROJECT = "view_project"
    
    # Task permissions
    CREATE_TASK = "create_task"
    EDIT_TASK = "edit_task"
    DELETE_TASK = "delete_task"
    VIEW_TASK = "view_task"
    ASSIGN_TASK = "assign_task"
    UPDATE_TASK_STATUS = "update_task_status"
    
    # Team permissions
    MANAGE_TEAM = "manage_team"
    ADD_MEMBER = "add_member"
    REMOVE_MEMBER = "remove_member"
    UPDATE_ROLE = "update_role"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"


class Role(str, Enum):
    """Project roles."""
    OWNER = "owner"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"


# Role permissions mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [
        # All permissions
        Permission.CREATE_PROJECT,
        Permission.EDIT_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.VIEW_PROJECT,
        Permission.CREATE_TASK,
        Permission.EDIT_TASK,
        Permission.DELETE_TASK,
        Permission.VIEW_TASK,
        Permission.ASSIGN_TASK,
        Permission.UPDATE_TASK_STATUS,
        Permission.MANAGE_TEAM,
        Permission.ADD_MEMBER,
        Permission.REMOVE_MEMBER,
        Permission.UPDATE_ROLE,
        Permission.VIEW_ANALYTICS,
    ],
    Role.MANAGER: [
        # Project view/edit
        Permission.EDIT_PROJECT,
        Permission.VIEW_PROJECT,
        # All task operations
        Permission.CREATE_TASK,
        Permission.EDIT_TASK,
        Permission.DELETE_TASK,
        Permission.VIEW_TASK,
        Permission.ASSIGN_TASK,
        Permission.UPDATE_TASK_STATUS,
        # Team management (except owner operations)
        Permission.ADD_MEMBER,
        # Analytics
        Permission.VIEW_ANALYTICS,
    ],
    Role.DEVELOPER: [
        # View project
        Permission.VIEW_PROJECT,
        # Task operations (limited)
        Permission.CREATE_TASK,
        Permission.VIEW_TASK,
        Permission.UPDATE_TASK_STATUS,
        # Can only edit own tasks
    ],
    Role.VIEWER: [
        # Read-only access
        Permission.VIEW_PROJECT,
        Permission.VIEW_TASK,
    ],
}


async def get_user_role_in_project(username: str, project_id: str) -> Optional[str]:
    """
    Get the role of a user in a specific project.
    
    Args:
        username: Username to check
        project_id: Project UUID
        
    Returns:
        Role string (owner, manager, developer, viewer) or None if not a member
    """
    db: SupabaseDB = get_db()
    
    # Check if user is the project owner
    project = await db.select_by_id("projects", project_id)
    if project and project.get("owner_id") == username:
        return Role.OWNER
    
    # Check if user is a team member
    team_members = await db.select_with_filters(
        "team_members",
        {"project_id": project_id, "username": username}
    )
    
    if team_members and len(team_members) > 0:
        return team_members[0].get("role")
    
    return None


def check_permission(user_role: str, required_permission: Permission) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        user_role: User's role in the project
        required_permission: Permission to check
        
    Returns:
        True if role has permission, False otherwise
    """
    if not user_role:
        return False
    
    try:
        role_enum = Role(user_role.lower())
        permissions = ROLE_PERMISSIONS.get(role_enum, [])
        return required_permission in permissions
    except ValueError:
        return False


def has_any_permission(user_role: str, required_permissions: List[Permission]) -> bool:
    """
    Check if a role has any of the specified permissions.
    
    Args:
        user_role: User's role in the project
        required_permissions: List of permissions to check
        
    Returns:
        True if role has at least one permission, False otherwise
    """
    return any(check_permission(user_role, perm) for perm in required_permissions)


def has_all_permissions(user_role: str, required_permissions: List[Permission]) -> bool:
    """
    Check if a role has all of the specified permissions.
    
    Args:
        user_role: User's role in the project
        required_permissions: List of permissions to check
        
    Returns:
        True if role has all permissions, False otherwise
    """
    return all(check_permission(user_role, perm) for perm in required_permissions)


async def is_project_owner(username: str, project_id: str) -> bool:
    """
    Check if user is the owner of a project.
    
    Args:
        username: Username to check
        project_id: Project UUID
        
    Returns:
        True if user is owner, False otherwise
    """
    db: SupabaseDB = get_db()
    project = await db.select_by_id("projects", project_id)
    return project is not None and project.get("owner_id") == username


async def is_project_member(username: str, project_id: str) -> bool:
    """
    Check if user is a member of a project (including owner).
    
    Args:
        username: Username to check
        project_id: Project UUID
        
    Returns:
        True if user is owner or team member, False otherwise
    """
    # Check if owner
    if await is_project_owner(username, project_id):
        return True
    
    # Check if team member
    role = await get_user_role_in_project(username, project_id)
    return role is not None


async def can_edit_task(username: str, project_id: str, task_owner: Optional[str] = None) -> bool:
    """
    Check if user can edit a task.
    Developers can only edit their own tasks.
    Managers and owners can edit any task.
    
    Args:
        username: Username to check
        project_id: Project UUID
        task_owner: Username who created/owns the task
        
    Returns:
        True if user can edit, False otherwise
    """
    role = await get_user_role_in_project(username, project_id)
    
    if not role:
        return False
    
    # Owner and manager can edit any task
    if role in [Role.OWNER, Role.MANAGER]:
        return True
    
    # Developer can only edit own tasks
    if role == Role.DEVELOPER:
        return task_owner == username
    
    # Viewer cannot edit
    return False


async def can_delete_task(username: str, project_id: str, task_owner: Optional[str] = None) -> bool:
    """
    Check if user can delete a task.
    Only owners and managers can delete tasks.
    
    Args:
        username: Username to check
        project_id: Project UUID
        task_owner: Username who created/owns the task
        
    Returns:
        True if user can delete, False otherwise
    """
    role = await get_user_role_in_project(username, project_id)
    
    if not role:
        return False
    
    # Only owner and manager can delete
    return role in [Role.OWNER, Role.MANAGER]


async def can_assign_task(username: str, project_id: str) -> bool:
    """
    Check if user can assign tasks to others.
    
    Args:
        username: Username to check
        project_id: Project UUID
        
    Returns:
        True if user can assign, False otherwise
    """
    role = await get_user_role_in_project(username, project_id)
    return check_permission(role, Permission.ASSIGN_TASK)


async def can_manage_team(username: str, project_id: str) -> bool:
    """
    Check if user can manage team members.
    
    Args:
        username: Username to check
        project_id: Project UUID
        
    Returns:
        True if user can manage team, False otherwise
    """
    role = await get_user_role_in_project(username, project_id)
    return check_permission(role, Permission.MANAGE_TEAM)


def get_role_permissions(role: str) -> List[Permission]:
    """
    Get all permissions for a role.
    
    Args:
        role: Role string
        
    Returns:
        List of permissions
    """
    try:
        role_enum = Role(role.lower())
        return ROLE_PERMISSIONS.get(role_enum, [])
    except ValueError:
        return []

