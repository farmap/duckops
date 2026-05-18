from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: str
    theme: str = "dark"

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    theme: Optional[str] = None

class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True
