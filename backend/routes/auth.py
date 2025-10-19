"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from models.auth import UserSignup, UserLogin, TokenResponse, UserResponse
from utils.supabase_auth import signup, login, logout, verify_token
from utils.middleware import get_token_from_header, verify_auth_token

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad Request"}
    }
)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup_endpoint(signup_data: UserSignup):
    """
    Register a new user.
    
    - **username**: Unique username (3-50 characters)
    - **password**: Password (minimum 6 characters)
    - **email**: Valid email address
    
    Returns authentication token and user information.
    """
    success, message, token_response = signup(signup_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return token_response


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(login_data: UserLogin):
    """
    Authenticate a user and receive a token.
    
    - **username**: Username
    - **password**: Password
    
    Returns authentication token and user information.
    """
    success, message, token_response = login(login_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    return token_response


@router.post("/logout")
async def logout_endpoint(token: str = Depends(get_token_from_header)) -> Dict[str, str]:
    """
    Logout the current user by invalidating their token.
    
    Requires valid authentication token in Authorization header.
    """
    success, message = logout(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    return {"message": message}


@router.get("/verify", response_model=UserResponse)
async def verify_endpoint(current_user: UserResponse = Depends(verify_auth_token)):
    """
    Verify if the current token is valid and return user information.
    
    Requires valid authentication token in Authorization header.
    """
    return current_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: UserResponse = Depends(verify_auth_token)):
    """
    Get the current authenticated user's information.
    
    Requires valid authentication token in Authorization header.
    """
    return current_user


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for the authentication service.
    """
    return {
        "status": "healthy",
        "service": "authentication"
    }

