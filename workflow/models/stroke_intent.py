"""
Stroke Intent Classification.

Defines stroke types that represent artist intent during different phases
of the drawing workflow.
"""

from enum import Enum
from typing import Dict, Set, Optional
from dataclasses import dataclass, field

from workflow.models.drawing_phase import DrawingPhase


class StrokeIntent(Enum):
    """
    Types of strokes based on artistic intent.
    
    Each stroke type represents a different purpose in the drawing workflow,
    helping to categorize and analyze drawing actions.
    """
    GESTURE = "gesture"       # Quick, loose strokes for initial layout
    CONTOUR = "contour"       # Form-defining strokes for anatomy/structure
    DETAIL = "detail"         # Fine detail work for refinement
    CONSTRUCTION = "construction"  # Construction lines and guidelines
    SHADING = "shading"       # Shading and tonal work
    CLEANUP = "cleanup"       # Cleaning up and erasing construction lines


@dataclass
class StrokeMetadata:
    """
    Extended metadata for strokes with intent and purpose tracking.
    
    Attributes:
        intent: The artistic intent of this stroke
        phase: Drawing phase when stroke was created
        purpose: Human-readable description of stroke purpose
        task_id: Associated task ID (if applicable)
        action_id: Associated action ID (if applicable)
        confidence: Confidence in stroke execution (0.0-1.0)
        refinement_pass: Which refinement iteration this belongs to
        evaluation_score: Quality score after execution (0.0-1.0)
    """
    intent: StrokeIntent
    phase: DrawingPhase
    purpose: str = ""
    task_id: Optional[str] = None
    action_id: Optional[str] = None
    confidence: float = 1.0
    refinement_pass: int = 0
    evaluation_score: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "intent": self.intent.value,
            "phase": self.phase.value,
            "purpose": self.purpose,
            "task_id": self.task_id,
            "action_id": self.action_id,
            "confidence": self.confidence,
            "refinement_pass": self.refinement_pass,
            "evaluation_score": self.evaluation_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StrokeMetadata':
        """Create from dictionary."""
        data = data.copy()
        data["intent"] = StrokeIntent(data["intent"])
        data["phase"] = DrawingPhase(data["phase"])
        return cls(**data)


class StrokeIntentHelper:
    """
    Helper class for managing stroke intents across different phases.
    
    Provides guidance on which stroke intents are appropriate for each
    drawing phase.
    """
    
    # Recommended stroke intents for each phase
    PHASE_INTENTS: Dict[DrawingPhase, Set[StrokeIntent]] = {
        DrawingPhase.SKETCH: {
            StrokeIntent.GESTURE,
            StrokeIntent.CONSTRUCTION,
        },
        DrawingPhase.REFINEMENT: {
            StrokeIntent.CONTOUR,
            StrokeIntent.CONSTRUCTION,
            StrokeIntent.GESTURE,
        },
        DrawingPhase.STYLIZATION: {
            StrokeIntent.CONTOUR,
            StrokeIntent.DETAIL,
            StrokeIntent.CLEANUP,
        },
        DrawingPhase.RENDERING: {
            StrokeIntent.DETAIL,
            StrokeIntent.SHADING,
            StrokeIntent.CLEANUP,
        },
        DrawingPhase.COMPLETE: set(),  # No strokes in complete phase
    }
    
    # Primary intent for each phase (most common)
    PRIMARY_INTENT: Dict[DrawingPhase, StrokeIntent] = {
        DrawingPhase.SKETCH: StrokeIntent.GESTURE,
        DrawingPhase.REFINEMENT: StrokeIntent.CONTOUR,
        DrawingPhase.STYLIZATION: StrokeIntent.CONTOUR,
        DrawingPhase.RENDERING: StrokeIntent.DETAIL,
    }
    
    @classmethod
    def get_recommended_intents(cls, phase: DrawingPhase) -> Set[StrokeIntent]:
        """
        Get recommended stroke intents for a phase.
        
        Args:
            phase: Current drawing phase
            
        Returns:
            Set of recommended stroke intents
        """
        return cls.PHASE_INTENTS.get(phase, set())
    
    @classmethod
    def get_primary_intent(cls, phase: DrawingPhase) -> Optional[StrokeIntent]:
        """
        Get the primary/default stroke intent for a phase.
        
        Args:
            phase: Current drawing phase
            
        Returns:
            Primary stroke intent for this phase
        """
        return cls.PRIMARY_INTENT.get(phase)
    
    @classmethod
    def is_intent_appropriate(cls, phase: DrawingPhase, intent: StrokeIntent) -> bool:
        """
        Check if a stroke intent is appropriate for a phase.
        
        Args:
            phase: Drawing phase
            intent: Stroke intent to check
            
        Returns:
            True if intent is appropriate for phase
        """
        return intent in cls.PHASE_INTENTS.get(phase, set())
    
    @classmethod
    def suggest_intent_for_task(cls, phase: DrawingPhase, task_type: str) -> StrokeIntent:
        """
        Suggest a stroke intent based on phase and task type.
        
        Args:
            phase: Current drawing phase
            task_type: Type of task being performed
            
        Returns:
            Suggested stroke intent
        """
        # Map common task types to intents
        task_intent_map = {
            "fix_pose": StrokeIntent.GESTURE,
            "fix_proportions": StrokeIntent.CONSTRUCTION,
            "refine_anatomy": StrokeIntent.CONTOUR,
            "add_detail": StrokeIntent.DETAIL,
            "improve_symmetry": StrokeIntent.CONTOUR,
            "enhance_silhouette": StrokeIntent.CONTOUR,
        }
        
        # Get intent from task type
        suggested = task_intent_map.get(task_type.lower()) if task_type else None
        
        # Fall back to phase primary intent if suggestion not appropriate
        if suggested and cls.is_intent_appropriate(phase, suggested):
            return suggested
        
        return cls.get_primary_intent(phase) or StrokeIntent.GESTURE
