"""Tests for stroke intent classification."""

import pytest

from workflow.models.stroke_intent import (
    StrokeIntent,
    StrokeMetadata,
    StrokeIntentHelper,
)
from workflow.models.drawing_phase import DrawingPhase


class TestStrokeIntent:
    """Test StrokeIntent enum."""
    
    def test_intent_values(self):
        """Test intent enum values."""
        assert StrokeIntent.GESTURE.value == "gesture"
        assert StrokeIntent.CONTOUR.value == "contour"
        assert StrokeIntent.DETAIL.value == "detail"
        assert StrokeIntent.CONSTRUCTION.value == "construction"
        assert StrokeIntent.SHADING.value == "shading"
        assert StrokeIntent.CLEANUP.value == "cleanup"


class TestStrokeMetadata:
    """Test StrokeMetadata class."""
    
    def test_create_metadata(self):
        """Test creating stroke metadata."""
        metadata = StrokeMetadata(
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
            purpose="Initial layout",
            task_id="task_123",
            confidence=0.8,
        )
        
        assert metadata.intent == StrokeIntent.GESTURE
        assert metadata.phase == DrawingPhase.SKETCH
        assert metadata.purpose == "Initial layout"
        assert metadata.task_id == "task_123"
        assert metadata.confidence == 0.8
    
    def test_metadata_serialization(self):
        """Test metadata to/from dict."""
        metadata = StrokeMetadata(
            intent=StrokeIntent.CONTOUR,
            phase=DrawingPhase.REFINEMENT,
            purpose="Define anatomy",
        )
        
        data = metadata.to_dict()
        assert data["intent"] == "contour"
        assert data["phase"] == "refinement"
        
        restored = StrokeMetadata.from_dict(data)
        assert restored.intent == metadata.intent
        assert restored.phase == metadata.phase


class TestStrokeIntentHelper:
    """Test StrokeIntentHelper class."""
    
    def test_get_recommended_intents_sketch(self):
        """Test recommended intents for sketch phase."""
        intents = StrokeIntentHelper.get_recommended_intents(DrawingPhase.SKETCH)
        assert StrokeIntent.GESTURE in intents
        assert StrokeIntent.CONSTRUCTION in intents
    
    def test_get_recommended_intents_refinement(self):
        """Test recommended intents for refinement phase."""
        intents = StrokeIntentHelper.get_recommended_intents(DrawingPhase.REFINEMENT)
        assert StrokeIntent.CONTOUR in intents
        assert StrokeIntent.CONSTRUCTION in intents
    
    def test_get_recommended_intents_stylization(self):
        """Test recommended intents for stylization phase."""
        intents = StrokeIntentHelper.get_recommended_intents(DrawingPhase.STYLIZATION)
        assert StrokeIntent.CONTOUR in intents
        assert StrokeIntent.DETAIL in intents
        assert StrokeIntent.CLEANUP in intents
    
    def test_get_recommended_intents_rendering(self):
        """Test recommended intents for rendering phase."""
        intents = StrokeIntentHelper.get_recommended_intents(DrawingPhase.RENDERING)
        assert StrokeIntent.DETAIL in intents
        assert StrokeIntent.SHADING in intents
        assert StrokeIntent.CLEANUP in intents
    
    def test_get_primary_intent(self):
        """Test getting primary intent for phases."""
        assert StrokeIntentHelper.get_primary_intent(DrawingPhase.SKETCH) == StrokeIntent.GESTURE
        assert StrokeIntentHelper.get_primary_intent(DrawingPhase.REFINEMENT) == StrokeIntent.CONTOUR
        assert StrokeIntentHelper.get_primary_intent(DrawingPhase.STYLIZATION) == StrokeIntent.CONTOUR
        assert StrokeIntentHelper.get_primary_intent(DrawingPhase.RENDERING) == StrokeIntent.DETAIL
    
    def test_is_intent_appropriate(self):
        """Test checking if intent is appropriate for phase."""
        # Gesture is appropriate for sketch
        assert StrokeIntentHelper.is_intent_appropriate(
            DrawingPhase.SKETCH, StrokeIntent.GESTURE
        )
        
        # Detail is not appropriate for sketch
        assert not StrokeIntentHelper.is_intent_appropriate(
            DrawingPhase.SKETCH, StrokeIntent.DETAIL
        )
        
        # Shading is appropriate for rendering
        assert StrokeIntentHelper.is_intent_appropriate(
            DrawingPhase.RENDERING, StrokeIntent.SHADING
        )
    
    def test_suggest_intent_for_task(self):
        """Test suggesting intent based on task type."""
        # fix_pose should suggest GESTURE
        intent = StrokeIntentHelper.suggest_intent_for_task(
            DrawingPhase.SKETCH, "fix_pose"
        )
        assert intent == StrokeIntent.GESTURE
        
        # refine_anatomy should suggest CONTOUR
        intent = StrokeIntentHelper.suggest_intent_for_task(
            DrawingPhase.REFINEMENT, "refine_anatomy"
        )
        assert intent == StrokeIntent.CONTOUR
        
        # add_detail should suggest DETAIL
        intent = StrokeIntentHelper.suggest_intent_for_task(
            DrawingPhase.RENDERING, "add_detail"
        )
        assert intent == StrokeIntent.DETAIL
    
    def test_suggest_intent_fallback(self):
        """Test intent suggestion fallback to phase primary."""
        # Unknown task type should use phase primary
        intent = StrokeIntentHelper.suggest_intent_for_task(
            DrawingPhase.REFINEMENT, "unknown_task"
        )
        assert intent == StrokeIntent.CONTOUR
