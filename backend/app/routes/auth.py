import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    LogoutResponse
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

logger = logging.getLogger("agripulse.routes.auth")

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
    description="Creates a new user account with secure bcrypt password hashing and returns the registered user profile."
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    user = AuthService.register_user(db=db, request=request)
    return ApiResponse[UserResponse](
        success=True,
        data=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate User and Issue JWT Token",
    description="Validates user credentials (email & password) and returns a signed JWT access token."
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )
    token_response = AuthService.generate_token_response(user=user)
    return ApiResponse[TokenResponse](
        success=True,
        data=token_response
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Current Authenticated User Profile",
    description="Returns the active user profile associated with the Bearer JWT token."
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return ApiResponse[UserResponse](
        success=True,
        data=UserResponse.model_validate(current_user)
    )


@router.post(
    "/logout",
    response_model=ApiResponse[LogoutResponse],
    status_code=status.HTTP_200_OK,
    summary="Log Out User",
    description="Stateless token logout endpoint confirming client session termination."
)
def logout(
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User id={current_user.id} logged out.")
    return ApiResponse[LogoutResponse](
        success=True,
        message="Logged out successfully",
        data=LogoutResponse(message="Logged out successfully")
    )
