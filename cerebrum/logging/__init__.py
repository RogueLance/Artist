"""
Logging module for failure tracking and classification.
"""

from cerebrum.logging.failure_logger import (
    FailureLogger,
    FailureRecord,
    FailureComponent,
    FailureSeverity
)

__all__ = [
    "FailureLogger",
    "FailureRecord",
    "FailureComponent",
    "FailureSeverity",
]
