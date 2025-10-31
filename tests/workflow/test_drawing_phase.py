"""Tests for drawing phase state machine."""

import pytest
from datetime import datetime

from workflow.models.drawing_phase import (
    DrawingPhase,
    PhaseTransition,
    PhaseTransitionValidator,
)


class TestDrawingPhase:
    """Test DrawingPhase enum."""
    
    def test_phase_values(self):
        """Test phase enum values."""
        assert DrawingPhase.SKETCH.value == "sketch"
        assert DrawingPhase.REFINEMENT.value == "refinement"
        assert DrawingPhase.STYLIZATION.value == "stylization"
        assert DrawingPhase.RENDERING.value == "rendering"
        assert DrawingPhase.COMPLETE.value == "complete"


class TestPhaseTransition:
    """Test PhaseTransition class."""
    
    def test_create_transition(self):
        """Test creating a phase transition."""
        transition = PhaseTransition(
            from_phase=DrawingPhase.SKETCH,
            to_phase=DrawingPhase.REFINEMENT,
            reason="Quality threshold met",
            metrics={"quality": 0.8},
            confidence=0.9,
        )
        
        assert transition.from_phase == DrawingPhase.SKETCH
        assert transition.to_phase == DrawingPhase.REFINEMENT
        assert transition.reason == "Quality threshold met"
        assert transition.metrics["quality"] == 0.8
        assert transition.confidence == 0.9
    
    def test_transition_serialization(self):
        """Test transition to/from dict."""
        transition = PhaseTransition(
            from_phase=DrawingPhase.SKETCH,
            to_phase=DrawingPhase.REFINEMENT,
            reason="Test",
        )
        
        data = transition.to_dict()
        assert data["from_phase"] == "sketch"
        assert data["to_phase"] == "refinement"
        
        restored = PhaseTransition.from_dict(data)
        assert restored.from_phase == transition.from_phase
        assert restored.to_phase == transition.to_phase


class TestPhaseTransitionValidator:
    """Test phase transition validation."""
    
    def test_valid_forward_transitions(self):
        """Test valid forward phase transitions."""
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.SKETCH, DrawingPhase.REFINEMENT
        )
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.REFINEMENT, DrawingPhase.STYLIZATION
        )
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.STYLIZATION, DrawingPhase.RENDERING
        )
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.RENDERING, DrawingPhase.COMPLETE
        )
    
    def test_valid_regression_transitions(self):
        """Test valid regression transitions."""
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.REFINEMENT, DrawingPhase.SKETCH
        )
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.STYLIZATION, DrawingPhase.REFINEMENT
        )
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.RENDERING, DrawingPhase.STYLIZATION
        )
    
    def test_valid_iteration_transitions(self):
        """Test valid iteration within same phase."""
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.SKETCH, DrawingPhase.SKETCH
        )
        assert PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.REFINEMENT, DrawingPhase.REFINEMENT
        )
    
    def test_invalid_transitions(self):
        """Test invalid phase transitions."""
        # Can't skip phases
        assert not PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.SKETCH, DrawingPhase.STYLIZATION
        )
        assert not PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.SKETCH, DrawingPhase.RENDERING
        )
        
        # Can't go from COMPLETE to early phases
        assert not PhaseTransitionValidator.is_valid_transition(
            DrawingPhase.COMPLETE, DrawingPhase.SKETCH
        )
    
    def test_get_valid_next_phases(self):
        """Test getting valid next phases."""
        valid_from_sketch = PhaseTransitionValidator.get_valid_next_phases(
            DrawingPhase.SKETCH
        )
        assert DrawingPhase.SKETCH in valid_from_sketch
        assert DrawingPhase.REFINEMENT in valid_from_sketch
        assert len(valid_from_sketch) == 2
    
    def test_is_forward_progression(self):
        """Test forward progression detection."""
        assert PhaseTransitionValidator.is_forward_progression(
            DrawingPhase.SKETCH, DrawingPhase.REFINEMENT
        )
        assert not PhaseTransitionValidator.is_forward_progression(
            DrawingPhase.REFINEMENT, DrawingPhase.SKETCH
        )
        assert not PhaseTransitionValidator.is_forward_progression(
            DrawingPhase.SKETCH, DrawingPhase.SKETCH
        )
    
    def test_is_regression(self):
        """Test regression detection."""
        assert PhaseTransitionValidator.is_regression(
            DrawingPhase.REFINEMENT, DrawingPhase.SKETCH
        )
        assert not PhaseTransitionValidator.is_regression(
            DrawingPhase.SKETCH, DrawingPhase.REFINEMENT
        )
        assert not PhaseTransitionValidator.is_regression(
            DrawingPhase.SKETCH, DrawingPhase.SKETCH
        )
