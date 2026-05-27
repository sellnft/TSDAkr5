from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # В реальном приложении здесь был бы запрос к БД
    # Для демонстрации возвращаем базовую информацию
    return {"id": user_id, "name": f"User {user_id}"}