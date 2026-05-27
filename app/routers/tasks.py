from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas import TaskCreate, Task, TaskStatusUpdate, TaskStatus
from app.storage import TaskStorage
from app.dependencies import get_current_user, get_storage, User

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.create_task(task_data.dict(), current_user.id)
    return task

@router.get("/tasks", response_model=list[Task])
async def get_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    min_priority: Optional[int] = Query(None, alias="min_priority"),
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    tasks = storage.get_user_tasks(current_user.id, status_filter, min_priority)
    return tasks

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/tasks/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = storage.update_task_status(task_id, status_update.status)
    return updated_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_task(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    storage.delete_task(task_id)