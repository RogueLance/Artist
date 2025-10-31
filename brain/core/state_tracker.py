"""
State Tracker for Brain System.

Tracks the current state of the Brain System including goals, context, and history.
"""

import logging
from typing import Optional, Dict, Any, List

from brain.models.brain_state import BrainState, ExecutionHistory, ExecutionResult
from brain.models.task import Task
from brain.models.action_plan import ActionPlan

logger = logging.getLogger(__name__)


class StateTracker:
    """
    Tracks the state of the Brain System.
    
    Maintains current goals, tasks, execution history, and context.
    """
    
    def __init__(self):
        """Initialize State Tracker."""
        self.state = BrainState()
        logger.info("StateTracker initialized")
    
    def set_goal(self, goal: str):
        """
        Set the current artistic goal.
        
        Args:
            goal: High-level artistic goal description
        """
        self.state.current_goal = goal
        logger.info(f"Goal set: {goal}")
    
    def get_goal(self) -> Optional[str]:
        """Get the current goal."""
        return self.state.current_goal
    
    def add_task(self, task: Task):
        """Add a task to pending tasks."""
        self.state.add_task(task)
        logger.debug(f"Task added: {task.task_id}")
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next task to execute."""
        return self.state.get_next_task()
    
    def activate_task(self, task: Task):
        """Activate a task."""
        self.state.activate_task(task)
        logger.info(f"Task activated: {task.task_id}")
    
    def complete_task(self, task: Task):
        """Complete a task."""
        self.state.complete_task(task)
        logger.info(f"Task completed: {task.task_id}")
    
    def fail_task(self, task: Task, error_message: str):
        """Mark a task as failed."""
        self.state.fail_task(task, error_message)
        logger.warning(f"Task failed: {task.task_id} - {error_message}")
    
    def set_action_plan(self, plan: ActionPlan):
        """Set the current action plan."""
        self.state.current_action_plan = plan
        logger.info(f"Action plan set: {plan.plan_id}")
    
    def get_action_plan(self) -> Optional[ActionPlan]:
        """Get the current action plan."""
        return self.state.current_action_plan
    
    def clear_action_plan(self):
        """Clear the current action plan."""
        self.state.current_action_plan = None
        logger.debug("Action plan cleared")
    
    def record_execution(
        self,
        execution_id: str,
        task_id: str,
        result: ExecutionResult,
        action_id: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """
        Record an execution in history.
        
        Args:
            execution_id: Unique execution identifier
            task_id: Associated task ID
            result: Execution result
            action_id: Associated action ID (optional)
            metrics: Execution metrics
            error_message: Error message if failed
        """
        history = ExecutionHistory(
            execution_id=execution_id,
            task_id=task_id,
            action_id=action_id,
            result=result,
            metrics=metrics or {},
            error_message=error_message
        )
        self.state.record_execution(history)
        logger.debug(f"Execution recorded: {execution_id}")
    
    def get_recent_executions(self, limit: int = 10) -> List[ExecutionHistory]:
        """Get recent execution history."""
        return self.state.get_recent_executions(limit)
    
    def increment_iteration(self):
        """Increment the iteration counter."""
        self.state.increment_iteration()
        logger.info(f"Iteration count: {self.state.iteration_count}")
    
    def get_iteration_count(self) -> int:
        """Get the current iteration count."""
        return self.state.iteration_count
    
    def update_vision_result(self, vision_result: Dict[str, Any]):
        """Update the last vision analysis result."""
        self.state.update_vision_result(vision_result)
        logger.debug("Vision result updated")
    
    def get_last_vision_result(self) -> Optional[Dict[str, Any]]:
        """Get the last vision analysis result."""
        return self.state.last_vision_result
    
    def update_context(self, key: str, value: Any):
        """Update a context value."""
        self.state.context[key] = value
        logger.debug(f"Context updated: {key}")
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get a context value."""
        return self.state.context.get(key)
    
    def get_all_context(self) -> Dict[str, Any]:
        """Get all context."""
        return self.state.context.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current state."""
        return self.state.get_summary()
    
    def get_state(self) -> BrainState:
        """Get the current brain state."""
        return self.state
    
    def reset(self):
        """Reset the state tracker."""
        self.state = BrainState()
        logger.info("State tracker reset")
