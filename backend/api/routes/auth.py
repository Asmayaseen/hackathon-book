"""
Authentication API Routes (+30 points)
JWT-based auth with user profiles
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    profile_type: str = "undergraduate"  # undergraduate, graduate, professional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    id: int
    email: str
    profile_type: str
    created_at: str


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """
    User Signup
    - Validates email/password
    - Hashes password with bcrypt
    - Stores in database
    - Returns JWT token
    """
    try:
        # TODO: Implement signup
        # 1. Check if email exists
        # 2. Hash password
        # 3. Create user in database
        # 4. Generate JWT token
        # 5. Return token + user data

        return TokenResponse(
            access_token="placeholder-jwt-token",
            user={
                "id": 1,
                "email": request.email,
                "profile_type": request.profile_type
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User Login"""
    # TODO: Implement login
    # 1. Find user by email
    # 2. Verify password hash
    # 3. Generate JWT token
    # 4. Return token + user data

    return TokenResponse(
        access_token="placeholder-jwt-token",
        user={"id": 1, "email": request.email, "profile_type": "undergraduate"}
    )


@router.get("/profile", response_model=UserProfile)
async def get_profile():
    """Get current user profile"""
    # TODO: Implement JWT verification and profile fetch
    return UserProfile(
        id=1,
        email="user@example.com",
        profile_type="undergraduate",
        created_at="2025-11-29T00:00:00Z"
    )
