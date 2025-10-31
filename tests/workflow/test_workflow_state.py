"""Tests for workflow state management."""

import pytest
from datetime import datetime

from workflow.models.workflow_state import WorkflowState
from workflow.models.drawing_phase import DrawingPhase


class TestWorkflowState:
    """Test WorkflowState class."""
    
    def test_initial_state(self):
        """Test initial workflow state."""
        state = WorkflowState()
        assert state.current_phase == DrawingPhase.SKETCH
        assert state.iteration_in_phase == 0
        assert state.total_strokes == 0
        assert state.phase_stroke_count == 0
        assert len(state.phase_history) == 0
    
    def test_transition_to_phase(self):
        """Test transitioning to new phase."""
        state = WorkflowState()
        
        # Valid transition
        success = state.transition_to_phase(
            DrawingPhase.REFINEMENT,
            reason="Quality met",
            metrics={"quality": 0.8},
        )
        
        assert success
        assert state.current_phase == DrawingPhase.REFINEMENT
        assert len(state.phase_history) == 1
        assert state.phase_history[0].from_phase == DrawingPhase.SKETCH
        assert state.phase_history[0].to_phase == DrawingPhase.REFINEMENT
    
    def test_invalid_transition(self):
        """Test invalid phase transition."""
        state = WorkflowState()
        
        # Try to skip phases
        success = state.transition_to_phase(DrawingPhase.RENDERING)
        assert not success
        assert state.current_phase == DrawingPhase.SKETCH
    
    def test_iteration_within_phase(self):
        """Test iterating within same phase."""
        state = WorkflowState()
        
        # First iteration
        state.transition_to_phase(DrawingPhase.SKETCH)
        assert state.iteration_in_phase == 1
        
        # Second iteration
        state.transition_to_phase(DrawingPhase.SKETCH)
        assert state.iteration_in_phase == 2
    
    def test_record_stroke(self):
        """Test recording strokes."""
        state = WorkflowState()
        
        state.record_stroke()
        assert state.total_strokes == 1
        assert state.phase_stroke_count == 1
        
        state.record_stroke()
        assert state.total_strokes == 2
        assert state.phase_stroke_count == 2
        
        # Transition resets phase stroke count
        state.transition_to_phase(DrawingPhase.REFINEMENT)
        assert state.total_strokes == 2
        assert state.phase_stroke_count == 0
        
        state.record_stroke()
        assert state.total_strokes == 3
        assert state.phase_stroke_count == 1
    
    def test_get_time_in_phase(self):
        """Test getting time in current phase."""
        state = WorkflowState()
        
        time_in_phase = state.get_time_in_phase()
        assert time_in_phase >= 0
    
    def test_get_phase_transitions(self):
        """Test getting phase transitions."""
        state = WorkflowState()
        
        state.transition_to_phase(DrawingPhase.REFINEMENT)
        state.transition_to_phase(DrawingPhase.STYLIZATION)
        
        # Get all transitions
        all_transitions = state.get_phase_transitions()
        assert len(all_transitions) == 2
        
        # Filter by phase
        refinement_transitions = state.get_phase_transitions(DrawingPhase.REFINEMENT)
        assert len(refinement_transitions) == 2  # from sketch and to stylization
    
    def test_is_phase_complete(self):
        """Test checking if workflow is complete."""
        state = WorkflowState()
        assert not state.is_phase_complete()
        
        state.current_phase = DrawingPhase.COMPLETE
        assert state.is_phase_complete()
    
    def test_get_summary(self):
        """Test getting workflow summary."""
        state = WorkflowState()
        state.record_stroke()
        state.transition_to_phase(DrawingPhase.REFINEMENT)
        
        summary = state.get_summary()
        assert summary["current_phase"] == "refinement"
        assert summary["total_strokes"] == 1
        assert summary["total_transitions"] == 1
        assert not summary["is_complete"]
    
    def test_serialization(self):
        """Test state to/from dict."""
        state = WorkflowState()
        state.record_stroke()
        state.transition_to_phase(DrawingPhase.REFINEMENT)
        
        data = state.to_dict()
        assert data["current_phase"] == "refinement"
        assert data["total_strokes"] == 1
        
        restored = WorkflowState.from_dict(data)
        assert restored.current_phase == state.current_phase
        assert restored.total_strokes == state.total_strokes
