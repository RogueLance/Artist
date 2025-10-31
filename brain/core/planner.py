"""
Planner for Brain System.

Translates vision analysis into actionable drawing plans.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List

from brain.models.task import Task, TaskType, TaskPriority
from brain.models.action_plan import ActionPlan, DrawingAction, ActionType
from brain.models.brain_state import ExecutionResult

logger = logging.getLogger(__name__)


class Planner:
    """
    Plans drawing actions based on vision analysis and task requirements.
    
    This component translates high-level tasks and vision feedback into
    concrete drawing actions that can be executed by the Motor System.
    """
    
    def __init__(self):
        """Initialize Planner."""
        self.default_stroke_length = 5  # Number of points in default stroke
        logger.info("Planner initialized")
    
    def analyze_vision_feedback(
        self,
        vision_result: Dict[str, Any]
    ) -> List[Task]:
        """
        Analyze vision feedback and create tasks.
        
        Args:
            vision_result: Result from VisionModule analysis
            
        Returns:
            List of tasks to address issues found in vision analysis
        """
        tasks = []
        
        # Extract relevant data from vision result
        has_pose = vision_result.get("has_pose", False)
        pose_errors = vision_result.get("pose_errors", [])
        refinement_areas = vision_result.get("refinement_areas", [])
        proportion_issues = vision_result.get("proportion_issues", False)
        symmetry_issues = vision_result.get("symmetry_issues", False)
        
        # Create tasks based on detected issues
        if not has_pose and vision_result.get("expected_pose", False):
            tasks.append(self._create_task(
                TaskType.FIX_POSE,
                "Fix pose detection - no pose detected",
                TaskPriority.CRITICAL
            ))
        
        # Create tasks from pose errors
        for error in pose_errors:
            task_type = self._error_to_task_type(error)
            tasks.append(self._create_task(
                task_type,
                f"Address pose error: {error}",
                TaskPriority.HIGH
            ))
        
        # Create tasks from refinement areas
        for area in refinement_areas:
            area_type = area.get("type", "unknown")
            region = area.get("region")
            task_type = self._area_to_task_type(area_type)
            tasks.append(self._create_task(
                task_type,
                f"Refine {area_type}",
                TaskPriority.MEDIUM,
                target_area=region
            ))
        
        # Create tasks for proportion issues
        if proportion_issues:
            tasks.append(self._create_task(
                TaskType.FIX_PROPORTIONS,
                "Fix body proportions",
                TaskPriority.HIGH
            ))
        
        # Create tasks for symmetry issues
        if symmetry_issues:
            tasks.append(self._create_task(
                TaskType.IMPROVE_SYMMETRY,
                "Improve bilateral symmetry",
                TaskPriority.MEDIUM
            ))
        
        logger.info(f"Created {len(tasks)} tasks from vision feedback")
        return tasks
    
    def create_action_plan(
        self,
        task: Task,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionPlan:
        """
        Create an action plan for a task.
        
        Args:
            task: Task to create plan for
            context: Additional context information
            
        Returns:
            ActionPlan with actions to accomplish the task
        """
        plan_id = str(uuid.uuid4())
        plan = ActionPlan(
            plan_id=plan_id,
            task_id=task.task_id,
            success_criteria=self._define_success_criteria(task)
        )
        
        # Generate actions based on task type
        actions = self._generate_actions_for_task(task, context)
        for action in actions:
            plan.add_action(action)
        
        logger.info(f"Created action plan {plan_id} with {len(actions)} actions for task {task.task_id}")
        return plan
    
    def evaluate_execution_result(
        self,
        task: Task,
        vision_result_before: Dict[str, Any],
        vision_result_after: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Evaluate if a task execution was successful.
        
        Args:
            task: Executed task
            vision_result_before: Vision analysis before execution
            vision_result_after: Vision analysis after execution
            
        Returns:
            ExecutionResult indicating success/failure
        """
        # Simple evaluation logic based on improvement
        score_before = self._calculate_quality_score(vision_result_before)
        score_after = self._calculate_quality_score(vision_result_after)
        
        improvement = score_after - score_before
        
        if improvement > 0.1:
            logger.info(f"Task {task.task_id} successful (improvement: {improvement:.2f})")
            return ExecutionResult.SUCCESS
        elif improvement > 0.0:
            logger.info(f"Task {task.task_id} partially successful (improvement: {improvement:.2f})")
            return ExecutionResult.PARTIAL
        else:
            logger.warning(f"Task {task.task_id} failed (improvement: {improvement:.2f})")
            return ExecutionResult.FAILURE
    
    def should_retry(
        self,
        task: Task,
        result: ExecutionResult,
        retry_count: int
    ) -> bool:
        """
        Determine if a task should be retried.
        
        Args:
            task: Task that was executed
            result: Execution result
            retry_count: Number of retries so far
            
        Returns:
            True if task should be retried
        """
        if result == ExecutionResult.SUCCESS:
            return False
        
        if not task.can_retry():
            return False
        
        # Retry failed tasks up to max retries
        if result == ExecutionResult.FAILURE and retry_count < task.max_retries:
            return True
        
        # Retry partial successes for critical tasks
        if result == ExecutionResult.PARTIAL and task.priority == TaskPriority.CRITICAL:
            return retry_count < 2
        
        return False
    
    def _create_task(
        self,
        task_type: TaskType,
        description: str,
        priority: TaskPriority,
        target_area: Optional[Dict[str, float]] = None
    ) -> Task:
        """Helper to create a task."""
        task_id = str(uuid.uuid4())
        return Task(
            task_id=task_id,
            task_type=task_type,
            description=description,
            priority=priority,
            target_area=target_area
        )
    
    def _error_to_task_type(self, error: str) -> TaskType:
        """Convert error string to task type."""
        error_lower = error.lower()
        if "hand" in error_lower:
            return TaskType.FIX_HAND
        elif "face" in error_lower:
            return TaskType.FIX_FACE
        elif "proportion" in error_lower:
            return TaskType.FIX_PROPORTIONS
        elif "symmetry" in error_lower:
            return TaskType.IMPROVE_SYMMETRY
        elif "pose" in error_lower:
            return TaskType.FIX_POSE
        else:
            return TaskType.REFINE_ANATOMY
    
    def _area_to_task_type(self, area_type: str) -> TaskType:
        """Convert area type to task type."""
        area_lower = area_type.lower()
        if "hand" in area_lower:
            return TaskType.FIX_HAND
        elif "face" in area_lower:
            return TaskType.FIX_FACE
        elif "silhouette" in area_lower:
            return TaskType.ENHANCE_SILHOUETTE
        elif "edge" in area_lower:
            return TaskType.ALIGN_EDGES
        else:
            return TaskType.REFINE_ANATOMY
    
    def _generate_actions_for_task(
        self,
        task: Task,
        context: Optional[Dict[str, Any]]
    ) -> List[DrawingAction]:
        """Generate actions based on task type."""
        actions = []
        
        # Simple rule-based action generation
        if task.task_type in [TaskType.FIX_HAND, TaskType.FIX_FACE, TaskType.REFINE_ANATOMY]:
            # Refinement action: erase and redraw
            actions.append(self._create_erase_action(task))
            actions.append(self._create_draw_action(task))
        
        elif task.task_type == TaskType.ENHANCE_SILHOUETTE:
            # Add outline strokes
            actions.append(self._create_draw_action(task, description="Enhance silhouette"))
        
        elif task.task_type == TaskType.FIX_PROPORTIONS:
            # Adjust proportions
            actions.append(self._create_erase_action(task, description="Erase incorrect proportions"))
            actions.append(self._create_draw_action(task, description="Redraw with correct proportions"))
        
        elif task.task_type == TaskType.IMPROVE_SYMMETRY:
            # Add symmetry corrections
            actions.append(self._create_draw_action(task, description="Add symmetry corrections"))
        
        else:
            # Default: single draw action
            actions.append(self._create_draw_action(task))
        
        return actions
    
    def _create_draw_action(
        self,
        task: Task,
        description: Optional[str] = None
    ) -> DrawingAction:
        """Create a drawing action."""
        action_id = str(uuid.uuid4())
        return DrawingAction(
            action_id=action_id,
            action_type=ActionType.DRAW_STROKE,
            description=description or f"Draw for {task.task_type.value}",
            target_region=task.target_area,
            tool_config={"tool_type": "pencil", "size": 2.0},
            stroke_points=self._generate_default_stroke_points(task.target_area),
            estimated_duration=2.0
        )
    
    def _create_erase_action(
        self,
        task: Task,
        description: Optional[str] = None
    ) -> DrawingAction:
        """Create an erase action."""
        action_id = str(uuid.uuid4())
        return DrawingAction(
            action_id=action_id,
            action_type=ActionType.ERASE_STROKE,
            description=description or f"Erase for {task.task_type.value}",
            target_region=task.target_area,
            tool_config={"tool_type": "eraser", "size": 10.0},
            estimated_duration=1.0
        )
    
    def _generate_default_stroke_points(
        self,
        target_area: Optional[Dict[str, float]]
    ) -> List[Dict[str, float]]:
        """Generate default stroke points."""
        if not target_area:
            # Default stroke in center
            return [
                {"x": 200 + i * 10, "y": 200 + i * 10, "pressure": 0.5}
                for i in range(self.default_stroke_length)
            ]
        
        # Generate stroke within target area
        x = target_area.get("x", 0)
        y = target_area.get("y", 0)
        width = target_area.get("width", 100)
        
        return [
            {"x": x + i * (width / self.default_stroke_length), "y": y + i * 5, "pressure": 0.5}
            for i in range(self.default_stroke_length)
        ]
    
    def _define_success_criteria(self, task: Task) -> Dict[str, Any]:
        """Define success criteria for a task."""
        return {
            "min_improvement": 0.1,
            "max_retries": task.max_retries,
            "task_type": task.task_type.value
        }
    
    def _calculate_quality_score(self, vision_result: Dict[str, Any]) -> float:
        """Calculate overall quality score from vision result."""
        score = 0.0
        count = 0
        
        # Aggregate various metrics
        if "proportion_score" in vision_result:
            score += vision_result["proportion_score"]
            count += 1
        
        if "symmetry_score" in vision_result:
            score += vision_result["symmetry_score"]
            count += 1
        
        if "overall_similarity" in vision_result:
            score += vision_result["overall_similarity"]
            count += 1
        
        if "detection_confidence" in vision_result:
            score += vision_result["detection_confidence"]
            count += 1
        
        return score / count if count > 0 else 0.5
