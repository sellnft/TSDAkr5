from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import require_admin, get_storage, User
from app.storage import TaskStorage
from app.schemas import StatsResponse
from collections import Counter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/admin/stats", response_model=StatsResponse)
async def get_stats(
    admin_user: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    all_tasks = storage.get_all_tasks()
    status_counts = Counter(task.status.value for task in all_tasks)
    
    return StatsResponse(
        total_tasks=len(all_tasks),
        by_status={
            "todo": status_counts.get("todo", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "done": status_counts.get("done", 0)
        }
    )

@router.delete("/admin/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin_user: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")