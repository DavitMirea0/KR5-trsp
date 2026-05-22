from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import require_admin, User
from app.storage import TaskStorage, get_storage
from app.schemas import AdminStatsResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
) -> AdminStatsResponse:
    all_tasks = storage.get_all_tasks()
    
    by_status = {
        "todo": 0,
        "in_progress": 0,
        "done": 0
    }
    
    for task in all_tasks:
        by_status[task.status] = by_status.get(task.status, 0) + 1
    
    return AdminStatsResponse(
        total_tasks=len(all_tasks),
        by_status=by_status
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
) -> None:
    if not storage.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")