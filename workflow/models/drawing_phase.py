"""
Drawing Phase State Machine.

Defines the phases of artistic workflow and valid transitions between them.
"""

from enum import Enum
from typing import Set, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


class DrawingPhase(Enum):
    """
    Phases of the artistic drawing workflow.
    
    Each phase represents a distinct stage in the iterative drawing process,
    simulating how a real artist approaches creating artwork.
    """
    SKETCH = "sketch"           # Initial gesture and rough proportions
    REFINEMENT = "refinement"   # Anatomy and perspective construction
    STYLIZATION = "stylization" # Line work, clean, expressive strokes
    RENDERING = "rendering"     # Color, shading, final touch-up
    COMPLETE = "complete"       # Final phase, artwork finished


@dataclass
class PhaseTransition:
    """
    Represents a transition between drawing phases.
    
    Attributes:
        from_phase: Starting phase
        to_phase: Target phase
        timestamp: When transition occurred
        reason: Description of why transition occurred
        metrics: Metrics that triggered the transition
        confidence: Confidence score for this transition (0.0-1.0)
    """
    from_phase: DrawingPhase
    to_phase: DrawingPhase
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "from_phase": self.from_phase.value,
            "to_phase": self.to_phase.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "metrics": self.metrics,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PhaseTransition':
        """Create from dictionary."""
        data = data.copy()
        data["from_phase"] = DrawingPhase(data["from_phase"])
        data["to_phase"] = DrawingPhase(data["to_phase"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class PhaseTransitionValidator:
    """
    Validates and manages transitions between drawing phases.
    
    Enforces the logical progression of artistic workflow and prevents
    invalid phase transitions.
    """
    
    # Valid transitions between phases
    VALID_TRANSITIONS: Dict[DrawingPhase, Set[DrawingPhase]] = {
        DrawingPhase.SKETCH: {
            DrawingPhase.SKETCH,        # Can iterate within sketch
            DrawingPhase.REFINEMENT,    # Normal progression
        },
        DrawingPhase.REFINEMENT: {
            DrawingPhase.SKETCH,        # Can go back to fix fundamentals
            DrawingPhase.REFINEMENT,    # Can iterate within refinement
            DrawingPhase.STYLIZATION,   # Normal progression
        },
        DrawingPhase.STYLIZATION: {
            DrawingPhase.REFINEMENT,    # Can go back to fix structure
            DrawingPhase.STYLIZATION,   # Can iterate within stylization
            DrawingPhase.RENDERING,     # Normal progression
        },
        DrawingPhase.RENDERING: {
            DrawingPhase.STYLIZATION,   # Can go back to fix line work
            DrawingPhase.RENDERING,     # Can iterate within rendering
            DrawingPhase.COMPLETE,      # Finish artwork
        },
        DrawingPhase.COMPLETE: {
            DrawingPhase.COMPLETE,      # Stay complete
            DrawingPhase.RENDERING,     # Can reopen for final touches
        },
    }
    
    @classmethod
    def is_valid_transition(cls, from_phase: DrawingPhase, to_phase: DrawingPhase) -> bool:
        """
        Check if a transition is valid.
        
        Args:
            from_phase: Current phase
            to_phase: Target phase
            
        Returns:
            True if transition is valid
        """
        return to_phase in cls.VALID_TRANSITIONS.get(from_phase, set())
    
    @classmethod
    def get_valid_next_phases(cls, current_phase: DrawingPhase) -> Set[DrawingPhase]:
        """
        Get all valid phases that can be transitioned to from current phase.
        
        Args:
            current_phase: Current drawing phase
            
        Returns:
            Set of valid next phases
        """
        return cls.VALID_TRANSITIONS.get(current_phase, set())
    
    @classmethod
    def is_forward_progression(cls, from_phase: DrawingPhase, to_phase: DrawingPhase) -> bool:
        """
        Check if transition is forward progression (not iteration or regression).
        
        Args:
            from_phase: Starting phase
            to_phase: Target phase
            
        Returns:
            True if this is forward progression
        """
        phase_order = [
            DrawingPhase.SKETCH,
            DrawingPhase.REFINEMENT,
            DrawingPhase.STYLIZATION,
            DrawingPhase.RENDERING,
            DrawingPhase.COMPLETE,
        ]
        
        try:
            from_idx = phase_order.index(from_phase)
            to_idx = phase_order.index(to_phase)
            return to_idx > from_idx
        except ValueError:
            return False
    
    @classmethod
    def is_regression(cls, from_phase: DrawingPhase, to_phase: DrawingPhase) -> bool:
        """
        Check if transition is a regression (going back to earlier phase).
        
        Args:
            from_phase: Starting phase
            to_phase: Target phase
            
        Returns:
            True if this is a regression
        """
        phase_order = [
            DrawingPhase.SKETCH,
            DrawingPhase.REFINEMENT,
            DrawingPhase.STYLIZATION,
            DrawingPhase.RENDERING,
            DrawingPhase.COMPLETE,
        ]
        
        try:
            from_idx = phase_order.index(from_phase)
            to_idx = phase_order.index(to_phase)
            return to_idx < from_idx
        except ValueError:
            return False
