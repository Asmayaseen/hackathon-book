"""
Authentication API Routes (+50 points)
JWT-based auth with user profiles and background questions
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    software_experience = Column(String(50))
    hardware_experience = Column(String(50))
    learning_goal = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables if database is available
if engine:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database table creation warning: {e}")


# Pydantic models
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    software_experience: str = "beginner"
    hardware_experience: str = "beginner"
    learning_goal: str = ""


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    software_experience: str
    hardware_experience: str
    learning_goal: str
    created_at: str


# Database dependency
def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper functions
def hash_password(password: str) -> str:
    # Truncate password to 72 bytes to avoid bcrypt error
    return pwd_context.hash(password.encode('utf-8')[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password.encode('utf-8')[:72], hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# Routes
@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    User Signup with Background Questions (+50 points)
    - Validates email/password
    - Hashes password with bcrypt
    - Stores user profile with software/hardware experience
    - Returns JWT token
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_pw = hash_password(request.password)
        new_user = User(
            name=request.name,
            email=request.email,
            hashed_password=hashed_pw,
            software_experience=request.software_experience,
            hardware_experience=request.hardware_experience,
            learning_goal=request.learning_goal
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT token
        access_token = create_access_token(data={"sub": new_user.email})

        return TokenResponse(
            access_token=access_token,
            user={
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "software_experience": new_user.software_experience,
                "hardware_experience": new_user.hardware_experience,
                "learning_goal": new_user.learning_goal
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")


@router.post("/signin", response_model=TokenResponse)
async def signin(request: SigninRequest, db: Session = Depends(get_db)):
    """
    User Signin
    - Verifies email and password
    - Returns JWT token
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate JWT token
        access_token = create_access_token(data={"sub": user.email})

        return TokenResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "software_experience": user.software_experience,
                "hardware_experience": user.hardware_experience,
                "learning_goal": user.learning_goal
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signin error: {str(e)}")


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        software_experience=current_user.software_experience,
        hardware_experience=current_user.hardware_experience,
        learning_goal=current_user.learning_goal,
        created_at=current_user.created_at.isoformat()
    )


@router.get("/health")
async def auth_health_check():
    """Check authentication system health"""
    return {
        "status": "healthy",
        "database": "connected" if SessionLocal else "not configured",
        "jwt": "configured" if SECRET_KEY != "default-secret-key-change-in-production" else "using default key"
    }
