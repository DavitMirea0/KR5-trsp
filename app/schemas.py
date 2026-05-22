from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = Field(..., ge=1, le=5)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters')
        if len(v) > 80:
            raise ValueError('Title must be at most 80 characters')
        return v.strip()


class Task(TaskCreate):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class User(BaseModel):
    id: int
    role: str = "user"


class HealthResponse(BaseModel):
    status: str
    version: str


class RoomUsersResponse(BaseModel):
    room_id: str
    users: List[str]


class AdminStatsResponse(BaseModel):
    total_tasks: int
    by_status: Dict[str, int]