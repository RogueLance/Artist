"""Tests for checkpoint manager."""

import pytest

from motor.core.canvas import Canvas
from motor.core.stroke import Stroke, StrokePoint
from workflow.models.drawing_phase import DrawingPhase
from workflow.core.checkpoint_manager import CheckpointManager, CanvasCheckpoint


class TestCanvasCheckpoint:
    """Test CanvasCheckpoint class."""
    
    def test_checkpoint_serialization(self):
        """Test checkpoint to/from dict."""
        from datetime import datetime
        
        canvas = Canvas(width=800, height=600)
        
        checkpoint = CanvasCheckpoint(
            checkpoint_id="cp_1",
            timestamp=datetime.now(),
            phase=DrawingPhase.SKETCH,
            canvas_state=canvas.to_dict(),
            description="Test checkpoint",
        )
        
        data = checkpoint.to_dict()
        assert data["checkpoint_id"] == "cp_1"
        assert data["phase"] == "sketch"
        
        restored = CanvasCheckpoint.from_dict(data)
        assert restored.checkpoint_id == checkpoint.checkpoint_id
        assert restored.phase == checkpoint.phase


class TestCheckpointManager:
    """Test CheckpointManager class."""
    
    def test_create_checkpoint(self):
        """Test creating a checkpoint."""
        manager = CheckpointManager(max_checkpoints=5)
        canvas = Canvas(width=800, height=600)
        strokes = [
            Stroke(points=[StrokePoint(0, 0), StrokePoint(10, 10)])
        ]
        
        checkpoint = manager.create_checkpoint(
            canvas=canvas,
            phase=DrawingPhase.SKETCH,
            stroke_history=strokes,
            description="Initial checkpoint",
        )
        
        assert checkpoint is not None
        assert checkpoint.phase == DrawingPhase.SKETCH
        assert len(checkpoint.stroke_history) == 1
        assert manager.get_checkpoint_count() == 1
    
    def test_get_checkpoint(self):
        """Test getting checkpoint by ID."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        checkpoint = manager.create_checkpoint(
            canvas=canvas,
            phase=DrawingPhase.SKETCH,
            stroke_history=[],
        )
        
        retrieved = manager.get_checkpoint(checkpoint.checkpoint_id)
        assert retrieved is not None
        assert retrieved.checkpoint_id == checkpoint.checkpoint_id
    
    def test_get_latest_checkpoint(self):
        """Test getting latest checkpoint."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        cp1 = manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        cp2 = manager.create_checkpoint(canvas, DrawingPhase.REFINEMENT, [])
        
        latest = manager.get_latest_checkpoint()
        assert latest.checkpoint_id == cp2.checkpoint_id
    
    def test_get_checkpoints_by_phase(self):
        """Test filtering checkpoints by phase."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        manager.create_checkpoint(canvas, DrawingPhase.REFINEMENT, [])
        manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        
        sketch_checkpoints = manager.get_checkpoints_by_phase(DrawingPhase.SKETCH)
        assert len(sketch_checkpoints) == 2
        
        refinement_checkpoints = manager.get_checkpoints_by_phase(DrawingPhase.REFINEMENT)
        assert len(refinement_checkpoints) == 1
    
    def test_restore_checkpoint(self):
        """Test restoring canvas from checkpoint."""
        manager = CheckpointManager()
        original_canvas = Canvas(width=800, height=600, name="Original")
        
        checkpoint = manager.create_checkpoint(
            original_canvas,
            DrawingPhase.SKETCH,
            [],
        )
        
        restored_canvas = manager.restore_checkpoint(checkpoint)
        assert restored_canvas.width == original_canvas.width
        assert restored_canvas.height == original_canvas.height
        assert restored_canvas.name == original_canvas.name
    
    def test_rollback_to_checkpoint(self):
        """Test rolling back to a checkpoint."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        cp1 = manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        cp2 = manager.create_checkpoint(canvas, DrawingPhase.REFINEMENT, [])
        cp3 = manager.create_checkpoint(canvas, DrawingPhase.STYLIZATION, [])
        
        # Rollback to cp2
        result = manager.rollback_to_checkpoint(cp2.checkpoint_id)
        assert result is not None
        assert result.checkpoint_id == cp2.checkpoint_id
    
    def test_rollback_to_phase(self):
        """Test rolling back to a phase."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        cp_refinement = manager.create_checkpoint(canvas, DrawingPhase.REFINEMENT, [])
        manager.create_checkpoint(canvas, DrawingPhase.STYLIZATION, [])
        
        # Rollback to refinement
        result = manager.rollback_to_phase(DrawingPhase.REFINEMENT)
        assert result is not None
        assert result.checkpoint_id == cp_refinement.checkpoint_id
    
    def test_max_checkpoints_limit(self):
        """Test checkpoint limit enforcement."""
        manager = CheckpointManager(max_checkpoints=3)
        canvas = Canvas(width=800, height=600)
        
        # Create 5 checkpoints
        for i in range(5):
            manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        
        # Should only keep last 3
        assert manager.get_checkpoint_count() == 3
    
    def test_get_stroke_history_at_checkpoint(self):
        """Test getting stroke history from checkpoint."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        strokes = [
            Stroke(points=[StrokePoint(0, 0), StrokePoint(10, 10)]),
            Stroke(points=[StrokePoint(20, 20), StrokePoint(30, 30)]),
        ]
        
        checkpoint = manager.create_checkpoint(
            canvas,
            DrawingPhase.SKETCH,
            strokes,
        )
        
        history = manager.get_stroke_history_at_checkpoint(checkpoint)
        assert len(history) == 2
        assert isinstance(history[0], Stroke)
    
    def test_clear_checkpoints(self):
        """Test clearing all checkpoints."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        manager.create_checkpoint(canvas, DrawingPhase.SKETCH, [])
        manager.create_checkpoint(canvas, DrawingPhase.REFINEMENT, [])
        
        assert manager.get_checkpoint_count() == 2
        
        manager.clear_checkpoints()
        assert manager.get_checkpoint_count() == 0
    
    def test_get_checkpoint_summary(self):
        """Test getting checkpoint summary."""
        manager = CheckpointManager()
        canvas = Canvas(width=800, height=600)
        
        manager.create_checkpoint(
            canvas,
            DrawingPhase.SKETCH,
            [],
            description="First checkpoint",
        )
        manager.create_checkpoint(
            canvas,
            DrawingPhase.REFINEMENT,
            [Stroke()],
            description="Second checkpoint",
        )
        
        summary = manager.get_checkpoint_summary()
        assert len(summary) == 2
        assert summary[0]["description"] == "First checkpoint"
        assert summary[1]["stroke_count"] == 1
