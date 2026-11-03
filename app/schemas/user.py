from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr

class UserResponse(BaseModel):
    name: str
    email: EmailStr
    created_at: datetime
    id: int

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None