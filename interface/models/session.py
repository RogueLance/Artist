"""
Session management for the interface.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from interface.models.user_input import UserInput


@dataclass
class SessionConfig:
    """
    Configuration for an interface session.
    
    Attributes:
        canvas_width: Canvas width in pixels
        canvas_height: Canvas height in pixels
        max_iterations: Maximum refinement iterations
        auto_save: Auto-save canvas after each iteration
        log_file: Path to log file
        output_dir: Directory for output files
        enable_vision: Enable Vision module
        enable_brain: Enable Brain module
        interactive: Run in interactive mode
    """
    canvas_width: int = 800
    canvas_height: int = 600
    max_iterations: int = 10
    auto_save: bool = True
    log_file: Optional[Path] = None
    output_dir: Path = field(default_factory=lambda: Path("output"))
    enable_vision: bool = True
    enable_brain: bool = True
    interactive: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'canvas_width': self.canvas_width,
            'canvas_height': self.canvas_height,
            'max_iterations': self.max_iterations,
            'auto_save': self.auto_save,
            'log_file': str(self.log_file) if self.log_file else None,
            'output_dir': str(self.output_dir),
            'enable_vision': self.enable_vision,
            'enable_brain': self.enable_brain,
            'interactive': self.interactive
        }


@dataclass
class Session:
    """
    Represents an interface session.
    
    Tracks user inputs, system actions, and evaluation scores throughout
    a working session.
    
    Attributes:
        session_id: Unique session identifier
        config: Session configuration
        start_time: Session start time
        end_time: Session end time (if completed)
        goal: User's artistic goal
        inputs: List of user inputs
        actions: List of system actions
        evaluations: Evaluation scores and results
        current_iteration: Current iteration number
        canvas_states: History of canvas states (file paths)
    """
    session_id: str
    config: SessionConfig
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    goal: Optional[str] = None
    inputs: List[UserInput] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    evaluations: List[Dict[str, Any]] = field(default_factory=list)
    current_iteration: int = 0
    canvas_states: List[str] = field(default_factory=list)
    
    def add_input(self, user_input: UserInput):
        """Add a user input to the session."""
        self.inputs.append(user_input)
    
    def add_action(self, action: Dict[str, Any]):
        """Add a system action to the session."""
        action['timestamp'] = datetime.now().isoformat()
        self.actions.append(action)
    
    def add_evaluation(self, evaluation: Dict[str, Any]):
        """Add an evaluation result to the session."""
        evaluation['timestamp'] = datetime.now().isoformat()
        evaluation['iteration'] = self.current_iteration
        self.evaluations.append(evaluation)
    
    def add_canvas_state(self, canvas_path: str):
        """Record a canvas state."""
        self.canvas_states.append(canvas_path)
    
    def increment_iteration(self):
        """Increment the iteration counter."""
        self.current_iteration += 1
    
    def complete(self):
        """Mark the session as complete."""
        self.end_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'config': self.config.to_dict(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'goal': self.goal,
            'inputs': [inp.to_dict() for inp in self.inputs],
            'actions': self.actions,
            'evaluations': self.evaluations,
            'current_iteration': self.current_iteration,
            'canvas_states': self.canvas_states
        }
    
    def save(self, path: Path):
        """Save session to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'Session':
        """Load session from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        config = SessionConfig(**{k: v for k, v in data['config'].items() if k in SessionConfig.__annotations__})
        session = cls(
            session_id=data['session_id'],
            config=config,
            start_time=datetime.fromisoformat(data['start_time']),
            goal=data.get('goal'),
            current_iteration=data.get('current_iteration', 0)
        )
        
        if data.get('end_time'):
            session.end_time = datetime.fromisoformat(data['end_time'])
        
        session.inputs = [UserInput.from_dict(inp) for inp in data.get('inputs', [])]
        session.actions = data.get('actions', [])
        session.evaluations = data.get('evaluations', [])
        session.canvas_states = data.get('canvas_states', [])
        
        return session
