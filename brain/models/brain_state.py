"""
Brain State data structures.

Tracks the current state of the Brain System including goals, history, and context.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from brain.models.task import Task, TaskStatus
from brain.models.action_plan import ActionPlan


class ExecutionResult(Enum):
    """Result of an execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass
class ExecutionHistory:
    """
    Record of an executed action or task.
    
    Attributes:
        execution_id: Unique identifier
        task_id: Associated task ID
        action_id: Associated action ID (if applicable)
        result: Execution result
        timestamp: When execution occurred
        metrics: Metrics collected during execution
        error_message: Error message if failed
    """
    execution_id: str
    task_id: str
    action_id: Optional[str] = None
    result: ExecutionResult = ExecutionResult.SUCCESS
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "action_id": self.action_id,
            "result": self.result.value,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "error_message": self.error_message,
        }


@dataclass
class BrainState:
    """
    Current state of the Brain System.
    
    Tracks goals, tasks, history, and context for decision-making.
    
    Attributes:
        current_goal: High-level artistic goal
        active_tasks: Currently active tasks
        pending_tasks: Tasks waiting to be executed
        completed_tasks: Completed tasks
        failed_tasks: Failed tasks
        current_action_plan: Currently executing action plan
        execution_history: History of all executions
        context: Additional context information
        iteration_count: Number of refinement iterations
        last_vision_result: Last vision analysis result
        last_action_time: Timestamp of last action
    """
    current_goal: Optional[str] = None
    active_tasks: List[Task] = field(default_factory=list)
    pending_tasks: List[Task] = field(default_factory=list)
    completed_tasks: List[Task] = field(default_factory=list)
    failed_tasks: List[Task] = field(default_factory=list)
    current_action_plan: Optional[ActionPlan] = None
    execution_history: List[ExecutionHistory] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    iteration_count: int = 0
    last_vision_result: Optional[Dict[str, Any]] = None
    last_action_time: Optional[datetime] = None
    
    def add_task(self, task: Task):
        """Add a new task to pending tasks."""
        self.pending_tasks.append(task)
        # Sort by priority
        self.pending_tasks.sort(key=lambda t: t.priority.value)
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next pending task."""
        if self.pending_tasks:
            return self.pending_tasks[0]
        return None
    
    def activate_task(self, task: Task):
        """Move task from pending to active."""
        if task in self.pending_tasks:
            self.pending_tasks.remove(task)
        if task not in self.active_tasks:
            self.active_tasks.append(task)
        task.mark_in_progress()
    
    def complete_task(self, task: Task):
        """Mark task as completed."""
        if task in self.active_tasks:
            self.active_tasks.remove(task)
        if task not in self.completed_tasks:
            self.completed_tasks.append(task)
        task.mark_completed()
    
    def fail_task(self, task: Task, error_message: str):
        """Mark task as failed."""
        if task in self.active_tasks:
            self.active_tasks.remove(task)
        task.mark_failed(error_message)
        
        # Check if can retry
        if task.can_retry():
            task.retry()
            self.pending_tasks.append(task)
            self.pending_tasks.sort(key=lambda t: t.priority.value)
        else:
            self.failed_tasks.append(task)
    
    def record_execution(self, history: ExecutionHistory):
        """Record an execution in history."""
        self.execution_history.append(history)
        self.last_action_time = datetime.now()
    
    def get_recent_executions(self, limit: int = 10) -> List[ExecutionHistory]:
        """Get recent execution history."""
        return self.execution_history[-limit:]
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by ID."""
        for task in self.active_tasks + self.pending_tasks + self.completed_tasks + self.failed_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def increment_iteration(self):
        """Increment the iteration counter."""
        self.iteration_count += 1
    
    def update_vision_result(self, vision_result: Dict[str, Any]):
        """Update the last vision analysis result."""
        self.last_vision_result = vision_result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current state."""
        return {
            "current_goal": self.current_goal,
            "active_tasks": len(self.active_tasks),
            "pending_tasks": len(self.pending_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "iteration_count": self.iteration_count,
            "total_executions": len(self.execution_history),
            "has_active_plan": self.current_action_plan is not None,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "current_goal": self.current_goal,
            "active_tasks": [t.to_dict() for t in self.active_tasks],
            "pending_tasks": [t.to_dict() for t in self.pending_tasks],
            "completed_tasks": [t.to_dict() for t in self.completed_tasks],
            "failed_tasks": [t.to_dict() for t in self.failed_tasks],
            "current_action_plan": self.current_action_plan.to_dict() if self.current_action_plan else None,
            "execution_history": [h.to_dict() for h in self.execution_history],
            "context": self.context,
            "iteration_count": self.iteration_count,
            "last_vision_result": self.last_vision_result,
            "last_action_time": self.last_action_time.isoformat() if self.last_action_time else None,
        }
