"""
Logging utilities for the interface.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class InterfaceLogger:
    """
    Logger for interface actions and events.
    
    Provides structured logging of user inputs, system actions, and
    evaluation scores.
    """
    
    def __init__(self, log_file: Optional[Path] = None, console_level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            log_file: Path to log file (if None, only console logging)
            console_level: Console logging level
        """
        self.logger = logging.getLogger('cerebrum.interface')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        self.log_file = log_file
        self.event_log = []
    
    def log_user_input(self, input_type: str, value: Any, context: Optional[str] = None):
        """Log a user input event."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'user_input',
            'input_type': input_type,
            'value': str(value),
            'context': context
        }
        self.event_log.append(event)
        self.logger.info(f"User input: {input_type} = {value}")
        if context:
            self.logger.debug(f"  Context: {context}")
    
    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log a system action."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'system_action',
            'action': action,
            'details': details or {}
        }
        self.event_log.append(event)
        self.logger.info(f"Action: {action}")
        if details:
            self.logger.debug(f"  Details: {details}")
    
    def log_evaluation(self, task: str, scores: Dict[str, float], result: str):
        """Log an evaluation result."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'evaluation',
            'task': task,
            'scores': scores,
            'result': result
        }
        self.event_log.append(event)
        self.logger.info(f"Evaluation: {task} -> {result}")
        self.logger.debug(f"  Scores: {scores}")
    
    def log_decision(self, decision: str, context: str, reason: Optional[str] = None):
        """Log a user decision."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'decision',
            'decision': decision,
            'context': context,
            'reason': reason
        }
        self.event_log.append(event)
        self.logger.info(f"Decision: {decision} ({context})")
        if reason:
            self.logger.debug(f"  Reason: {reason}")
    
    def log_iteration(self, iteration: int, message: str):
        """Log an iteration event."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'iteration',
            'iteration': iteration,
            'message': message
        }
        self.event_log.append(event)
        self.logger.info(f"Iteration {iteration}: {message}")
    
    def save_event_log(self, path: Path):
        """Save event log to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.event_log, f, indent=2)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
