from typing import Dict, List, Optional
from app.schemas import Task, TaskStatus

class TaskStorage:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1
    
    def create_task(self, task_data: dict, owner_id: int) -> Task:
        task = Task(
            id=self.next_id,
            owner_id=owner_id,
            **task_data
        )
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task
    
    def get_user_tasks(self, owner_id: int, status: Optional[str] = None, 
                      min_priority: Optional[int] = None) -> List[Task]:
        tasks = [task for task in self.tasks.values() if task.owner_id == owner_id]
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        if min_priority:
            tasks = [task for task in tasks if task.priority >= min_priority]
        
        return tasks
    
    def get_task(self, task_id: int) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        if task_id in self.tasks:
            task = self.tasks[task_id]
            updated_task = task.copy(update={"status": status})
            self.tasks[task_id] = updated_task
            return updated_task
        return None
    
    def delete_task(self, task_id: int) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())
    
    def clear(self):
        """Для тестов"""
        self.tasks.clear()
        self.next_id = 1