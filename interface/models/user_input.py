"""
User input data structures.
"""

from enum import Enum
from typing import Optional, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime


class InputType(Enum):
    """Types of user input."""
    SKETCH = "sketch"
    REFERENCE = "reference"
    AI_IMAGE = "ai_image"
    GOAL = "goal"
    DECISION = "decision"
    COMMAND = "command"


class UserDecision(Enum):
    """User decision types."""
    APPROVE = "approve"
    REJECT = "reject"
    SKIP = "skip"
    MODIFY = "modify"


@dataclass
class UserInput:
    """
    Represents a user input action.
    
    Attributes:
        input_type: Type of input
        value: Input value (path, text, decision, etc.)
        timestamp: When the input was received
        metadata: Additional metadata about the input
        context: Context in which input was provided
    """
    input_type: InputType
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'input_type': self.input_type.value,
            'value': str(self.value),
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserInput':
        """Create UserInput from dictionary."""
        return cls(
            input_type=InputType(data['input_type']),
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            context=data.get('context')
        )
