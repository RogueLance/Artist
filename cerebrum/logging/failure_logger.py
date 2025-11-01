"""
Failure logging and classification system.

Tracks and classifies failures by system component (Motor, Vision, Brain, Integration)
to help diagnose issues and improve the system.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class FailureComponent(Enum):
    """Component where failure occurred."""
    MOTOR = "motor"
    VISION = "vision"
    BRAIN = "brain"
    INTEGRATION = "integration"
    PIPELINE = "pipeline"
    UNKNOWN = "unknown"


class FailureSeverity(Enum):
    """Severity level of failure."""
    CRITICAL = "critical"  # Complete failure, no output
    HIGH = "high"  # Major issues, output unusable
    MEDIUM = "medium"  # Significant issues, output degraded
    LOW = "low"  # Minor issues, output acceptable
    WARNING = "warning"  # Potential issue, no immediate impact


@dataclass
class FailureRecord:
    """Record of a failure occurrence."""
    timestamp: str
    component: FailureComponent
    severity: FailureSeverity
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    resolved: bool = False
    resolution_notes: str = ""


class FailureLogger:
    """
    Logger for tracking and analyzing system failures.
    
    Provides structured logging of failures with classification by component
    and severity, enabling systematic analysis and improvement.
    
    Example:
        >>> logger = FailureLogger("test_session")
        >>> 
        >>> # Log a failure
        >>> logger.log_failure(
        ...     component=FailureComponent.MOTOR,
        ...     severity=FailureSeverity.HIGH,
        ...     description="Stroke execution failed",
        ...     context={"stroke_id": "123", "error": "Invalid point"}
        ... )
        >>> 
        >>> # Get statistics
        >>> stats = logger.get_statistics()
        >>> print(f"Total failures: {stats['total_failures']}")
        >>> 
        >>> # Save log
        >>> logger.save("/tmp/logs/")
    """
    
    def __init__(self, session_name: Optional[str] = None):
        """
        Initialize failure logger.
        
        Args:
            session_name: Name for this logging session
        """
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.failures: List[FailureRecord] = []
        self.metadata: Dict[str, Any] = {
            "session_name": self.session_name,
            "start_time": datetime.now().isoformat()
        }
    
    def log_failure(
        self,
        component: FailureComponent,
        severity: FailureSeverity,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> FailureRecord:
        """
        Log a failure occurrence.
        
        Args:
            component: Component where failure occurred
            severity: Severity level
            description: Description of the failure
            context: Additional context information
            stack_trace: Optional stack trace
            
        Returns:
            Created FailureRecord
        """
        record = FailureRecord(
            timestamp=datetime.now().isoformat(),
            component=component,
            severity=severity,
            description=description,
            context=context or {},
            stack_trace=stack_trace
        )
        
        self.failures.append(record)
        
        # Also log to standard logger
        log_level = self._severity_to_log_level(severity)
        logger.log(
            log_level,
            f"[{component.value}] {description}",
            extra={"context": context}
        )
        
        return record
    
    def log_motor_failure(
        self,
        description: str,
        severity: FailureSeverity = FailureSeverity.MEDIUM,
        **context
    ):
        """Log a Motor system failure."""
        return self.log_failure(
            component=FailureComponent.MOTOR,
            severity=severity,
            description=description,
            context=context
        )
    
    def log_vision_failure(
        self,
        description: str,
        severity: FailureSeverity = FailureSeverity.MEDIUM,
        **context
    ):
        """Log a Vision system failure."""
        return self.log_failure(
            component=FailureComponent.VISION,
            severity=severity,
            description=description,
            context=context
        )
    
    def log_brain_failure(
        self,
        description: str,
        severity: FailureSeverity = FailureSeverity.MEDIUM,
        **context
    ):
        """Log a Brain system failure."""
        return self.log_failure(
            component=FailureComponent.BRAIN,
            severity=severity,
            description=description,
            context=context
        )
    
    def log_integration_failure(
        self,
        description: str,
        severity: FailureSeverity = FailureSeverity.HIGH,
        **context
    ):
        """Log an Integration failure."""
        return self.log_failure(
            component=FailureComponent.INTEGRATION,
            severity=severity,
            description=description,
            context=context
        )
    
    def log_pipeline_failure(
        self,
        description: str,
        severity: FailureSeverity = FailureSeverity.HIGH,
        **context
    ):
        """Log a Pipeline failure."""
        return self.log_failure(
            component=FailureComponent.PIPELINE,
            severity=severity,
            description=description,
            context=context
        )
    
    def mark_resolved(
        self,
        failure_index: int,
        resolution_notes: str = ""
    ):
        """
        Mark a failure as resolved.
        
        Args:
            failure_index: Index of failure in failures list
            resolution_notes: Notes about the resolution
        """
        if 0 <= failure_index < len(self.failures):
            self.failures[failure_index].resolved = True
            self.failures[failure_index].resolution_notes = resolution_notes
            logger.info(f"Failure {failure_index} marked as resolved")
    
    def get_failures_by_component(
        self,
        component: FailureComponent
    ) -> List[FailureRecord]:
        """Get all failures for a specific component."""
        return [f for f in self.failures if f.component == component]
    
    def get_failures_by_severity(
        self,
        severity: FailureSeverity
    ) -> List[FailureRecord]:
        """Get all failures of a specific severity."""
        return [f for f in self.failures if f.severity == severity]
    
    def get_unresolved_failures(self) -> List[FailureRecord]:
        """Get all unresolved failures."""
        return [f for f in self.failures if not f.resolved]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get failure statistics.
        
        Returns:
            Dictionary with failure statistics by component and severity
        """
        stats = {
            "total_failures": len(self.failures),
            "unresolved_failures": len(self.get_unresolved_failures()),
            "by_component": {},
            "by_severity": {},
            "resolution_rate": 0.0
        }
        
        # Count by component
        for component in FailureComponent:
            count = len(self.get_failures_by_component(component))
            if count > 0:
                stats["by_component"][component.value] = count
        
        # Count by severity
        for severity in FailureSeverity:
            count = len(self.get_failures_by_severity(severity))
            if count > 0:
                stats["by_severity"][severity.value] = count
        
        # Calculate resolution rate
        if self.failures:
            resolved_count = len([f for f in self.failures if f.resolved])
            stats["resolution_rate"] = resolved_count / len(self.failures)
        
        return stats
    
    def generate_report(self) -> str:
        """
        Generate human-readable failure report.
        
        Returns:
            Formatted report string
        """
        stats = self.get_statistics()
        
        report = []
        report.append("=" * 60)
        report.append(f"Failure Report: {self.session_name}")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Total Failures: {stats['total_failures']}")
        report.append(f"Unresolved: {stats['unresolved_failures']}")
        report.append(f"Resolution Rate: {stats['resolution_rate']:.1%}")
        report.append("")
        
        # By component
        report.append("By Component:")
        for component, count in sorted(stats["by_component"].items()):
            report.append(f"  {component}: {count}")
        report.append("")
        
        # By severity
        report.append("By Severity:")
        for severity, count in sorted(stats["by_severity"].items()):
            report.append(f"  {severity}: {count}")
        report.append("")
        
        # Recent unresolved failures
        unresolved = self.get_unresolved_failures()
        if unresolved:
            report.append("Recent Unresolved Failures:")
            for i, failure in enumerate(unresolved[-5:], 1):  # Last 5
                report.append(f"  {i}. [{failure.severity.value}] {failure.description}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save(self, output_dir: Path):
        """
        Save failure log to disk.
        
        Args:
            output_dir: Directory to save log
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = output_dir / f"{self.session_name}_failures.json"
        
        # Prepare data
        data = {
            "metadata": self.metadata,
            "statistics": self.get_statistics(),
            "failures": [
                {
                    "timestamp": f.timestamp,
                    "component": f.component.value,
                    "severity": f.severity.value,
                    "description": f.description,
                    "context": f.context,
                    "stack_trace": f.stack_trace,
                    "resolved": f.resolved,
                    "resolution_notes": f.resolution_notes
                }
                for f in self.failures
            ]
        }
        
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save text report
        report_file = output_dir / f"{self.session_name}_report.txt"
        with open(report_file, 'w') as f:
            f.write(self.generate_report())
        
        logger.info(f"Failure log saved to {output_dir}")
    
    @classmethod
    def load(cls, log_file: Path) -> 'FailureLogger':
        """
        Load failure log from disk.
        
        Args:
            log_file: Path to JSON log file
            
        Returns:
            Loaded FailureLogger instance
        """
        log_file = Path(log_file)
        
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        # Create logger
        failure_logger = cls(session_name=data["metadata"]["session_name"])
        failure_logger.metadata = data["metadata"]
        
        # Load failures
        for f_data in data["failures"]:
            record = FailureRecord(
                timestamp=f_data["timestamp"],
                component=FailureComponent(f_data["component"]),
                severity=FailureSeverity(f_data["severity"]),
                description=f_data["description"],
                context=f_data["context"],
                stack_trace=f_data.get("stack_trace"),
                resolved=f_data["resolved"],
                resolution_notes=f_data["resolution_notes"]
            )
            failure_logger.failures.append(record)
        
        logger.info(f"Failure log loaded from {log_file}")
        return failure_logger
    
    def _severity_to_log_level(self, severity: FailureSeverity) -> int:
        """Convert FailureSeverity to logging level."""
        mapping = {
            FailureSeverity.CRITICAL: logging.CRITICAL,
            FailureSeverity.HIGH: logging.ERROR,
            FailureSeverity.MEDIUM: logging.WARNING,
            FailureSeverity.LOW: logging.INFO,
            FailureSeverity.WARNING: logging.WARNING
        }
        return mapping.get(severity, logging.WARNING)
