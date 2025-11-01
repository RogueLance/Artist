"""Tests for workflow executor."""

import pytest

from motor.core.canvas import Canvas
from motor.core.stroke import Stroke, StrokePoint
from workflow.models.drawing_phase import DrawingPhase
from workflow.models.stroke_intent import StrokeIntent
from workflow.core.workflow_executor import WorkflowExecutor


class TestWorkflowExecutor:
    """Test WorkflowExecutor class."""
    
    def test_initialization(self):
        """Test workflow executor initialization."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        assert executor.canvas == canvas
        assert executor.workflow_state.current_phase == DrawingPhase.SKETCH
        assert executor.checkpoint_manager.get_checkpoint_count() == 1  # Initial checkpoint
        assert executor.decision_logger is not None
    
    def test_transition_to_phase(self):
        """Test phase transition."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        success = executor.transition_to_phase(
            DrawingPhase.REFINEMENT,
            reason="Quality threshold met",
        )
        
        assert success
        assert executor.workflow_state.current_phase == DrawingPhase.REFINEMENT
        # Should have initial + transition checkpoint
        assert executor.checkpoint_manager.get_checkpoint_count() == 2
    
    def test_invalid_transition(self):
        """Test invalid phase transition."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        # Try to skip phases
        success = executor.transition_to_phase(DrawingPhase.RENDERING)
        
        assert not success
        assert executor.workflow_state.current_phase == DrawingPhase.SKETCH
    
    def test_execute_stroke(self):
        """Test executing a stroke."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        stroke = Stroke(points=[
            StrokePoint(10, 10),
            StrokePoint(20, 20),
        ])
        
        stroke_id = executor.execute_stroke(
            stroke,
            intent=StrokeIntent.GESTURE,
            purpose="Initial gesture",
        )
        
        assert stroke_id is not None
        assert len(executor.stroke_history) == 1
        assert executor.workflow_state.total_strokes == 1
        assert "workflow" in stroke.metadata
        assert stroke.metadata["stroke_id"] == stroke_id
    
    def test_execute_stroke_auto_intent(self):
        """Test stroke execution with auto-detected intent."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        stroke = Stroke(points=[StrokePoint(0, 0)])
        stroke_id = executor.execute_stroke(stroke)
        
        # Should auto-detect intent based on phase
        workflow_meta = stroke.metadata["workflow"]
        assert workflow_meta["intent"] == StrokeIntent.GESTURE.value
        assert workflow_meta["phase"] == DrawingPhase.SKETCH.value
    
    def test_create_checkpoint(self):
        """Test creating checkpoints."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        initial_count = executor.checkpoint_manager.get_checkpoint_count()
        
        checkpoint_id = executor.create_checkpoint(
            description="Test checkpoint",
            metadata={"type": "manual"},
        )
        
        assert checkpoint_id is not None
        assert executor.checkpoint_manager.get_checkpoint_count() == initial_count + 1
    
    def test_rollback_to_checkpoint(self):
        """Test rolling back to a checkpoint."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        # Create checkpoint after some strokes
        stroke1 = Stroke(points=[StrokePoint(0, 0)])
        executor.execute_stroke(stroke1)
        
        checkpoint_id = executor.create_checkpoint(description="After stroke 1")
        
        # Add more strokes
        stroke2 = Stroke(points=[StrokePoint(10, 10)])
        executor.execute_stroke(stroke2)
        
        assert len(executor.stroke_history) == 2
        
        # Rollback
        success = executor.rollback_to_checkpoint(checkpoint_id)
        
        assert success
        assert len(executor.stroke_history) == 1
    
    def test_rollback_to_phase(self):
        """Test rolling back to a phase."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        # Progress through phases
        executor.transition_to_phase(DrawingPhase.REFINEMENT)
        executor.transition_to_phase(DrawingPhase.STYLIZATION)
        
        # Rollback to refinement
        success = executor.rollback_to_phase(DrawingPhase.REFINEMENT)
        
        assert success
        assert executor.workflow_state.current_phase == DrawingPhase.REFINEMENT
    
    def test_evaluate_and_decide_transition_forward(self):
        """Test evaluation-based phase transition (forward)."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        # High quality metrics should suggest forward transition
        metrics = {"quality": 0.8, "accuracy": 0.75}
        suggested_phase = executor.evaluate_and_decide_transition(metrics)
        
        assert suggested_phase == DrawingPhase.REFINEMENT
    
    def test_evaluate_and_decide_transition_stay(self):
        """Test evaluation suggesting staying in phase."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        # Medium quality metrics should suggest staying
        metrics = {"quality": 0.6, "accuracy": 0.5}
        suggested_phase = executor.evaluate_and_decide_transition(metrics)
        
        assert suggested_phase is None
    
    def test_evaluate_and_decide_transition_regress(self):
        """Test evaluation suggesting regression."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        # Progress to refinement first
        executor.transition_to_phase(DrawingPhase.REFINEMENT)
        
        # Iterate a few times with poor quality
        for _ in range(3):
            executor.workflow_state.transition_to_phase(DrawingPhase.REFINEMENT)
        
        # Poor quality after iterations should suggest regression
        metrics = {"quality": 0.3, "accuracy": 0.2}
        suggested_phase = executor.evaluate_and_decide_transition(metrics)
        
        assert suggested_phase == DrawingPhase.SKETCH
    
    def test_get_workflow_summary(self):
        """Test getting workflow summary."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        executor.execute_stroke(Stroke(points=[StrokePoint(0, 0)]))
        executor.transition_to_phase(DrawingPhase.REFINEMENT)
        
        summary = executor.get_workflow_summary()
        
        assert "workflow_state" in summary
        assert "checkpoint_count" in summary
        assert "total_strokes" in summary
        assert summary["total_strokes"] == 1
    
    def test_export_workflow(self):
        """Test exporting workflow."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        executor.execute_stroke(Stroke(points=[StrokePoint(0, 0)]))
        
        data = executor.export_workflow()
        
        assert "workflow_state" in data
        assert "canvas" in data
        assert "stroke_history" in data
        assert "checkpoints" in data
        assert "decision_log" in data
    
    def test_is_complete(self):
        """Test checking if workflow is complete."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        assert not executor.is_complete()
        
        executor.workflow_state.current_phase = DrawingPhase.COMPLETE
        assert executor.is_complete()
    
    def test_get_stroke_count_by_intent(self):
        """Test counting strokes by intent."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        executor.execute_stroke(
            Stroke(points=[StrokePoint(0, 0)]),
            intent=StrokeIntent.GESTURE,
        )
        executor.execute_stroke(
            Stroke(points=[StrokePoint(10, 10)]),
            intent=StrokeIntent.GESTURE,
        )
        executor.execute_stroke(
            Stroke(points=[StrokePoint(20, 20)]),
            intent=StrokeIntent.CONSTRUCTION,
        )
        
        gesture_count = executor.get_stroke_count_by_intent(StrokeIntent.GESTURE)
        assert gesture_count == 2
        
        construction_count = executor.get_stroke_count_by_intent(StrokeIntent.CONSTRUCTION)
        assert construction_count == 1
    
    def test_get_phase_stroke_count(self):
        """Test counting strokes by phase."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas)
        
        executor.execute_stroke(Stroke(points=[StrokePoint(0, 0)]))
        executor.execute_stroke(Stroke(points=[StrokePoint(10, 10)]))
        
        executor.transition_to_phase(DrawingPhase.REFINEMENT)
        executor.execute_stroke(Stroke(points=[StrokePoint(20, 20)]))
        
        sketch_count = executor.get_phase_stroke_count(DrawingPhase.SKETCH)
        assert sketch_count == 2
        
        refinement_count = executor.get_phase_stroke_count(DrawingPhase.REFINEMENT)
        assert refinement_count == 1
    
    def test_workflow_without_logging(self):
        """Test workflow executor without decision logging."""
        canvas = Canvas(width=800, height=600)
        executor = WorkflowExecutor(canvas, enable_logging=False)
        
        assert executor.decision_logger is None
        
        # Should still work without logging
        executor.execute_stroke(Stroke(points=[StrokePoint(0, 0)]))
        assert len(executor.stroke_history) == 1
