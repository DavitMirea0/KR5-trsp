from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, User

router = APIRouter(prefix="/users", tags=["users"])


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/{user_id}", response_model=dict)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> dict:
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"id": user_id, "role": "user" if user_id != 1 else "admin"}