"""
Decision Logging System.

Tracks decisions, strokes, and evaluations at each phase for replay
and analysis.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from workflow.models.drawing_phase import DrawingPhase
from workflow.models.stroke_intent import StrokeIntent


@dataclass
class StrokeDecision:
    """
    Record of a stroke decision and execution.
    
    Attributes:
        stroke_id: Unique stroke identifier
        timestamp: When stroke was executed
        intent: Stroke intent/purpose
        phase: Phase when stroke was executed
        task_id: Associated task ID
        action_id: Associated action ID
        purpose: Human-readable purpose
        pre_evaluation: Evaluation before stroke
        post_evaluation: Evaluation after stroke
        stroke_data: Serialized stroke data
        metadata: Additional metadata
    """
    stroke_id: str
    timestamp: datetime
    intent: StrokeIntent
    phase: DrawingPhase
    task_id: Optional[str] = None
    action_id: Optional[str] = None
    purpose: str = ""
    pre_evaluation: Optional[Dict[str, float]] = None
    post_evaluation: Optional[Dict[str, float]] = None
    stroke_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_improvement_score(self) -> Optional[float]:
        """
        Calculate improvement from pre to post evaluation.
        
        Returns:
            Improvement score or None if evaluations missing
        """
        if self.pre_evaluation and self.post_evaluation:
            # Average improvement across all metrics
            pre_avg = sum(self.pre_evaluation.values()) / len(self.pre_evaluation)
            post_avg = sum(self.post_evaluation.values()) / len(self.post_evaluation)
            return post_avg - pre_avg
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stroke_id": self.stroke_id,
            "timestamp": self.timestamp.isoformat(),
            "intent": self.intent.value,
            "phase": self.phase.value,
            "task_id": self.task_id,
            "action_id": self.action_id,
            "purpose": self.purpose,
            "pre_evaluation": self.pre_evaluation,
            "post_evaluation": self.post_evaluation,
            "stroke_data": self.stroke_data,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrokeDecision':
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["intent"] = StrokeIntent(data["intent"])
        data["phase"] = DrawingPhase(data["phase"])
        return cls(**data)


@dataclass
class PhaseDecisionLog:
    """
    Log of all decisions made during a specific phase.
    
    Attributes:
        phase: Drawing phase
        start_time: When phase started
        end_time: When phase ended
        strokes: List of stroke decisions
        phase_evaluations: Periodic evaluations during phase
        transition_reason: Why phase transitioned
        total_improvement: Overall improvement during phase
        metadata: Additional phase metadata
    """
    phase: DrawingPhase
    start_time: datetime
    end_time: Optional[datetime] = None
    strokes: List[StrokeDecision] = field(default_factory=list)
    phase_evaluations: List[Dict[str, Any]] = field(default_factory=list)
    transition_reason: str = ""
    total_improvement: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_stroke_decision(self, decision: StrokeDecision):
        """Add a stroke decision to the log."""
        self.strokes.append(decision)
    
    def add_evaluation(self, evaluation: Dict[str, Any]):
        """Add a phase evaluation."""
        self.phase_evaluations.append({
            "timestamp": datetime.now().isoformat(),
            "evaluation": evaluation,
        })
    
    def close_phase(self, reason: str = ""):
        """Mark phase as complete."""
        self.end_time = datetime.now()
        self.transition_reason = reason
        
        # Calculate total improvement
        if self.strokes:
            improvements = [
                s.get_improvement_score() 
                for s in self.strokes 
                if s.get_improvement_score() is not None
            ]
            if improvements:
                self.total_improvement = sum(improvements) / len(improvements)
    
    def get_phase_duration(self) -> Optional[float]:
        """
        Get phase duration in seconds.
        
        Returns:
            Duration or None if phase not ended
        """
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_stroke_count(self) -> int:
        """Get number of strokes in this phase."""
        return len(self.strokes)
    
    def get_strokes_by_intent(self, intent: StrokeIntent) -> List[StrokeDecision]:
        """
        Get strokes filtered by intent.
        
        Args:
            intent: Stroke intent to filter by
            
        Returns:
            List of matching stroke decisions
        """
        return [s for s in self.strokes if s.intent == intent]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get phase summary."""
        return {
            "phase": self.phase.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_phase_duration(),
            "stroke_count": self.get_stroke_count(),
            "evaluation_count": len(self.phase_evaluations),
            "total_improvement": self.total_improvement,
            "transition_reason": self.transition_reason,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase": self.phase.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "strokes": [s.to_dict() for s in self.strokes],
            "phase_evaluations": self.phase_evaluations,
            "transition_reason": self.transition_reason,
            "total_improvement": self.total_improvement,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhaseDecisionLog':
        """Create from dictionary."""
        data = data.copy()
        data["phase"] = DrawingPhase(data["phase"])
        data["start_time"] = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        data["strokes"] = [StrokeDecision.from_dict(s) for s in data.get("strokes", [])]
        return cls(**data)


class DecisionLogger:
    """
    Manages decision logging across the entire workflow.
    
    Tracks all decisions, strokes, and evaluations throughout the
    drawing process for analysis and replay.
    """
    
    def __init__(self):
        """Initialize decision logger."""
        self.phase_logs: List[PhaseDecisionLog] = []
        self.current_log: Optional[PhaseDecisionLog] = None
    
    def start_phase(self, phase: DrawingPhase, metadata: Optional[Dict[str, Any]] = None):
        """
        Start logging a new phase.
        
        Args:
            phase: Drawing phase starting
            metadata: Additional phase metadata
        """
        # Close previous phase if exists
        if self.current_log and self.current_log.end_time is None:
            self.current_log.close_phase("Phase transition")
        
        # Create new log
        self.current_log = PhaseDecisionLog(
            phase=phase,
            start_time=datetime.now(),
            metadata=metadata or {},
        )
        self.phase_logs.append(self.current_log)
    
    def log_stroke(
        self,
        stroke_id: str,
        intent: StrokeIntent,
        phase: DrawingPhase,
        purpose: str = "",
        task_id: Optional[str] = None,
        action_id: Optional[str] = None,
        pre_evaluation: Optional[Dict[str, float]] = None,
        post_evaluation: Optional[Dict[str, float]] = None,
        stroke_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log a stroke decision.
        
        Args:
            stroke_id: Unique stroke identifier
            intent: Stroke intent
            phase: Current phase
            purpose: Stroke purpose
            task_id: Associated task ID
            action_id: Associated action ID
            pre_evaluation: Evaluation before stroke
            post_evaluation: Evaluation after stroke
            stroke_data: Serialized stroke data
            metadata: Additional metadata
        """
        if not self.current_log:
            self.start_phase(phase)
        
        decision = StrokeDecision(
            stroke_id=stroke_id,
            timestamp=datetime.now(),
            intent=intent,
            phase=phase,
            task_id=task_id,
            action_id=action_id,
            purpose=purpose,
            pre_evaluation=pre_evaluation,
            post_evaluation=post_evaluation,
            stroke_data=stroke_data,
            metadata=metadata or {},
        )
        
        self.current_log.add_stroke_decision(decision)
    
    def log_evaluation(self, evaluation: Dict[str, Any]):
        """
        Log a phase evaluation.
        
        Args:
            evaluation: Evaluation metrics
        """
        if self.current_log:
            self.current_log.add_evaluation(evaluation)
    
    def close_phase(self, reason: str = ""):
        """
        Close the current phase log.
        
        Args:
            reason: Reason for closing phase
        """
        if self.current_log:
            self.current_log.close_phase(reason)
    
    def get_phase_log(self, phase: DrawingPhase) -> Optional[PhaseDecisionLog]:
        """
        Get the most recent log for a phase.
        
        Args:
            phase: Phase to get log for
            
        Returns:
            Phase log or None if not found
        """
        for log in reversed(self.phase_logs):
            if log.phase == phase:
                return log
        return None
    
    def get_all_phase_logs(self, phase: DrawingPhase) -> List[PhaseDecisionLog]:
        """
        Get all logs for a specific phase.
        
        Args:
            phase: Phase to filter by
            
        Returns:
            List of phase logs
        """
        return [log for log in self.phase_logs if log.phase == phase]
    
    def get_all_strokes(self) -> List[StrokeDecision]:
        """
        Get all stroke decisions across all phases.
        
        Returns:
            List of all stroke decisions
        """
        all_strokes = []
        for log in self.phase_logs:
            all_strokes.extend(log.strokes)
        return all_strokes
    
    def get_total_stroke_count(self) -> int:
        """Get total number of logged strokes."""
        return sum(log.get_stroke_count() for log in self.phase_logs)
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get summary of entire workflow.
        
        Returns:
            Workflow summary dictionary
        """
        return {
            "total_phases": len(self.phase_logs),
            "total_strokes": self.get_total_stroke_count(),
            "phase_summaries": [log.get_summary() for log in self.phase_logs],
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phase_logs": [log.to_dict() for log in self.phase_logs],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionLogger':
        """Create from dictionary."""
        logger = cls()
        logger.phase_logs = [
            PhaseDecisionLog.from_dict(log) for log in data.get("phase_logs", [])
        ]
        if logger.phase_logs:
            logger.current_log = logger.phase_logs[-1]
        return logger
