"""
Task data structures for Brain System.

Defines tasks that the Brain System plans and manages.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class TaskType(Enum):
    """Types of tasks the Brain System can plan."""
    FIX_POSE = "fix_pose"
    REFINE_ANATOMY = "refine_anatomy"
    ENHANCE_SILHOUETTE = "enhance_silhouette"
    FIX_PROPORTIONS = "fix_proportions"
    IMPROVE_SYMMETRY = "improve_symmetry"
    ALIGN_EDGES = "align_edges"
    FIX_HAND = "fix_hand"
    FIX_FACE = "fix_face"
    ADD_DETAIL = "add_detail"
    CORRECT_STRUCTURE = "correct_structure"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = 1  # Structural issues that must be fixed
    HIGH = 2      # Important issues affecting overall quality
    MEDIUM = 3    # Noticeable issues that should be addressed
    LOW = 4       # Minor refinements


@dataclass
class Task:
    """
    Represents a task the Brain System needs to accomplish.
    
    Attributes:
        task_id: Unique identifier for the task
        task_type: Type of task
        description: Human-readable description
        priority: Task priority level
        status: Current status
        target_area: Region of canvas to focus on (x, y, width, height)
        parameters: Task-specific parameters
        created_at: When task was created
        completed_at: When task was completed
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts allowed
        error_message: Error message if task failed
    """
    task_id: str
    task_type: TaskType
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    target_area: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    
    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_failed(self, error_message: str):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries
    
    def retry(self):
        """Reset task for retry."""
        if not self.can_retry():
            raise ValueError(f"Task {self.task_id} exceeded max retries")
        self.status = TaskStatus.PENDING
        self.error_message = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "target_area": self.target_area,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
        }
