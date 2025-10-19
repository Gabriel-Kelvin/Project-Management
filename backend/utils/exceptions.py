"""
Custom exception classes for the application.
"""
from fastapi import HTTPException, status


class ProjectNotFoundException(HTTPException):
    """Exception raised when a project is not found."""
    
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found"
        )


class UnauthorizedAccessException(HTTPException):
    """Exception raised when user tries to access unauthorized resource."""
    
    def __init__(self, message: str = "You don't have permission to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class InvalidDataException(HTTPException):
    """Exception raised when invalid data is provided."""
    
    def __init__(self, message: str = "Invalid data provided"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class TaskNotFoundException(HTTPException):
    """Exception raised when a task is not found."""
    
    def __init__(self, task_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found"
        )


class TeamMemberNotFoundException(HTTPException):
    """Exception raised when a team member is not found."""
    
    def __init__(self, message: str = "Team member not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )


class DatabaseException(HTTPException):
    """Exception raised when a database operation fails."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )


class DuplicateEntryException(HTTPException):
    """Exception raised when trying to create a duplicate entry."""
    
    def __init__(self, message: str = "Entry already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class MemberAlreadyExistsException(HTTPException):
    """Exception raised when trying to add an existing team member."""
    
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User '{username}' is already a member of this project"
        )


class InvalidRoleException(HTTPException):
    """Exception raised when an invalid role is provided."""
    
    def __init__(self, role: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{role}'. Must be one of: owner, manager, developer, viewer"
        )


class CannotRemoveOwnerException(HTTPException):
    """Exception raised when trying to remove the project owner."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the project owner from the team"
        )


class UserNotFoundException(HTTPException):
    """Exception raised when a user is not found."""
    
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )


class InsufficientPermissionsException(HTTPException):
    """Exception raised when user lacks required permissions."""
    
    def __init__(self, action: str = "perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to {action}"
        )

