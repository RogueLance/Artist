"""
Task Manager for Brain System.

Manages task lifecycle, prioritization, and scheduling.
"""

import uuid
from typing import List, Optional, Dict, Any
import logging

from brain.models.task import Task, TaskType, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages tasks for the Brain System.
    
    Handles task creation, prioritization, scheduling, and lifecycle management.
    """
    
    def __init__(self):
        """Initialize Task Manager."""
        self.tasks: Dict[str, Task] = {}
        logger.info("TaskManager initialized")
    
    def create_task(
        self,
        task_type: TaskType,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        target_area: Optional[Dict[str, float]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Create a new task.
        
        Args:
            task_type: Type of task
            description: Human-readable description
            priority: Task priority level
            target_area: Target region on canvas
            parameters: Task-specific parameters
            
        Returns:
            Created Task object
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            description=description,
            priority=priority,
            target_area=target_area,
            parameters=parameters or {}
        )
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id}: {task_type.value} - {description}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get all tasks with a specific priority."""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks, sorted by priority."""
        pending = self.get_tasks_by_status(TaskStatus.PENDING)
        return sorted(pending, key=lambda t: t.priority.value)
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active tasks."""
        return self.get_tasks_by_status(TaskStatus.IN_PROGRESS)
    
    def update_task_status(self, task_id: str, status: TaskStatus, error_message: Optional[str] = None):
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            error_message: Error message if failed
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return
        
        if status == TaskStatus.IN_PROGRESS:
            task.mark_in_progress()
        elif status == TaskStatus.COMPLETED:
            task.mark_completed()
        elif status == TaskStatus.FAILED:
            task.mark_failed(error_message or "Unknown error")
        else:
            task.status = status
        
        logger.info(f"Task {task_id} status updated to {status.value}")
    
    def retry_task(self, task_id: str) -> bool:
        """
        Retry a failed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was reset for retry, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return False
        
        if not task.can_retry():
            logger.warning(f"Task {task_id} exceeded max retries")
            return False
        
        task.retry()
        logger.info(f"Task {task_id} reset for retry (attempt {task.retry_count})")
        return True
    
    def clear_completed_tasks(self):
        """Remove completed tasks from the manager."""
        completed_ids = [task_id for task_id, task in self.tasks.items() 
                        if task.status == TaskStatus.COMPLETED]
        for task_id in completed_ids:
            del self.tasks[task_id]
        logger.info(f"Cleared {len(completed_ids)} completed tasks")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get task statistics."""
        stats = {
            "total": len(self.tasks),
            "pending": len(self.get_tasks_by_status(TaskStatus.PENDING)),
            "in_progress": len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS)),
            "completed": len(self.get_tasks_by_status(TaskStatus.COMPLETED)),
            "failed": len(self.get_tasks_by_status(TaskStatus.FAILED)),
            "cancelled": len(self.get_tasks_by_status(TaskStatus.CANCELLED)),
        }
        return stats
