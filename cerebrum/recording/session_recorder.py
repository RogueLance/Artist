"""
Session recording module for capturing drawing process.

Records canvas states throughout the drawing process to enable
time-lapse visualization and progressive analysis.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
from PIL import Image
import json

logger = logging.getLogger(__name__)


@dataclass
class CanvasSnapshot:
    """A snapshot of the canvas at a specific point in time."""
    timestamp: float
    iteration: int
    stage: str
    canvas_data: np.ndarray
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


class SessionRecorder:
    """
    Records drawing session progress for visualization and analysis.
    
    Captures canvas states at key points during the drawing process,
    enabling time-lapse generation and progressive analysis.
    
    Example:
        >>> recorder = SessionRecorder(session_name="portrait_study")
        >>> recorder.start()
        >>> 
        >>> # During drawing process
        >>> recorder.record_snapshot(
        ...     canvas_data=canvas_array,
        ...     stage="gesture",
        ...     metrics={"quality": 0.5}
        ... )
        >>> 
        >>> recorder.stop()
        >>> recorder.save("/tmp/sessions/")
    """
    
    def __init__(
        self,
        session_name: Optional[str] = None,
        record_frequency: str = "stage"  # "stage", "iteration", "action"
    ):
        """
        Initialize session recorder.
        
        Args:
            session_name: Name for this recording session
            record_frequency: How often to record ("stage", "iteration", "action")
        """
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.record_frequency = record_frequency
        
        self.snapshots: List[CanvasSnapshot] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.iteration_count = 0
        self.metadata: Dict[str, Any] = {}
        
        self._is_recording = False
    
    def start(self):
        """Start recording session."""
        import time
        self.start_time = time.time()
        self._is_recording = True
        self.metadata["start_time"] = datetime.now().isoformat()
        logger.info(f"Recording started: {self.session_name}")
    
    def stop(self):
        """Stop recording session."""
        import time
        self.end_time = time.time()
        self._is_recording = False
        self.metadata["end_time"] = datetime.now().isoformat()
        
        if self.start_time:
            duration = self.end_time - self.start_time
            self.metadata["duration_seconds"] = duration
        
        logger.info(f"Recording stopped: {self.session_name} ({len(self.snapshots)} snapshots)")
    
    def record_snapshot(
        self,
        canvas_data: np.ndarray,
        stage: str,
        metrics: Optional[Dict[str, Any]] = None,
        notes: str = ""
    ):
        """
        Record a canvas snapshot.
        
        Args:
            canvas_data: Current canvas state as numpy array
            stage: Current stage name
            metrics: Optional metrics for this snapshot
            notes: Optional notes about this snapshot
        """
        if not self._is_recording:
            logger.warning("Cannot record snapshot - recording not started")
            return
        
        import time
        timestamp = time.time() - (self.start_time or 0)
        
        snapshot = CanvasSnapshot(
            timestamp=timestamp,
            iteration=self.iteration_count,
            stage=stage,
            canvas_data=canvas_data.copy(),
            metrics=metrics or {},
            notes=notes
        )
        
        self.snapshots.append(snapshot)
        logger.debug(f"Snapshot recorded: {stage} at {timestamp:.2f}s")
    
    def increment_iteration(self):
        """Increment iteration counter."""
        self.iteration_count += 1
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the recording."""
        self.metadata[key] = value
    
    def get_snapshots_by_stage(self, stage: str) -> List[CanvasSnapshot]:
        """Get all snapshots for a specific stage."""
        return [s for s in self.snapshots if s.stage == stage]
    
    def get_snapshot_at_time(self, timestamp: float) -> Optional[CanvasSnapshot]:
        """Get snapshot closest to specified timestamp."""
        if not self.snapshots:
            return None
        
        closest = min(self.snapshots, key=lambda s: abs(s.timestamp - timestamp))
        return closest
    
    def save(self, output_dir: Path):
        """
        Save recording session to disk.
        
        Args:
            output_dir: Directory to save recording
        """
        output_dir = Path(output_dir)
        session_dir = output_dir / self.session_name
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save snapshots as images
        snapshots_dir = session_dir / "snapshots"
        snapshots_dir.mkdir(exist_ok=True)
        
        snapshot_info = []
        
        for i, snapshot in enumerate(self.snapshots):
            # Save image
            filename = f"snapshot_{i:04d}_{snapshot.stage}.png"
            image_path = snapshots_dir / filename
            Image.fromarray(snapshot.canvas_data).save(image_path)
            
            # Record info
            snapshot_info.append({
                "index": i,
                "filename": filename,
                "timestamp": snapshot.timestamp,
                "iteration": snapshot.iteration,
                "stage": snapshot.stage,
                "metrics": snapshot.metrics,
                "notes": snapshot.notes
            })
        
        # Save metadata
        metadata = {
            "session_name": self.session_name,
            "record_frequency": self.record_frequency,
            "total_snapshots": len(self.snapshots),
            "total_iterations": self.iteration_count,
            **self.metadata
        }
        
        metadata_path = session_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save snapshot info
        snapshots_path = session_dir / "snapshots.json"
        with open(snapshots_path, 'w') as f:
            json.dump(snapshot_info, f, indent=2)
        
        logger.info(f"Session saved to {session_dir}")
        return session_dir
    
    @classmethod
    def load(cls, session_dir: Path) -> 'SessionRecorder':
        """
        Load a recording session from disk.
        
        Args:
            session_dir: Directory containing saved session
            
        Returns:
            Loaded SessionRecorder instance
        """
        session_dir = Path(session_dir)
        
        # Load metadata
        metadata_path = session_dir / "metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Load snapshot info
        snapshots_path = session_dir / "snapshots.json"
        with open(snapshots_path, 'r') as f:
            snapshot_info = json.load(f)
        
        # Create recorder
        recorder = cls(
            session_name=metadata["session_name"],
            record_frequency=metadata["record_frequency"]
        )
        recorder.metadata = metadata
        recorder.iteration_count = metadata["total_iterations"]
        
        # Load snapshots
        snapshots_dir = session_dir / "snapshots"
        for info in snapshot_info:
            image_path = snapshots_dir / info["filename"]
            canvas_data = np.array(Image.open(image_path))
            
            snapshot = CanvasSnapshot(
                timestamp=info["timestamp"],
                iteration=info["iteration"],
                stage=info["stage"],
                canvas_data=canvas_data,
                metrics=info["metrics"],
                notes=info["notes"]
            )
            recorder.snapshots.append(snapshot)
        
        logger.info(f"Session loaded from {session_dir}")
        return recorder
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of recording session."""
        return {
            "session_name": self.session_name,
            "total_snapshots": len(self.snapshots),
            "total_iterations": self.iteration_count,
            "stages": list(set(s.stage for s in self.snapshots)),
            "duration": self.metadata.get("duration_seconds"),
            "is_recording": self._is_recording
        }
