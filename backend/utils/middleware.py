"""
Middleware and dependency functions for authentication and authorization.
"""
from typing import Optional, List, Callable
from fastapi import Header, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from models.auth import User, UserResponse
from utils.supabase_auth import verify_token


# Define security scheme
security = HTTPBearer()


async def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Token string
        
    Raises:
        HTTPException: If authorization header is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if it's a Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return parts[1]


async def verify_auth_token(token: str = Depends(get_token_from_header)) -> UserResponse:
    """
    Verify the authentication token and return the user.
    
    Args:
        token: Authentication token from header
        
    Returns:
        UserResponse object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    is_valid, message, user = verify_token(token)
    
    if not is_valid or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Convert User to UserResponse
    from utils.supabase_auth import user_to_response
    return user_to_response(user)


async def get_current_user(token: str = Depends(get_token_from_header)) -> User:
    """
    Get the current authenticated user (full User object).
    
    Args:
        token: Authentication token from header
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    is_valid, message, user = verify_token(token)
    
    if not is_valid or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def optional_auth(authorization: Optional[str] = Header(None)) -> Optional[UserResponse]:
    """
    Optional authentication - returns user if authenticated, None otherwise.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        UserResponse object if authenticated, None otherwise
    """
    if not authorization:
        return None
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        token = parts[1]
        is_valid, message, user = verify_token(token)
        
        if is_valid and user:
            from utils.supabase_auth import user_to_response
            return user_to_response(user)
    except Exception:
        pass
    
    return None


def require_role(required_roles: List[str]) -> Callable:
    """
    Dependency factory to require specific roles for a project endpoint.
    
    Usage:
        @router.get("/projects/{project_id}/something")
        async def endpoint(
            project_id: str,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_role(["owner", "manager"]))
        ):
            ...
    
    Args:
        required_roles: List of roles that are allowed (e.g., ["owner", "manager"])
        
    Returns:
        Dependency function that checks role
    """
    async def check_role(
        project_id: str = Path(...),
        current_user: User = Depends(get_current_user)
    ) -> None:
        from utils.permissions import get_user_role_in_project
        from utils.exceptions import InsufficientPermissionsException
        
        # Get user's role in this project
        user_role = await get_user_role_in_project(current_user.username, project_id)
        
        # Check if user has one of the required roles
        if not user_role or user_role not in required_roles:
            roles_str = ", ".join(required_roles)
            raise InsufficientPermissionsException(
                f"This action requires one of these roles: {roles_str}"
            )
    
    return check_role


def require_project_owner() -> Callable:
    """
    Dependency to require project owner role.
    
    Usage:
        @router.delete("/projects/{project_id}")
        async def delete_project(
            project_id: str,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_project_owner())
        ):
            ...
    
    Returns:
        Dependency function that checks for owner role
    """
    return require_role(["owner"])


def require_project_member() -> Callable:
    """
    Dependency to require user to be a project member (any role).
    
    Usage:
        @router.get("/projects/{project_id}")
        async def get_project(
            project_id: str,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_project_member())
        ):
            ...
    
    Returns:
        Dependency function that checks membership
    """
    async def check_member(
        project_id: str = Path(...),
        current_user: User = Depends(get_current_user)
    ) -> None:
        from utils.permissions import is_project_member
        from utils.exceptions import UnauthorizedAccessException
        
        # Check if user is a member
        if not await is_project_member(current_user.username, project_id):
            raise UnauthorizedAccessException(
                "You must be a project member to access this resource"
            )
    
    return check_member


def require_permission(permission: str) -> Callable:
    """
    Dependency factory to require a specific permission for a project endpoint.
    
    Usage:
        from utils.permissions import Permission
        
        @router.post("/projects/{project_id}/tasks")
        async def create_task(
            project_id: str,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_permission(Permission.CREATE_TASK))
        ):
            ...
    
    Args:
        permission: Permission enum value required
        
    Returns:
        Dependency function that checks permission
    """
    async def check_perm(
        project_id: str = Path(...),
        current_user: User = Depends(get_current_user)
    ) -> None:
        from utils.permissions import get_user_role_in_project, check_permission, Permission
        from utils.exceptions import InsufficientPermissionsException
        
        # Get user's role in this project
        user_role = await get_user_role_in_project(current_user.username, project_id)
        
        # Convert permission string to Permission enum if needed
        perm_enum = Permission(permission) if isinstance(permission, str) else permission
        
        # Check if user has the required permission
        if not check_permission(user_role, perm_enum):
            raise InsufficientPermissionsException(
                f"This action requires permission: {permission}"
            )
    
    return check_perm

