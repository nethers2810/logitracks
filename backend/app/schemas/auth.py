from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    admin = "admin"
    planner = "planner"
    analyst = "analyst"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
