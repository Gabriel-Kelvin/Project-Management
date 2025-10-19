import re
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status

# Validation patterns
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_MIN_LENGTH = 6
PROJECT_NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 500
TASK_TITLE_MAX_LENGTH = 150

# Allowed values
ALLOWED_ROLES = ['owner', 'manager', 'developer', 'viewer']
ALLOWED_STATUSES = ['todo', 'in_progress', 'completed']
ALLOWED_PRIORITIES = ['low', 'medium', 'high']

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

def validate_username(username: str) -> str:
    """
    Validate username format
    - Must be 3-20 characters
    - Only alphanumeric and underscore
    """
    if not username:
        raise ValidationError("Username is required", "username")
    
    if not isinstance(username, str):
        raise ValidationError("Username must be a string", "username")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters", "username")
    
    if len(username) > 20:
        raise ValidationError("Username must be no more than 20 characters", "username")
    
    if not USERNAME_PATTERN.match(username):
        raise ValidationError(
            "Username can only contain letters, numbers, and underscores", 
            "username"
        )
    
    return username.lower()

def validate_email(email: str) -> str:
    """
    Validate email format
    """
    if not email:
        raise ValidationError("Email is required", "email")
    
    if not isinstance(email, str):
        raise ValidationError("Email must be a string", "email")
    
    email = email.strip().lower()
    
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format", "email")
    
    if len(email) > 254:  # RFC 5321 limit
        raise ValidationError("Email is too long", "email")
    
    return email

def validate_password(password: str) -> str:
    """
    Validate password strength
    - Minimum 6 characters
    """
    if not password:
        raise ValidationError("Password is required", "password")
    
    if not isinstance(password, str):
        raise ValidationError("Password must be a string", "password")
    
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters", 
            "password"
        )
    
    if len(password) > 128:  # Reasonable upper limit
        raise ValidationError("Password is too long", "password")
    
    return password

def validate_project_name(name: str) -> str:
    """
    Validate project name
    - Maximum 100 characters
    - Not empty
    """
    if not name:
        raise ValidationError("Project name is required", "name")
    
    if not isinstance(name, str):
        raise ValidationError("Project name must be a string", "name")
    
    name = name.strip()
    
    if not name:
        raise ValidationError("Project name cannot be empty", "name")
    
    if len(name) > PROJECT_NAME_MAX_LENGTH:
        raise ValidationError(
            f"Project name must be no more than {PROJECT_NAME_MAX_LENGTH} characters", 
            "name"
        )
    
    return name

def validate_description(description: Optional[str]) -> Optional[str]:
    """
    Validate description
    - Maximum 500 characters
    - Allow markdown
    """
    if description is None:
        return None
    
    if not isinstance(description, str):
        raise ValidationError("Description must be a string", "description")
    
    description = description.strip()
    
    if len(description) > DESCRIPTION_MAX_LENGTH:
        raise ValidationError(
            f"Description must be no more than {DESCRIPTION_MAX_LENGTH} characters", 
            "description"
        )
    
    return description

def validate_task_title(title: str) -> str:
    """
    Validate task title
    - Maximum 150 characters
    - Not empty
    """
    if not title:
        raise ValidationError("Task title is required", "title")
    
    if not isinstance(title, str):
        raise ValidationError("Task title must be a string", "title")
    
    title = title.strip()
    
    if not title:
        raise ValidationError("Task title cannot be empty", "title")
    
    if len(title) > TASK_TITLE_MAX_LENGTH:
        raise ValidationError(
            f"Task title must be no more than {TASK_TITLE_MAX_LENGTH} characters", 
            "title"
        )
    
    return title

def validate_role(role: str) -> str:
    """
    Validate user role
    - Must be one of allowed roles
    """
    if not role:
        raise ValidationError("Role is required", "role")
    
    if not isinstance(role, str):
        raise ValidationError("Role must be a string", "role")
    
    role = role.lower().strip()
    
    if role not in ALLOWED_ROLES:
        raise ValidationError(
            f"Role must be one of: {', '.join(ALLOWED_ROLES)}", 
            "role"
        )
    
    return role

def validate_status(status: str) -> str:
    """
    Validate task status
    - Must be valid status
    """
    if not status:
        raise ValidationError("Status is required", "status")
    
    if not isinstance(status, str):
        raise ValidationError("Status must be a string", "status")
    
    status = status.lower().strip()
    
    if status not in ALLOWED_STATUSES:
        raise ValidationError(
            f"Status must be one of: {', '.join(ALLOWED_STATUSES)}", 
            "status"
        )
    
    return status

def validate_priority(priority: str) -> str:
    """
    Validate task priority
    - Must be valid priority
    """
    if not priority:
        raise ValidationError("Priority is required", "priority")
    
    if not isinstance(priority, str):
        raise ValidationError("Priority must be a string", "priority")
    
    priority = priority.lower().strip()
    
    if priority not in ALLOWED_PRIORITIES:
        raise ValidationError(
            f"Priority must be one of: {', '.join(ALLOWED_PRIORITIES)}", 
            "priority"
        )
    
    return priority

def validate_due_date(due_date: Optional[str]) -> Optional[str]:
    """
    Validate due date format (ISO 8601)
    """
    if due_date is None:
        return None
    
    if not isinstance(due_date, str):
        raise ValidationError("Due date must be a string", "due_date")
    
    due_date = due_date.strip()
    
    if not due_date:
        return None
    
    # Basic ISO 8601 validation
    try:
        from datetime import datetime
        datetime.fromisoformat(due_date.replace('Z', '+00:00'))
    except ValueError:
        raise ValidationError("Due date must be in ISO 8601 format", "due_date")
    
    return due_date

def validate_pagination_params(page: int = 1, limit: int = 20) -> tuple:
    """
    Validate pagination parameters
    """
    if not isinstance(page, int) or page < 1:
        raise ValidationError("Page must be a positive integer", "page")
    
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ValidationError("Limit must be between 1 and 100", "limit")
    
    return page, limit

def validate_sort_params(sort_by: Optional[str], sort_order: str = "asc") -> tuple:
    """
    Validate sorting parameters
    """
    if sort_by is not None:
        if not isinstance(sort_by, str):
            raise ValidationError("Sort by must be a string", "sort_by")
        sort_by = sort_by.strip()
    
    if not isinstance(sort_order, str):
        raise ValidationError("Sort order must be a string", "sort_order")
    
    sort_order = sort_order.lower().strip()
    
    if sort_order not in ["asc", "desc"]:
        raise ValidationError("Sort order must be 'asc' or 'desc'", "sort_order")
    
    return sort_by, sort_order

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS
    """
    if not isinstance(text, str):
        return str(text)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def validate_signup_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete signup data
    """
    try:
        validated_data = {
            'username': validate_username(data.get('username')),
            'email': validate_email(data.get('email')),
            'password': validate_password(data.get('password'))
        }
        return validated_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}"
        )

def validate_login_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete login data
    """
    try:
        validated_data = {
            'username': validate_username(data.get('username')),
            'password': validate_password(data.get('password'))
        }
        return validated_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}"
        )

def validate_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete project data
    """
    try:
        validated_data = {
            'name': validate_project_name(data.get('name')),
            'description': validate_description(data.get('description'))
        }
        return validated_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}"
        )

def validate_task_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete task data
    """
    try:
        validated_data = {
            'title': validate_task_title(data.get('title')),
            'description': validate_description(data.get('description')),
            'status': validate_status(data.get('status', 'todo')),
            'priority': validate_priority(data.get('priority', 'medium')),
            'due_date': validate_due_date(data.get('due_date'))
        }
        return validated_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}"
        )

def validate_member_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete member data
    """
    try:
        validated_data = {
            'username': validate_username(data.get('username')),
            'role': validate_role(data.get('role'))
        }
        return validated_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}"
        )

def validate_status_update_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate status update data
    """
    try:
        validated_data = {
            'status': validate_status(data.get('status'))
        }
        return validated_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}"
        )

# Utility functions for common validations
def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def validate_uuid(uuid_string: str, field_name: str = "id") -> str:
    """Validate UUID format"""
    if not uuid_string:
        raise ValidationError(f"{field_name} is required", field_name)
    
    if not is_valid_uuid(uuid_string):
        raise ValidationError(f"Invalid {field_name} format", field_name)
    
    return uuid_string

def validate_positive_integer(value: Any, field_name: str) -> int:
    """Validate positive integer"""
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(f"{field_name} must be positive", field_name)
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a positive integer", field_name)
