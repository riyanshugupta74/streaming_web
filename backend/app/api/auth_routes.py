"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.auth import authenticate_user, create_access_token, get_current_user, hash_password
from app.schemas import LoginRequest, SignupRequest, TokenResponse, UserOut
from app.models import User
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new viewer and return a JWT access token."""
    new_user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="viewer"
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    token = create_access_token(new_user.id, new_user.email, new_user.role)
    return TokenResponse(
        access_token=token,
        role=new_user.role,
        email=new_user.email,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and receive a JWT access token."""
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id, user.email, user.role)
    return TokenResponse(
        access_token=token,
        role=user.role,
        email=user.email,
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user."""
    return current_user
