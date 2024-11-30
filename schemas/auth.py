from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Token(BaseModel):
    """
    Schema for authentication token response.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of token (e.g., 'bearer')")

class TokenData(BaseModel):
    """
    Schema for decoded token data.
    """
    username: Optional[str] = Field(None, description="Username stored in the token")

class UserBase(BaseModel):
    """
    Base schema for user data.
    """
    username: str = Field(..., description="Unique username", min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, description="User's email address")

class UserCreate(UserBase):
    """
    Schema for user creation request.
    """
    password: str = Field(..., description="User's password", min_length=8)

class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="User's password")

class User(UserBase):
    """
    Schema for user response.
    """
    id: int = Field(..., description="Unique user ID")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether the user has admin privileges")

    class Config:
        orm_mode = True
