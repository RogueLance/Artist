"""
Brain System - Planning and Decision Making Engine for Cerebrum AI Art Platform.

The Brain System provides the central decision-making capabilities that interpret
visual feedback and plan corrective actions. It mimics cognitive planning by
choosing whether to refine, retry, or stylize based on errors detected by the
Vision System.

Main Components:
    - BrainModule: Primary API for planning and decision-making
    - TaskManager: Task lifecycle management
    - Planner: Translates vision feedback into action plans
    - StateTracker: Tracks goals, tasks, and execution history

Example:
    >>> from brain import BrainModule
    >>> from vision import VisionModule
    >>> from motor import MotorInterface
    >>> 
    >>> # Initialize systems
    >>> brain = BrainModule()
    >>> vision = VisionModule()
    >>> motor = MotorInterface(backend="simulation")
    >>> 
    >>> # Set goal
    >>> brain.set_goal("Draw an accurate human figure")
    >>> 
    >>> # Analyze and plan
    >>> vision_data = vision.analyze("canvas.png")
    >>> tasks = brain.plan_next_action(vision_data)
    >>> 
    >>> # Execute tasks
    >>> for task in tasks:
    ...     plan = brain.get_action_plan(task)
    ...     for action in plan.actions:
    ...         brain.delegate_to_motor(action, motor)
"""

from brain.brain_module import BrainModule
from brain.core import TaskManager, Planner, StateTracker
from brain.models import (
    Task,
    TaskType,
    TaskStatus,
    TaskPriority,
    ActionPlan,
    DrawingAction,
    ActionType,
    BrainState,
    ExecutionHistory,
)

__version__ = "0.1.0"

__all__ = [
    "BrainModule",
    "TaskManager",
    "Planner",
    "StateTracker",
    "Task",
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    "ActionPlan",
    "DrawingAction",
    "ActionType",
    "BrainState",
    "ExecutionHistory",
]
