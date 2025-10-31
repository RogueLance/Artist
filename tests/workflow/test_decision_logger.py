"""Tests for decision logger."""

import pytest

from workflow.models.drawing_phase import DrawingPhase
from workflow.models.stroke_intent import StrokeIntent
from workflow.core.decision_logger import (
    DecisionLogger,
    PhaseDecisionLog,
    StrokeDecision,
)


class TestStrokeDecision:
    """Test StrokeDecision class."""
    
    def test_create_decision(self):
        """Test creating a stroke decision."""
        from datetime import datetime
        
        decision = StrokeDecision(
            stroke_id="stroke_1",
            timestamp=datetime.now(),
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
            purpose="Initial layout",
            task_id="task_1",
        )
        
        assert decision.stroke_id == "stroke_1"
        assert decision.intent == StrokeIntent.GESTURE
        assert decision.phase == DrawingPhase.SKETCH
    
    def test_get_improvement_score(self):
        """Test calculating improvement score."""
        from datetime import datetime
        
        decision = StrokeDecision(
            stroke_id="stroke_1",
            timestamp=datetime.now(),
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
            pre_evaluation={"quality": 0.5, "accuracy": 0.6},
            post_evaluation={"quality": 0.7, "accuracy": 0.8},
        )
        
        improvement = decision.get_improvement_score()
        assert improvement > 0
        assert improvement == pytest.approx(0.2, abs=0.01)
    
    def test_serialization(self):
        """Test decision to/from dict."""
        from datetime import datetime
        
        decision = StrokeDecision(
            stroke_id="stroke_1",
            timestamp=datetime.now(),
            intent=StrokeIntent.CONTOUR,
            phase=DrawingPhase.REFINEMENT,
        )
        
        data = decision.to_dict()
        assert data["intent"] == "contour"
        
        restored = StrokeDecision.from_dict(data)
        assert restored.intent == decision.intent


class TestPhaseDecisionLog:
    """Test PhaseDecisionLog class."""
    
    def test_create_log(self):
        """Test creating a phase log."""
        from datetime import datetime
        
        log = PhaseDecisionLog(
            phase=DrawingPhase.SKETCH,
            start_time=datetime.now(),
        )
        
        assert log.phase == DrawingPhase.SKETCH
        assert log.end_time is None
        assert len(log.strokes) == 0
    
    def test_add_stroke_decision(self):
        """Test adding stroke decisions."""
        from datetime import datetime
        
        log = PhaseDecisionLog(
            phase=DrawingPhase.SKETCH,
            start_time=datetime.now(),
        )
        
        decision = StrokeDecision(
            stroke_id="stroke_1",
            timestamp=datetime.now(),
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
        )
        
        log.add_stroke_decision(decision)
        assert len(log.strokes) == 1
        assert log.get_stroke_count() == 1
    
    def test_add_evaluation(self):
        """Test adding evaluations."""
        from datetime import datetime
        
        log = PhaseDecisionLog(
            phase=DrawingPhase.SKETCH,
            start_time=datetime.now(),
        )
        
        log.add_evaluation({"quality": 0.7})
        assert len(log.phase_evaluations) == 1
    
    def test_close_phase(self):
        """Test closing a phase."""
        from datetime import datetime
        
        log = PhaseDecisionLog(
            phase=DrawingPhase.SKETCH,
            start_time=datetime.now(),
        )
        
        log.close_phase("Quality threshold met")
        assert log.end_time is not None
        assert log.transition_reason == "Quality threshold met"
    
    def test_get_strokes_by_intent(self):
        """Test filtering strokes by intent."""
        from datetime import datetime
        
        log = PhaseDecisionLog(
            phase=DrawingPhase.SKETCH,
            start_time=datetime.now(),
        )
        
        log.add_stroke_decision(StrokeDecision(
            stroke_id="s1",
            timestamp=datetime.now(),
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
        ))
        
        log.add_stroke_decision(StrokeDecision(
            stroke_id="s2",
            timestamp=datetime.now(),
            intent=StrokeIntent.CONSTRUCTION,
            phase=DrawingPhase.SKETCH,
        ))
        
        gesture_strokes = log.get_strokes_by_intent(StrokeIntent.GESTURE)
        assert len(gesture_strokes) == 1
    
    def test_serialization(self):
        """Test log to/from dict."""
        from datetime import datetime
        
        log = PhaseDecisionLog(
            phase=DrawingPhase.SKETCH,
            start_time=datetime.now(),
        )
        
        data = log.to_dict()
        assert data["phase"] == "sketch"
        
        restored = PhaseDecisionLog.from_dict(data)
        assert restored.phase == log.phase


class TestDecisionLogger:
    """Test DecisionLogger class."""
    
    def test_start_phase(self):
        """Test starting a new phase."""
        logger = DecisionLogger()
        logger.start_phase(DrawingPhase.SKETCH)
        
        assert logger.current_log is not None
        assert logger.current_log.phase == DrawingPhase.SKETCH
        assert len(logger.phase_logs) == 1
    
    def test_log_stroke(self):
        """Test logging a stroke."""
        logger = DecisionLogger()
        logger.start_phase(DrawingPhase.SKETCH)
        
        logger.log_stroke(
            stroke_id="stroke_1",
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
            purpose="Initial gesture",
        )
        
        assert logger.get_total_stroke_count() == 1
    
    def test_log_evaluation(self):
        """Test logging evaluation."""
        logger = DecisionLogger()
        logger.start_phase(DrawingPhase.SKETCH)
        
        logger.log_evaluation({"quality": 0.7})
        
        assert len(logger.current_log.phase_evaluations) == 1
    
    def test_close_phase(self):
        """Test closing a phase."""
        logger = DecisionLogger()
        logger.start_phase(DrawingPhase.SKETCH)
        
        logger.close_phase("Transition to refinement")
        
        assert logger.current_log.end_time is not None
    
    def test_phase_transition(self):
        """Test transitioning between phases."""
        logger = DecisionLogger()
        
        logger.start_phase(DrawingPhase.SKETCH)
        logger.log_stroke(
            stroke_id="s1",
            intent=StrokeIntent.GESTURE,
            phase=DrawingPhase.SKETCH,
        )
        
        # Start new phase (should close previous)
        logger.start_phase(DrawingPhase.REFINEMENT)
        
        assert len(logger.phase_logs) == 2
        assert logger.phase_logs[0].end_time is not None
        assert logger.current_log.phase == DrawingPhase.REFINEMENT
    
    def test_get_phase_log(self):
        """Test getting phase log."""
        logger = DecisionLogger()
        
        logger.start_phase(DrawingPhase.SKETCH)
        logger.start_phase(DrawingPhase.REFINEMENT)
        
        sketch_log = logger.get_phase_log(DrawingPhase.SKETCH)
        assert sketch_log is not None
        assert sketch_log.phase == DrawingPhase.SKETCH
    
    def test_get_all_phase_logs(self):
        """Test getting all logs for a phase."""
        logger = DecisionLogger()
        
        logger.start_phase(DrawingPhase.SKETCH)
        logger.start_phase(DrawingPhase.REFINEMENT)
        logger.start_phase(DrawingPhase.SKETCH)  # Second iteration
        
        sketch_logs = logger.get_all_phase_logs(DrawingPhase.SKETCH)
        assert len(sketch_logs) == 2
    
    def test_get_all_strokes(self):
        """Test getting all strokes."""
        logger = DecisionLogger()
        
        logger.start_phase(DrawingPhase.SKETCH)
        logger.log_stroke("s1", StrokeIntent.GESTURE, DrawingPhase.SKETCH)
        
        logger.start_phase(DrawingPhase.REFINEMENT)
        logger.log_stroke("s2", StrokeIntent.CONTOUR, DrawingPhase.REFINEMENT)
        
        all_strokes = logger.get_all_strokes()
        assert len(all_strokes) == 2
    
    def test_get_workflow_summary(self):
        """Test getting workflow summary."""
        logger = DecisionLogger()
        
        logger.start_phase(DrawingPhase.SKETCH)
        logger.log_stroke("s1", StrokeIntent.GESTURE, DrawingPhase.SKETCH)
        logger.start_phase(DrawingPhase.REFINEMENT)
        
        summary = logger.get_workflow_summary()
        assert summary["total_phases"] == 2
        assert summary["total_strokes"] == 1
    
    def test_serialization(self):
        """Test logger to/from dict."""
        logger = DecisionLogger()
        logger.start_phase(DrawingPhase.SKETCH)
        logger.log_stroke("s1", StrokeIntent.GESTURE, DrawingPhase.SKETCH)
        
        data = logger.to_dict()
        assert len(data["phase_logs"]) == 1
        
        restored = DecisionLogger.from_dict(data)
        assert len(restored.phase_logs) == 1
        assert restored.get_total_stroke_count() == 1
