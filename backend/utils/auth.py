"""
Authentication utility functions for signup, login, and token management.
"""
import uuid
from typing import Optional, Tuple
from datetime import datetime

from models.auth import (
    User, UserSignup, UserLogin, UserResponse, TokenResponse,
    get_storage, InMemoryStorage
)


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return f"user_{uuid.uuid4().hex[:12]}"


def generate_token() -> str:
    """Generate a simple authentication token."""
    return uuid.uuid4().hex


def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse (without password)."""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )


def signup(signup_data: UserSignup) -> Tuple[bool, str, Optional[TokenResponse]]:
    """
    Register a new user.
    
    Args:
        signup_data: User signup data
        
    Returns:
        Tuple of (success, message, token_response)
    """
    storage: InMemoryStorage = get_storage()
    
    # Check if username already exists
    if storage.username_exists(signup_data.username):
        return False, "Username already exists", None
    
    # Check if email already exists
    if storage.email_exists(signup_data.email):
        return False, "Email already exists", None
    
    # Create new user
    user_id = generate_user_id()
    new_user = User(
        id=user_id,
        username=signup_data.username,
        password=signup_data.password,  # Plain text (not recommended for production)
        email=signup_data.email,
        created_at=datetime.now()
    )
    
    # Add user to storage
    storage.add_user(new_user)
    
    # Generate token
    token = generate_token()
    storage.add_token(token, new_user.username)
    
    # Create response
    token_response = TokenResponse(
        token=token,
        user=user_to_response(new_user)
    )
    
    return True, "User registered successfully", token_response


def login(login_data: UserLogin) -> Tuple[bool, str, Optional[TokenResponse]]:
    """
    Authenticate a user and generate a token.
    
    Args:
        login_data: User login credentials
        
    Returns:
        Tuple of (success, message, token_response)
    """
    storage: InMemoryStorage = get_storage()
    
    # Get user by username
    user = storage.get_user_by_username(login_data.username)
    
    if not user:
        return False, "Invalid username or password", None
    
    # Verify password (plain text comparison)
    if user.password != login_data.password:
        return False, "Invalid username or password", None
    
    # Generate new token
    token = generate_token()
    storage.add_token(token, user.username)
    
    # Create response
    token_response = TokenResponse(
        token=token,
        user=user_to_response(user)
    )
    
    return True, "Login successful", token_response


def logout(token: str) -> Tuple[bool, str]:
    """
    Logout a user by invalidating their token.
    
    Args:
        token: Authentication token
        
    Returns:
        Tuple of (success, message)
    """
    storage: InMemoryStorage = get_storage()
    
    if storage.remove_token(token):
        return True, "Logout successful"
    else:
        return False, "Invalid token"


def verify_token(token: str) -> Tuple[bool, Optional[UserResponse]]:
    """
    Verify if a token is valid and return the associated user.
    
    Args:
        token: Authentication token
        
    Returns:
        Tuple of (is_valid, user_response)
    """
    storage: InMemoryStorage = get_storage()
    
    username = storage.get_username_by_token(token)
    
    if not username:
        return False, None
    
    user = storage.get_user_by_username(username)
    
    if not user:
        return False, None
    
    return True, user_to_response(user)


def get_user_from_token(token: str) -> Optional[User]:
    """
    Get the full user object from a token.
    
    Args:
        token: Authentication token
        
    Returns:
        User object or None
    """
    storage: InMemoryStorage = get_storage()
    
    username = storage.get_username_by_token(token)
    
    if not username:
        return None
    
    return storage.get_user_by_username(username)

