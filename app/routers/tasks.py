from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from app.schemas import Task, TaskCreate, TaskStatus, TaskStatusUpdate
from app.storage import TaskStorage, get_storage
from app.dependencies import get_current_user, User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> Task:
    return storage.create(task_data, current_user.id)


@router.get("/", response_model=List[Task])
async def get_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    min_priority: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> List[Task]:
    return storage.get_by_owner(current_user.id, status_filter, min_priority)


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> Task:
    task = storage.get_by_id(task_id)
    
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    update_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> Task:
    task = storage.get_by_id(task_id)
    
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = storage.update_status(task_id, update_data.status)
    
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
) -> None:
    task = storage.get_by_id(task_id)
    
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not storage.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")