"""
Main Brain Module API.

This is the primary interface for the Brain System, providing high-level methods
for planning, decision-making, and task management.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from brain.core.task_manager import TaskManager
from brain.core.planner import Planner
from brain.core.state_tracker import StateTracker
from brain.models.task import Task, TaskType, TaskPriority
from brain.models.action_plan import ActionPlan, DrawingAction
from brain.models.brain_state import ExecutionResult

logger = logging.getLogger(__name__)


class BrainModule:
    """
    Main Brain Module for planning and decision-making.
    
    This class provides the primary API for the Brain System, which interprets
    visual feedback and decides what corrective action or stylistic progression
    should occur. It acts as the central agent that receives vision input and
    decides what to do next.
    
    Example:
        >>> brain = BrainModule()
        >>> brain.set_goal("Draw an accurate human figure")
        >>> 
        >>> # Analyze vision feedback
        >>> vision_data = vision.analyze("canvas.png")
        >>> tasks = brain.plan_next_action(vision_data)
        >>> 
        >>> # Execute tasks
        >>> for task in tasks:
        ...     plan = brain.get_action_plan(task)
        ...     for action in plan.actions:
        ...         brain.delegate_to_motor(action, motor)
        ...     brain.evaluate_result(task, vision_before, vision_after)
    """
    
    def __init__(self):
        """Initialize Brain Module."""
        self.task_manager = TaskManager()
        self.planner = Planner()
        self.state_tracker = StateTracker()
        logger.info("BrainModule initialized")
    
    def set_goal(self, goal: str):
        """
        Set the current artistic goal.
        
        Args:
            goal: High-level artistic goal description
        """
        self.state_tracker.set_goal(goal)
        logger.info(f"Goal set: {goal}")
    
    def get_goal(self) -> Optional[str]:
        """Get the current artistic goal."""
        return self.state_tracker.get_goal()
    
    def plan_next_action(
        self,
        vision_data: Dict[str, Any],
        auto_schedule: bool = True
    ) -> List[Task]:
        """
        Analyze vision feedback and plan next actions.
        
        This method translates vision outputs into drawing plans by:
        1. Analyzing vision feedback for issues
        2. Creating tasks to address issues
        3. Prioritizing tasks
        4. Optionally scheduling tasks automatically
        
        Args:
            vision_data: Vision analysis result from VisionModule
            auto_schedule: Automatically schedule tasks
            
        Returns:
            List of created tasks
        """
        logger.info("Planning next action based on vision feedback")
        
        # Update vision result in state
        self.state_tracker.update_vision_result(vision_data)
        
        # Analyze vision feedback and create tasks
        tasks = self.planner.analyze_vision_feedback(vision_data)
        
        # Add tasks to task manager and state tracker
        for task in tasks:
            self.task_manager.tasks[task.task_id] = task
            if auto_schedule:
                self.state_tracker.add_task(task)
        
        logger.info(f"Created {len(tasks)} tasks from vision analysis")
        return tasks
    
    def get_action_plan(self, task: Task) -> ActionPlan:
        """
        Get action plan for a task.
        
        Creates a concrete action plan with drawing operations to accomplish
        the given task.
        
        Args:
            task: Task to create plan for
            
        Returns:
            ActionPlan with concrete drawing actions
        """
        context = self.state_tracker.get_all_context()
        plan = self.planner.create_action_plan(task, context)
        self.state_tracker.set_action_plan(plan)
        return plan
    
    def evaluate_result(
        self,
        task: Task,
        vision_result_before: Dict[str, Any],
        vision_result_after: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Evaluate the result of a task execution.
        
        Compares vision analysis before and after task execution to determine
        if the task was successful.
        
        Args:
            task: Executed task
            vision_result_before: Vision analysis before execution
            vision_result_after: Vision analysis after execution
            
        Returns:
            ExecutionResult indicating success/failure/partial
        """
        result = self.planner.evaluate_execution_result(
            task, vision_result_before, vision_result_after
        )
        
        # Record execution
        execution_id = str(uuid.uuid4())
        self.state_tracker.record_execution(
            execution_id=execution_id,
            task_id=task.task_id,
            result=result,
            metrics={
                "quality_before": self.planner._calculate_quality_score(vision_result_before),
                "quality_after": self.planner._calculate_quality_score(vision_result_after)
            }
        )
        
        # Update task status
        if result == ExecutionResult.SUCCESS:
            self.state_tracker.complete_task(task)
            self.task_manager.update_task_status(task.task_id, task.status)
        elif result == ExecutionResult.FAILURE:
            if self.planner.should_retry(task, result, task.retry_count):
                self.schedule_refinement_task(task)
            else:
                self.state_tracker.fail_task(task, "Execution failed")
                self.task_manager.update_task_status(task.task_id, task.status)
        else:  # PARTIAL
            if task.priority == TaskPriority.CRITICAL:
                self.schedule_refinement_task(task)
            else:
                self.state_tracker.complete_task(task)
                self.task_manager.update_task_status(task.task_id, task.status)
        
        return result
    
    def schedule_refinement_task(self, task: Task):
        """
        Schedule a task for refinement/retry.
        
        Args:
            task: Task to schedule for refinement
        """
        if task.can_retry():
            self.task_manager.retry_task(task.task_id)
            self.state_tracker.add_task(task)
            logger.info(f"Task {task.task_id} scheduled for refinement (attempt {task.retry_count + 1})")
        else:
            logger.warning(f"Task {task.task_id} cannot be retried (max retries exceeded)")
    
    def delegate_to_motor(
        self,
        action: DrawingAction,
        motor_interface: Any
    ) -> bool:
        """
        Delegate an action to the Motor System.
        
        Translates a DrawingAction into Motor System commands and executes them.
        
        Args:
            action: Drawing action to execute
            motor_interface: MotorInterface instance
            
        Returns:
            True if action was executed successfully
        """
        try:
            if action.action_type.value == "draw_stroke":
                # Convert action to motor stroke
                from motor import Stroke, StrokePoint, ToolPresets
                
                # Get tool configuration
                tool_config = action.tool_config or {"tool_type": "pencil", "size": 2.0}
                tool_type = tool_config.get("tool_type", "pencil")
                size = tool_config.get("size", 2.0)
                
                # Select appropriate tool
                if tool_type == "pencil":
                    motor_interface.switch_tool(ToolPresets.pencil(size=size))
                elif tool_type == "pen":
                    motor_interface.switch_tool(ToolPresets.pen(size=size))
                elif tool_type == "brush":
                    motor_interface.switch_tool(ToolPresets.brush(size=size))
                
                # Create stroke from points
                if action.stroke_points:
                    points = []
                    for pt in action.stroke_points:
                        points.append(StrokePoint(
                            x=pt.get("x", 0),
                            y=pt.get("y", 0),
                            pressure=pt.get("pressure", 0.5)
                        ))
                    stroke = Stroke(points=points)
                    motor_interface.draw_stroke(stroke)
                
                logger.info(f"Action {action.action_id} delegated to Motor")
                return True
            
            elif action.action_type.value == "erase_stroke":
                # Erase action
                from motor import ToolPresets
                tool_config = action.tool_config or {"size": 10.0}
                size = tool_config.get("size", 10.0)
                motor_interface.switch_tool(ToolPresets.eraser(size=size))
                
                # Could implement specific erase logic here
                logger.info(f"Erase action {action.action_id} delegated to Motor")
                return True
            
            elif action.action_type.value == "switch_tool":
                # Tool switch action
                from motor import ToolPresets
                tool_config = action.tool_config or {}
                tool_type = tool_config.get("tool_type", "pencil")
                size = tool_config.get("size", 2.0)
                
                if tool_type == "pencil":
                    motor_interface.switch_tool(ToolPresets.pencil(size=size))
                elif tool_type == "pen":
                    motor_interface.switch_tool(ToolPresets.pen(size=size))
                elif tool_type == "brush":
                    motor_interface.switch_tool(ToolPresets.brush(size=size))
                elif tool_type == "eraser":
                    motor_interface.switch_tool(ToolPresets.eraser(size=size))
                
                logger.info(f"Tool switch action {action.action_id} delegated to Motor")
                return True
            
            else:
                logger.warning(f"Unsupported action type: {action.action_type.value}")
                return False
        
        except Exception as e:
            logger.error(f"Error delegating action {action.action_id} to Motor: {e}")
            return False
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next task to execute."""
        return self.state_tracker.get_next_task()
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active tasks."""
        return self.task_manager.get_active_tasks()
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return self.task_manager.get_pending_tasks()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current brain state."""
        return self.state_tracker.get_summary()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get brain system statistics."""
        stats = {
            "task_stats": self.task_manager.get_statistics(),
            "state_summary": self.state_tracker.get_summary(),
            "iteration_count": self.state_tracker.get_iteration_count(),
        }
        return stats
    
    def increment_iteration(self):
        """Increment the iteration counter."""
        self.state_tracker.increment_iteration()
    
    def reset(self):
        """Reset the brain module."""
        self.task_manager = TaskManager()
        self.state_tracker.reset()
        logger.info("BrainModule reset")
    
    def close(self):
        """Close the brain module and clean up resources."""
        logger.info("BrainModule closed")
