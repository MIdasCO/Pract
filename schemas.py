from typing import Optional, List, Dict, Annotated
from pydantic import BaseModel, Field
from datetime import datetime

# Task schemas
class TaskBase(BaseModel):
    name: str
    deadline: datetime
    text:  str
    task_status: str
    
class TaskCreate(TaskBase):
    pass


class TaskSchema(TaskBase):
    id: int
    class Config:
        orm_mode = True

# User schemas
class UserLoginSchema(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    name: str
    email: str
    password: str

class UserCreate(UserBase):
    pass

class UserSchema(UserBase):
    id: int 

    class Config:
        orm_mode = True