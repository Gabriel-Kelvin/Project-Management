"""
Supabase-based authentication system for persistent user storage.
"""
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Tuple
from models.auth import User, UserSignup, UserLogin, TokenResponse, UserResponse
from utils.config import get_supabase_client


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return f"user_{secrets.token_hex(8)}"


def generate_token() -> str:
    """Generate a unique authentication token."""
    return secrets.token_urlsafe(32)


def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse."""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )


def signup(signup_data: UserSignup) -> Tuple[bool, str, Optional[TokenResponse]]:
    """
    Register a new user in Supabase.
    
    Args:
        signup_data: User signup data
        
    Returns:
        Tuple of (success, message, token_response)
    """
    try:
        supabase = get_supabase_client()
        
        # Check if username already exists
        username_check = supabase.table('users').select('username').eq('username', signup_data.username).execute()
        if username_check.data:
            return False, "Username already exists", None
        
        # Check if email already exists
        email_check = supabase.table('users').select('email').eq('email', signup_data.email).execute()
        if email_check.data:
            return False, "Email already exists", None
        
        # Create new user
        user_id = generate_user_id()
        hashed_password = hash_password(signup_data.password)
        
        new_user_data = {
            'id': user_id,
            'username': signup_data.username,
            'password': hashed_password,
            'email': signup_data.email,
            'created_at': datetime.now().isoformat()
        }
        
        # Insert user into Supabase
        result = supabase.table('users').insert(new_user_data).execute()
        
        if not result.data:
            return False, "Failed to create user", None
        
        # Create User object for response
        new_user = User(
            id=user_id,
            username=signup_data.username,
            password=hashed_password,
            email=signup_data.email,
            created_at=datetime.now()
        )
        
        # Generate token
        token = generate_token()
        
        # Store token in Supabase
        token_data = {
            'token': token,
            'username': signup_data.username,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('auth_tokens').insert(token_data).execute()
        
        # Create response
        token_response = TokenResponse(
            token=token,
            user=user_to_response(new_user)
        )
        
        return True, "User registered successfully", token_response
        
    except Exception as e:
        return False, f"Registration failed: {str(e)}", None


def login(login_data: UserLogin) -> Tuple[bool, str, Optional[TokenResponse]]:
    """
    Authenticate a user using Supabase.
    
    Args:
        login_data: User login credentials
        
    Returns:
        Tuple of (success, message, token_response)
    """
    try:
        supabase = get_supabase_client()
        
        # Get user by username
        result = supabase.table('users').select('*').eq('username', login_data.username).execute()
        
        if not result.data:
            return False, "Invalid username or password", None
        
        user_data = result.data[0]
        
        # Verify password
        if not verify_password(login_data.password, user_data['password']):
            return False, "Invalid username or password", None
        
        # Create User object
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            created_at=datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
        )
        
        # Generate new token
        token = generate_token()
        
        # Store token in Supabase
        token_data = {
            'token': token,
            'username': user.username,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('auth_tokens').insert(token_data).execute()
        
        # Create response
        token_response = TokenResponse(
            token=token,
            user=user_to_response(user)
        )
        
        return True, "Login successful", token_response
        
    except Exception as e:
        return False, f"Login failed: {str(e)}", None


def logout(token: str) -> Tuple[bool, str]:
    """
    Logout user by removing token from Supabase.
    
    Args:
        token: Authentication token
        
    Returns:
        Tuple of (success, message)
    """
    try:
        supabase = get_supabase_client()
        
        # Remove token from Supabase
        result = supabase.table('auth_tokens').delete().eq('token', token).execute()
        
        if result.data:
            return True, "Logout successful"
        else:
            return False, "Token not found"
            
    except Exception as e:
        return False, f"Logout failed: {str(e)}"


def verify_token(token: str) -> Tuple[bool, str, Optional[User]]:
    """
    Verify token and return user information from Supabase.
    
    Args:
        token: Authentication token
        
    Returns:
        Tuple of (success, message, user)
    """
    try:
        supabase = get_supabase_client()
        
        # Check if token exists
        token_result = supabase.table('auth_tokens').select('username').eq('token', token).execute()
        
        if not token_result.data:
            return False, "Invalid token", None
        
        username = token_result.data[0]['username']
        
        # Get user data
        user_result = supabase.table('users').select('*').eq('username', username).execute()
        
        if not user_result.data:
            return False, "User not found", None
        
        user_data = user_result.data[0]
        
        # Create User object
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            created_at=datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
        )
        
        return True, "Token valid", user
        
    except Exception as e:
        return False, f"Token verification failed: {str(e)}", None
