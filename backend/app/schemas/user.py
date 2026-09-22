import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Kisan Sharma"})
    email: EmailStr = Field(..., json_schema_extra={"example": "kisan.sharma@example.com"})


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters long")


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
