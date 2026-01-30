from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

# O que chega da web para a API
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# O que a API devolve para a web
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str

    class Config:
        from_attributes = True
