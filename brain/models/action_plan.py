"""
Action Plan data structures for Brain System.

Defines action plans that translate tasks into executable drawing operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class ActionType(Enum):
    """Types of drawing actions."""
    DRAW_STROKE = "draw_stroke"
    ERASE_STROKE = "erase_stroke"
    SWITCH_TOOL = "switch_tool"
    CHANGE_LAYER = "change_layer"
    ADJUST_COLOR = "adjust_color"
    REFINE_AREA = "refine_area"


@dataclass
class DrawingAction:
    """
    Represents a single drawing action to execute.
    
    Attributes:
        action_id: Unique identifier
        action_type: Type of action
        description: Human-readable description
        tool_config: Tool configuration for this action
        stroke_points: List of stroke points if drawing
        target_region: Target region (x, y, width, height)
        parameters: Action-specific parameters
        estimated_duration: Estimated time to execute (seconds)
    """
    action_id: str
    action_type: ActionType
    description: str
    tool_config: Optional[Dict[str, Any]] = None
    stroke_points: Optional[List[Dict[str, float]]] = None
    target_region: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "description": self.description,
            "tool_config": self.tool_config,
            "stroke_points": self.stroke_points,
            "target_region": self.target_region,
            "parameters": self.parameters,
            "estimated_duration": self.estimated_duration,
        }


@dataclass
class ActionPlan:
    """
    Represents a plan of actions to accomplish a task.
    
    Attributes:
        plan_id: Unique identifier
        task_id: Associated task ID
        actions: List of actions to execute
        created_at: When plan was created
        estimated_total_duration: Total estimated time (seconds)
        success_criteria: Criteria for evaluating success
    """
    plan_id: str
    task_id: str
    actions: List[DrawingAction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    estimated_total_duration: float = 0.0
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    def add_action(self, action: DrawingAction):
        """Add an action to the plan."""
        self.actions.append(action)
        self.estimated_total_duration += action.estimated_duration
    
    def get_next_action(self) -> Optional[DrawingAction]:
        """Get the next action to execute."""
        if self.actions:
            return self.actions[0]
        return None
    
    def remove_action(self, action_id: str) -> bool:
        """Remove an action from the plan."""
        for i, action in enumerate(self.actions):
            if action.action_id == action_id:
                removed = self.actions.pop(i)
                self.estimated_total_duration -= removed.estimated_duration
                return True
        return False
    
    def is_complete(self) -> bool:
        """Check if all actions are complete."""
        return len(self.actions) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "plan_id": self.plan_id,
            "task_id": self.task_id,
            "actions": [action.to_dict() for action in self.actions],
            "created_at": self.created_at.isoformat(),
            "estimated_total_duration": self.estimated_total_duration,
            "success_criteria": self.success_criteria,
        }
