"""
Team member and role management API routes.
"""
from fastapi import APIRouter, Depends, status
from typing import List

from models.auth import User
from models.project import TeamMember, TeamMemberAdd
from utils.middleware import get_current_user
from utils.supabase_client import get_db, SupabaseDB
from utils.permissions import (
    get_user_role_in_project, is_project_owner, is_project_member,
    can_manage_team, Role
)
from utils.exceptions import (
    ProjectNotFoundException, UnauthorizedAccessException,
    InvalidDataException, MemberAlreadyExistsException,
    InvalidRoleException, CannotRemoveOwnerException,
    TeamMemberNotFoundException, InsufficientPermissionsException
)


# Create router
router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["Team Members"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - Project or member doesn't exist"}
    }
)


async def verify_project_exists(project_id: str) -> dict:
    """
    Verify that project exists.
    
    Args:
        project_id: Project UUID
        
    Returns:
        Project dictionary
        
    Raises:
        ProjectNotFoundException: If project doesn't exist
    """
    db: SupabaseDB = get_db()
    project = await db.select_by_id("projects", project_id)
    
    if not project:
        raise ProjectNotFoundException(project_id)
    
    return project


def validate_role(role: str) -> None:
    """
    Validate that role is valid.
    
    Args:
        role: Role string to validate
        
    Raises:
        InvalidRoleException: If role is invalid
    """
    valid_roles = [r.value for r in Role]
    if role.lower() not in valid_roles:
        raise InvalidRoleException(role)


@router.post("", response_model=TeamMember, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    project_id: str,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_user)
):
    """
    Add a team member to a project.
    
    - **username**: Username of the user to add (required)
    - **role**: Role to assign (default: developer)
    
    Only project owners can add team members.
    If user already exists, their role will be updated instead.
    """
    db: SupabaseDB = get_db()
    
    # Verify project exists
    project = await verify_project_exists(project_id)
    
    # Only owner can add members
    if not await is_project_owner(current_user.username, project_id):
        raise InsufficientPermissionsException("add team members (owner only)")
    
    # Validate role
    validate_role(member_data.role)
    
    # Check if trying to add the owner (already a member by default)
    if member_data.username == project["owner_id"]:
        raise InvalidDataException("Project owner is already a member by default")
    
    # Check if user already exists in team
    existing_members = await db.select_with_filters(
        "team_members",
        {"project_id": project_id, "username": member_data.username}
    )
    
    if existing_members and len(existing_members) > 0:
        # Update role instead of creating new entry
        existing_member = existing_members[0]
        updated_member = await db.update(
            "team_members",
            existing_member["id"],
            {"role": member_data.role}
        )
        return TeamMember(**updated_member)
    
    # Add new team member
    member_dict = {
        "project_id": project_id,
        "username": member_data.username,
        "role": member_data.role
    }
    
    created_member = await db.insert("team_members", member_dict)
    
    return TeamMember(**created_member)


@router.get("", response_model=List[TeamMember])
async def get_team_members(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all team members of a project.
    
    Returns list of all members with their roles and assignment timestamps.
    Only accessible to project members.
    """
    db: SupabaseDB = get_db()
    
    # Verify project exists
    await verify_project_exists(project_id)
    
    # Verify user is a member
    if not await is_project_member(current_user.username, project_id):
        raise UnauthorizedAccessException("You don't have access to this project")
    
    # Get all team members
    members = await db.select_where("team_members", "project_id", project_id)
    
    return [TeamMember(**member) for member in members]


@router.put("/{username}", response_model=TeamMember)
async def update_member_role(
    project_id: str,
    username: str,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_user)
):
    """
    Update a team member's role.
    
    - **role**: New role to assign
    
    Only project owners can update roles.
    Cannot change the owner's role.
    """
    db: SupabaseDB = get_db()
    
    # Verify project exists
    project = await verify_project_exists(project_id)
    
    # Only owner can update roles
    if not await is_project_owner(current_user.username, project_id):
        raise InsufficientPermissionsException("update member roles (owner only)")
    
    # Validate new role
    validate_role(member_data.role)
    
    # Cannot change owner's role
    if username == project["owner_id"]:
        raise InvalidDataException("Cannot change the project owner's role")
    
    # Find the team member
    members = await db.select_with_filters(
        "team_members",
        {"project_id": project_id, "username": username}
    )
    
    if not members or len(members) == 0:
        raise TeamMemberNotFoundException(f"User '{username}' is not a member of this project")
    
    member = members[0]
    
    # Update role
    updated_member = await db.update(
        "team_members",
        member["id"],
        {"role": member_data.role}
    )
    
    return TeamMember(**updated_member)


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    project_id: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a team member from a project.
    
    Only project owners can remove team members.
    Cannot remove the project owner.
    
    Note: This will not delete or reassign tasks assigned to the removed member.
    Those tasks will remain assigned to them for historical purposes.
    """
    db: SupabaseDB = get_db()
    
    # Verify project exists
    project = await verify_project_exists(project_id)
    
    # Only owner can remove members
    if not await is_project_owner(current_user.username, project_id):
        raise InsufficientPermissionsException("remove team members (owner only)")
    
    # Cannot remove the owner
    if username == project["owner_id"]:
        raise CannotRemoveOwnerException()
    
    # Find the team member
    members = await db.select_with_filters(
        "team_members",
        {"project_id": project_id, "username": username}
    )
    
    if not members or len(members) == 0:
        raise TeamMemberNotFoundException(f"User '{username}' is not a member of this project")
    
    member = members[0]
    
    # Delete team member
    await db.delete("team_members", member["id"])
    
    # Note: Tasks assigned to this user remain unchanged
    # Consider adding a query parameter to handle task reassignment/deletion
    
    return None


@router.get("/{username}", response_model=TeamMember)
async def get_team_member(
    project_id: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get information about a specific team member.
    
    Returns the member's role and assignment timestamp.
    Only accessible to project members.
    """
    db: SupabaseDB = get_db()
    
    # Verify project exists
    await verify_project_exists(project_id)
    
    # Verify user is a member
    if not await is_project_member(current_user.username, project_id):
        raise UnauthorizedAccessException("You don't have access to this project")
    
    # Find the team member
    members = await db.select_with_filters(
        "team_members",
        {"project_id": project_id, "username": username}
    )
    
    if not members or len(members) == 0:
        raise TeamMemberNotFoundException(f"User '{username}' is not a member of this project")
    
    return TeamMember(**members[0])


@router.get("/{username}/permissions")
async def get_member_permissions(
    project_id: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the permissions for a specific team member.
    
    Returns the list of permissions the member has based on their role.
    Only accessible to project members.
    """
    from utils.permissions import get_role_permissions
    
    db: SupabaseDB = get_db()
    
    # Verify project exists
    await verify_project_exists(project_id)
    
    # Verify user is a member
    if not await is_project_member(current_user.username, project_id):
        raise UnauthorizedAccessException("You don't have access to this project")
    
    # Get user's role
    role = await get_user_role_in_project(username, project_id)
    
    if not role:
        raise TeamMemberNotFoundException(f"User '{username}' is not a member of this project")
    
    # Get permissions for this role
    permissions = get_role_permissions(role)
    
    return {
        "username": username,
        "role": role,
        "permissions": [perm.value for perm in permissions]
    }

