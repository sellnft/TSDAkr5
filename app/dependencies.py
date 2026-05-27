from fastapi import Header, HTTPException, Depends
from app.storage import TaskStorage
from app.schemas import User

# Глобальное хранилище (синглтон)
_task_storage = TaskStorage()

def get_storage() -> TaskStorage:
    return _task_storage

async def get_current_user(x_user_id: str = Header(None, alias="X-User-Id"), x_user_role: str = Header("user", alias="X-User-Role")) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    return User(id=user_id, role=x_user_role)

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user