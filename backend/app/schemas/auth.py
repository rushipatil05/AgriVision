from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Kisan Sharma"})
    email: EmailStr = Field(..., json_schema_extra={"example": "kisan.sharma@example.com"})
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters long",
        json_schema_extra={"example": "AgriPulse#2026"}
    )


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "kisan.sharma@example.com"})
    password: str = Field(..., min_length=1, json_schema_extra={"example": "AgriPulse#2026"})


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Bearer token")
    token_type: str = Field("bearer", description="Token authentication scheme")
    expires_in: int = Field(..., description="Token validity duration in seconds", json_schema_extra={"example": 3600})
    user: UserResponse = Field(..., description="Authenticated user profile details")


class LogoutResponse(BaseModel):
    message: str = Field(default="Successfully logged out")
