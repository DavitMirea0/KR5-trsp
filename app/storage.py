from typing import Dict, List, Optional
from app.schemas import Task, TaskCreate, TaskStatus


class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1
    
    def create(self, task_data: TaskCreate, owner_id: int) -> Task:
        task = Task(
            id=self._next_id,
            **task_data.model_dump(),
            owner_id=owner_id
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def get_by_owner(self, owner_id: int, status: Optional[str] = None, 
                     min_priority: Optional[int] = None) -> List[Task]:
        tasks = [t for t in self._tasks.values() if t.owner_id == owner_id]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if min_priority is not None:
            tasks = [t for t in tasks if t.priority >= min_priority]
        
        return tasks
    
    def update_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
        return task
    
    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())
    
    def clear(self):
        self._tasks.clear()
        self._next_id = 1


_task_storage = TaskStorage()


def get_storage() -> TaskStorage:
    return _task_storage