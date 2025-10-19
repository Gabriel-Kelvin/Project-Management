"""
Authentication models and in-memory user storage.
"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User model for authentication."""
    id: str
    username: str
    password: str  # Plain text for simplicity (not recommended for production)
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "username": "johndoe",
                "password": "password123",
                "email": "johndoe@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class UserSignup(BaseModel):
    """Model for user signup requests."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "password123",
                "email": "johndoe@example.com"
            }
        }


class UserLogin(BaseModel):
    """Model for user login requests."""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "password123"
            }
        }


class UserResponse(BaseModel):
    """Model for user response (without password)."""
    id: str
    username: str
    email: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class TokenResponse(BaseModel):
    """Model for authentication token response."""
    token: str
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123xyz789",
                "user": {
                    "id": "user_123",
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }


# In-memory storage for users and tokens
# Note: This data will be lost when the server restarts
class InMemoryStorage:
    """In-memory storage for users and authentication tokens."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}  # username -> User
        self.tokens: Dict[str, str] = {}  # token -> username
        self.user_ids: Dict[str, User] = {}  # user_id -> User
    
    def add_user(self, user: User) -> None:
        """Add a user to storage."""
        self.users[user.username] = user
        self.user_ids[user.id] = user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.users.get(username)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.user_ids.get(user_id)
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        return username in self.users
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return any(user.email == email for user in self.users.values())
    
    def add_token(self, token: str, username: str) -> None:
        """Add a token for a user."""
        self.tokens[token] = username
    
    def get_username_by_token(self, token: str) -> Optional[str]:
        """Get username by token."""
        return self.tokens.get(token)
    
    def remove_token(self, token: str) -> bool:
        """Remove a token (logout)."""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    def token_exists(self, token: str) -> bool:
        """Check if token exists."""
        return token in self.tokens
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self.users.values())


# Global storage instance
storage = InMemoryStorage()


def get_storage() -> InMemoryStorage:
    """Get the global storage instance."""
    return storage

