"""
Workflow State Management.

Tracks the current state of the artistic workflow including phase,
checkpoints, and progression.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from workflow.models.drawing_phase import DrawingPhase, PhaseTransition


@dataclass
class WorkflowState:
    """
    Current state of the artistic workflow.
    
    Tracks the progression through drawing phases, manages phase transitions,
    and maintains workflow history.
    
    Attributes:
        current_phase: Current drawing phase
        phase_history: History of all phase transitions
        phase_start_time: When current phase started
        iteration_in_phase: Number of iterations within current phase
        total_strokes: Total number of strokes executed
        phase_stroke_count: Strokes executed in current phase
        workflow_id: Unique identifier for this workflow session
        metadata: Additional workflow metadata
    """
    current_phase: DrawingPhase = DrawingPhase.SKETCH
    phase_history: List[PhaseTransition] = field(default_factory=list)
    phase_start_time: datetime = field(default_factory=datetime.now)
    iteration_in_phase: int = 0
    total_strokes: int = 0
    phase_stroke_count: int = 0
    workflow_id: str = field(default_factory=lambda: f"workflow_{datetime.now().timestamp()}")
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def transition_to_phase(
        self,
        new_phase: DrawingPhase,
        reason: str = "",
        metrics: Optional[Dict[str, float]] = None,
        confidence: float = 1.0
    ) -> bool:
        """
        Transition to a new drawing phase.
        
        Args:
            new_phase: Target phase
            reason: Reason for transition
            metrics: Metrics that triggered transition
            confidence: Confidence in this transition
            
        Returns:
            True if transition was successful
        """
        from workflow.models.drawing_phase import PhaseTransitionValidator
        
        # Validate transition
        if not PhaseTransitionValidator.is_valid_transition(self.current_phase, new_phase):
            return False
        
        # Record transition
        transition = PhaseTransition(
            from_phase=self.current_phase,
            to_phase=new_phase,
            reason=reason,
            metrics=metrics or {},
            confidence=confidence,
        )
        self.phase_history.append(transition)
        
        # Update state
        self.current_phase = new_phase
        self.phase_start_time = datetime.now()
        
        # Reset or increment iteration counter
        if new_phase == transition.from_phase:
            self.iteration_in_phase += 1
        else:
            self.iteration_in_phase = 0
        
        # Reset phase stroke count for new phase
        self.phase_stroke_count = 0
        
        return True
    
    def record_stroke(self):
        """Record that a stroke was executed."""
        self.total_strokes += 1
        self.phase_stroke_count += 1
    
    def get_time_in_phase(self) -> float:
        """
        Get time spent in current phase in seconds.
        
        Returns:
            Seconds in current phase
        """
        return (datetime.now() - self.phase_start_time).total_seconds()
    
    def get_phase_transitions(self, phase: Optional[DrawingPhase] = None) -> List[PhaseTransition]:
        """
        Get phase transitions, optionally filtered by phase.
        
        Args:
            phase: Filter for transitions to/from this phase
            
        Returns:
            List of matching transitions
        """
        if phase is None:
            return self.phase_history
        
        return [
            t for t in self.phase_history
            if t.from_phase == phase or t.to_phase == phase
        ]
    
    def get_phase_duration(self, phase: DrawingPhase) -> float:
        """
        Get total time spent in a specific phase.
        
        Args:
            phase: Phase to calculate duration for
            
        Returns:
            Total seconds spent in phase
        """
        total_duration = 0.0
        
        # Track when we enter and exit the phase
        for i, transition in enumerate(self.phase_history):
            # When transitioning TO this phase, we enter it
            if transition.to_phase == phase:
                # Find when we leave this phase (transition FROM it)
                start_time = transition.timestamp
                end_time = None
                
                # Look for next transition FROM this phase
                for j in range(i + 1, len(self.phase_history)):
                    if self.phase_history[j].from_phase == phase:
                        end_time = self.phase_history[j].timestamp
                        break
                
                # If no exit transition found, check if still in phase
                if end_time is None:
                    if self.current_phase == phase:
                        end_time = datetime.now()
                    else:
                        # Phase was skipped or we're in a different phase
                        continue
                
                duration = (end_time - start_time).total_seconds()
                total_duration += duration
        
        # Special case: if no transitions yet but we're in this phase
        if not self.phase_history and self.current_phase == phase:
            total_duration = self.get_time_in_phase()
        
        return total_duration
    
    def is_phase_complete(self) -> bool:
        """
        Check if workflow is complete.
        
        Returns:
            True if in COMPLETE phase
        """
        return self.current_phase == DrawingPhase.COMPLETE
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the workflow state.
        
        Returns:
            Dictionary with workflow summary
        """
        return {
            "workflow_id": self.workflow_id,
            "current_phase": self.current_phase.value,
            "iteration_in_phase": self.iteration_in_phase,
            "time_in_phase_seconds": self.get_time_in_phase(),
            "total_strokes": self.total_strokes,
            "phase_stroke_count": self.phase_stroke_count,
            "total_transitions": len(self.phase_history),
            "is_complete": self.is_phase_complete(),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current_phase": self.current_phase.value,
            "phase_history": [t.to_dict() for t in self.phase_history],
            "phase_start_time": self.phase_start_time.isoformat(),
            "iteration_in_phase": self.iteration_in_phase,
            "total_strokes": self.total_strokes,
            "phase_stroke_count": self.phase_stroke_count,
            "workflow_id": self.workflow_id,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create from dictionary."""
        data = data.copy()
        data["current_phase"] = DrawingPhase(data["current_phase"])
        data["phase_history"] = [
            PhaseTransition.from_dict(t) for t in data.get("phase_history", [])
        ]
        data["phase_start_time"] = datetime.fromisoformat(data["phase_start_time"])
        return cls(**data)
