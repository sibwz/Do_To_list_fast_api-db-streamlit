from pydantic import BaseModel, EmailStr

from datetime import datetime
from typing import Optional
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class ShowUser(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True



class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None  # ✅ this must be here

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    done: Optional[bool]  # ✅ This must be here!

class ShowTask(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    done: bool

    class Config:
        from_attributes = True
