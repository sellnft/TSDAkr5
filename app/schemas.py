from pydantic import BaseModel, Field, validator
from typing import Optional
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

class Task(TaskCreate):
    id: int
    owner_id: int

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class User(BaseModel):
    id: int
    role: str

class HealthResponse(BaseModel):
    status: str
    env: str

class RoomUsersResponse(BaseModel):
    room_id: str
    users: list[str]

class StatsResponse(BaseModel):
    total_tasks: int
    by_status: dict[str, int]