"""
Workflow Executor.

Orchestrates the complete artistic workflow, integrating the Brain, Motor,
Vision, and Workflow systems.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from motor.core.canvas import Canvas
from motor.core.stroke import Stroke
from workflow.models.drawing_phase import DrawingPhase
from workflow.models.stroke_intent import StrokeIntent, StrokeMetadata, StrokeIntentHelper
from workflow.models.workflow_state import WorkflowState
from workflow.core.checkpoint_manager import CheckpointManager
from workflow.core.decision_logger import DecisionLogger


class WorkflowExecutor:
    """
    Executes and manages the artistic workflow pipeline.
    
    Coordinates between Brain, Motor, Vision, and Workflow systems to
    implement a complete iterative drawing process.
    """
    
    def __init__(
        self,
        canvas: Canvas,
        max_checkpoints: int = 10,
        enable_logging: bool = True,
    ):
        """
        Initialize workflow executor.
        
        Args:
            canvas: Canvas to work with
            max_checkpoints: Maximum checkpoints to maintain
            enable_logging: Whether to enable decision logging
        """
        self.canvas = canvas
        self.workflow_state = WorkflowState()
        self.checkpoint_manager = CheckpointManager(max_checkpoints=max_checkpoints)
        self.decision_logger = DecisionLogger() if enable_logging else None
        self.stroke_history: List[Stroke] = []
        
        # Start with sketch phase
        self._initialize_workflow()
    
    def _initialize_workflow(self):
        """Initialize workflow in sketch phase."""
        self.workflow_state.current_phase = DrawingPhase.SKETCH
        
        if self.decision_logger:
            self.decision_logger.start_phase(DrawingPhase.SKETCH)
        
        # Create initial checkpoint
        self.create_checkpoint(
            description="Initial canvas state",
            metadata={"type": "initial"}
        )
    
    def transition_to_phase(
        self,
        new_phase: DrawingPhase,
        reason: str = "",
        metrics: Optional[Dict[str, float]] = None,
        create_checkpoint: bool = True,
    ) -> bool:
        """
        Transition to a new drawing phase.
        
        Args:
            new_phase: Target phase
            reason: Reason for transition
            metrics: Metrics triggering transition
            create_checkpoint: Whether to create checkpoint
            
        Returns:
            True if transition successful
        """
        # Attempt transition
        success = self.workflow_state.transition_to_phase(
            new_phase, reason, metrics
        )
        
        if not success:
            return False
        
        # Close previous phase log
        if self.decision_logger:
            self.decision_logger.close_phase(reason)
            self.decision_logger.start_phase(new_phase)
        
        # Create checkpoint at phase boundary
        if create_checkpoint:
            self.create_checkpoint(
                description=f"Phase transition to {new_phase.value}",
                metadata={
                    "type": "phase_transition",
                    "reason": reason,
                    "metrics": metrics or {},
                }
            )
        
        return True
    
    def execute_stroke(
        self,
        stroke: Stroke,
        intent: Optional[StrokeIntent] = None,
        purpose: str = "",
        task_id: Optional[str] = None,
        action_id: Optional[str] = None,
        pre_evaluation: Optional[Dict[str, float]] = None,
        post_evaluation: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        Execute a stroke with full metadata tracking.
        
        Args:
            stroke: Stroke to execute
            intent: Stroke intent (auto-detected if not provided)
            purpose: Human-readable purpose
            task_id: Associated task ID
            action_id: Associated action ID
            pre_evaluation: Evaluation before stroke
            post_evaluation: Evaluation after stroke
            
        Returns:
            Stroke ID
        """
        # Auto-detect intent if not provided
        if intent is None:
            intent = StrokeIntentHelper.get_primary_intent(
                self.workflow_state.current_phase
            ) or StrokeIntent.GESTURE
        
        # Generate stroke ID
        stroke_id = str(uuid.uuid4())
        
        # Add workflow metadata to stroke
        workflow_metadata = StrokeMetadata(
            intent=intent,
            phase=self.workflow_state.current_phase,
            purpose=purpose,
            task_id=task_id,
            action_id=action_id,
            refinement_pass=self.workflow_state.iteration_in_phase,
        )
        
        # Merge with existing metadata
        stroke.metadata.update({
            "workflow": workflow_metadata.to_dict(),
            "stroke_id": stroke_id,
        })
        
        # Add to stroke history
        self.stroke_history.append(stroke)
        
        # Update workflow state
        self.workflow_state.record_stroke()
        
        # Log decision
        if self.decision_logger:
            self.decision_logger.log_stroke(
                stroke_id=stroke_id,
                intent=intent,
                phase=self.workflow_state.current_phase,
                purpose=purpose,
                task_id=task_id,
                action_id=action_id,
                pre_evaluation=pre_evaluation,
                post_evaluation=post_evaluation,
                stroke_data=stroke.to_dict(),
            )
        
        return stroke_id
    
    def create_checkpoint(
        self,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a checkpoint at current state.
        
        Args:
            description: Checkpoint description
            metadata: Additional metadata
            
        Returns:
            Checkpoint ID
        """
        checkpoint = self.checkpoint_manager.create_checkpoint(
            canvas=self.canvas,
            phase=self.workflow_state.current_phase,
            stroke_history=self.stroke_history,
            description=description,
            metadata=metadata,
        )
        return checkpoint.checkpoint_id
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            
        Returns:
            True if rollback successful
        """
        checkpoint = self.checkpoint_manager.rollback_to_checkpoint(checkpoint_id)
        if not checkpoint:
            return False
        
        # Restore canvas
        self.canvas = self.checkpoint_manager.restore_checkpoint(checkpoint)
        
        # Restore stroke history
        self.stroke_history = self.checkpoint_manager.get_stroke_history_at_checkpoint(
            checkpoint
        )
        
        # Update workflow state
        self.workflow_state.current_phase = checkpoint.phase
        self.workflow_state.phase_start_time = checkpoint.timestamp
        self.workflow_state.total_strokes = len(self.stroke_history)
        
        return True
    
    def rollback_to_phase(self, phase: DrawingPhase) -> bool:
        """
        Rollback to last checkpoint of a phase.
        
        Args:
            phase: Phase to rollback to
            
        Returns:
            True if rollback successful
        """
        checkpoint = self.checkpoint_manager.rollback_to_phase(phase)
        if checkpoint:
            return self.rollback_to_checkpoint(checkpoint.checkpoint_id)
        return False
    
    def evaluate_and_decide_transition(
        self,
        evaluation_metrics: Dict[str, float],
        quality_threshold: float = 0.7,
    ) -> Optional[DrawingPhase]:
        """
        Evaluate current phase and decide if transition needed.
        
        Args:
            evaluation_metrics: Current quality metrics
            quality_threshold: Threshold for phase completion
            
        Returns:
            Suggested next phase or None
        """
        current_phase = self.workflow_state.current_phase
        
        # Log evaluation
        if self.decision_logger:
            self.decision_logger.log_evaluation(evaluation_metrics)
        
        # Check for empty metrics
        if not evaluation_metrics:
            return None
        
        # Calculate average quality
        avg_quality = sum(evaluation_metrics.values()) / len(evaluation_metrics)
        
        # Decision logic based on phase and quality
        if avg_quality >= quality_threshold:
            # Quality is good, consider progression
            if current_phase == DrawingPhase.SKETCH:
                return DrawingPhase.REFINEMENT
            elif current_phase == DrawingPhase.REFINEMENT:
                return DrawingPhase.STYLIZATION
            elif current_phase == DrawingPhase.STYLIZATION:
                return DrawingPhase.RENDERING
            elif current_phase == DrawingPhase.RENDERING:
                return DrawingPhase.COMPLETE
        
        elif avg_quality < 0.4 and self.workflow_state.iteration_in_phase > 2:
            # Quality is poor after multiple iterations, regress
            if current_phase == DrawingPhase.RENDERING:
                return DrawingPhase.STYLIZATION
            elif current_phase == DrawingPhase.STYLIZATION:
                return DrawingPhase.REFINEMENT
            elif current_phase == DrawingPhase.REFINEMENT:
                return DrawingPhase.SKETCH
        
        # Stay in current phase
        return None
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive workflow summary.
        
        Returns:
            Workflow summary dictionary
        """
        summary = {
            "workflow_state": self.workflow_state.get_summary(),
            "checkpoint_count": self.checkpoint_manager.get_checkpoint_count(),
            "total_strokes": len(self.stroke_history),
        }
        
        if self.decision_logger:
            summary["decision_log"] = self.decision_logger.get_workflow_summary()
        
        return summary
    
    def export_workflow(self) -> Dict[str, Any]:
        """
        Export complete workflow for serialization.
        
        Returns:
            Complete workflow data
        """
        data = {
            "workflow_state": self.workflow_state.to_dict(),
            "canvas": self.canvas.to_dict(),
            "stroke_history": [s.to_dict() for s in self.stroke_history],
            "checkpoints": self.checkpoint_manager.get_checkpoint_summary(),
        }
        
        if self.decision_logger:
            data["decision_log"] = self.decision_logger.to_dict()
        
        return data
    
    def is_complete(self) -> bool:
        """
        Check if workflow is complete.
        
        Returns:
            True if in COMPLETE phase
        """
        return self.workflow_state.is_phase_complete()
    
    def get_current_phase(self) -> DrawingPhase:
        """Get current drawing phase."""
        return self.workflow_state.current_phase
    
    def get_stroke_count_by_intent(self, intent: StrokeIntent) -> int:
        """
        Get count of strokes by intent.
        
        Args:
            intent: Stroke intent to count
            
        Returns:
            Number of strokes with that intent
        """
        count = 0
        for stroke in self.stroke_history:
            workflow_meta = stroke.metadata.get("workflow", {})
            if workflow_meta.get("intent") == intent.value:
                count += 1
        return count
    
    def get_phase_stroke_count(self, phase: DrawingPhase) -> int:
        """
        Get count of strokes in a phase.
        
        Args:
            phase: Phase to count strokes for
            
        Returns:
            Number of strokes in that phase
        """
        count = 0
        for stroke in self.stroke_history:
            workflow_meta = stroke.metadata.get("workflow", {})
            if workflow_meta.get("phase") == phase.value:
                count += 1
        return count
