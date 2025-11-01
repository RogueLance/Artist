"""
Canvas Checkpoint and Rollback System.

Manages saving and restoring canvas state at phase transitions and critical
points in the workflow.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import copy

from motor.core.canvas import Canvas
from motor.core.stroke import Stroke
from workflow.models.drawing_phase import DrawingPhase


@dataclass
class CanvasCheckpoint:
    """
    A snapshot of canvas state at a specific point in time.
    
    Captures canvas configuration, layers, and stroke history to enable
    rollback and comparison.
    
    Attributes:
        checkpoint_id: Unique identifier
        timestamp: When checkpoint was created
        phase: Drawing phase at checkpoint time
        canvas_state: Serialized canvas state
        stroke_history: List of strokes executed up to this point
        metadata: Additional checkpoint metadata
        description: Human-readable description
    """
    checkpoint_id: str
    timestamp: datetime
    phase: DrawingPhase
    canvas_state: Dict[str, Any]
    stroke_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase.value,
            "canvas_state": self.canvas_state,
            "stroke_history": self.stroke_history,
            "metadata": self.metadata,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanvasCheckpoint':
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["phase"] = DrawingPhase(data["phase"])
        return cls(**data)


class CheckpointManager:
    """
    Manages canvas checkpoints and rollback functionality.
    
    Provides checkpoint creation, storage, and restoration capabilities
    for the workflow system.
    """
    
    def __init__(self, max_checkpoints: int = 10):
        """
        Initialize checkpoint manager.
        
        Args:
            max_checkpoints: Maximum number of checkpoints to keep
        """
        self.checkpoints: List[CanvasCheckpoint] = []
        self.max_checkpoints = max_checkpoints
        self.current_checkpoint_index: int = -1
    
    def create_checkpoint(
        self,
        canvas: Canvas,
        phase: DrawingPhase,
        stroke_history: List[Stroke],
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> CanvasCheckpoint:
        """
        Create a new checkpoint.
        
        Args:
            canvas: Current canvas state
            phase: Current drawing phase
            stroke_history: List of strokes executed
            description: Checkpoint description
            metadata: Additional metadata
            
        Returns:
            Created checkpoint
        """
        checkpoint_id = f"checkpoint_{datetime.now().timestamp()}"
        
        # Serialize canvas and strokes
        canvas_state = canvas.to_dict()
        stroke_data = [stroke.to_dict() for stroke in stroke_history]
        
        checkpoint = CanvasCheckpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now(),
            phase=phase,
            canvas_state=canvas_state,
            stroke_history=stroke_data,
            metadata=metadata or {},
            description=description,
        )
        
        # Add checkpoint
        self.checkpoints.append(checkpoint)
        self.current_checkpoint_index = len(self.checkpoints) - 1
        
        # Trim old checkpoints if needed
        if len(self.checkpoints) > self.max_checkpoints:
            self.checkpoints.pop(0)
            self.current_checkpoint_index -= 1
        
        return checkpoint
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[CanvasCheckpoint]:
        """
        Get a checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint if found, None otherwise
        """
        for checkpoint in self.checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                return checkpoint
        return None
    
    def get_latest_checkpoint(self) -> Optional[CanvasCheckpoint]:
        """
        Get the most recent checkpoint.
        
        Returns:
            Latest checkpoint or None if no checkpoints exist
        """
        if self.checkpoints:
            return self.checkpoints[-1]
        return None
    
    def get_checkpoints_by_phase(self, phase: DrawingPhase) -> List[CanvasCheckpoint]:
        """
        Get all checkpoints for a specific phase.
        
        Args:
            phase: Drawing phase to filter by
            
        Returns:
            List of checkpoints for the phase
        """
        return [cp for cp in self.checkpoints if cp.phase == phase]
    
    def restore_checkpoint(self, checkpoint: CanvasCheckpoint) -> Canvas:
        """
        Restore canvas from a checkpoint.
        
        Args:
            checkpoint: Checkpoint to restore from
            
        Returns:
            Restored canvas
        """
        return Canvas.from_dict(checkpoint.canvas_state)
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> Optional[CanvasCheckpoint]:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to rollback to
            
        Returns:
            Checkpoint if found, None otherwise
        """
        for i, checkpoint in enumerate(self.checkpoints):
            if checkpoint.checkpoint_id == checkpoint_id:
                self.current_checkpoint_index = i
                return checkpoint
        return None
    
    def rollback_to_phase(self, phase: DrawingPhase) -> Optional[CanvasCheckpoint]:
        """
        Rollback to the last checkpoint of a specific phase.
        
        Args:
            phase: Phase to rollback to
            
        Returns:
            Checkpoint if found, None otherwise
        """
        phase_checkpoints = self.get_checkpoints_by_phase(phase)
        if phase_checkpoints:
            checkpoint = phase_checkpoints[-1]
            return self.rollback_to_checkpoint(checkpoint.checkpoint_id)
        return None
    
    def get_stroke_history_at_checkpoint(
        self,
        checkpoint: CanvasCheckpoint
    ) -> List[Stroke]:
        """
        Get stroke history at a checkpoint.
        
        Args:
            checkpoint: Checkpoint to get strokes from
            
        Returns:
            List of strokes
        """
        return [Stroke.from_dict(s) for s in checkpoint.stroke_history]
    
    def clear_checkpoints(self):
        """Clear all checkpoints."""
        self.checkpoints.clear()
        self.current_checkpoint_index = -1
    
    def get_checkpoint_count(self) -> int:
        """Get number of stored checkpoints."""
        return len(self.checkpoints)
    
    def get_checkpoint_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all checkpoints.
        
        Returns:
            List of checkpoint summaries
        """
        return [
            {
                "checkpoint_id": cp.checkpoint_id,
                "timestamp": cp.timestamp.isoformat(),
                "phase": cp.phase.value,
                "description": cp.description,
                "stroke_count": len(cp.stroke_history),
            }
            for cp in self.checkpoints
        ]
