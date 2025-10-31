"""
Vision System - Canvas Analysis Engine for Cerebrum AI Art Platform.

The Vision System provides perception capabilities for analyzing canvas state,
detecting poses and anatomy, comparing to references, and identifying areas
needing refinement.

Main Components:
    - VisionModule: Primary API for vision analysis
    - PoseDetector: Pose estimation using MediaPipe
    - LandmarkDetector: Face and hand landmark detection
    - Comparator: Comparison metrics and analysis
    - ImageProcessor: Image loading and preprocessing

Example:
    >>> from vision import VisionModule
    >>> vision = VisionModule()
    >>> 
    >>> # Analyze canvas
    >>> result = vision.analyze("canvas.png")
    >>> if result.has_pose():
    ...     print(f"Detected pose with {len(result.pose.keypoints)} keypoints")
    >>> 
    >>> # Compare to reference
    >>> comparison = vision.compare_to("canvas.png", "reference.png")
    >>> print(f"Similarity: {comparison.overall_similarity:.1%}")
    >>> 
    >>> # Detect errors
    >>> errors = vision.detect_pose_errors("canvas.png", "reference.png")
    >>> for error in errors:
    ...     print(f"- {error}")
"""

from vision.vision_module import VisionModule
from vision.core import ImageProcessor, PoseDetector, LandmarkDetector, Comparator
from vision.models import (
    AnalysisResult,
    ComparisonResult,
    PoseData,
    PoseKeypoint,
    Landmark,
    PoseLandmarks,
    FaceLandmarks,
    HandLandmarks,
    PoseMetrics,
    ProportionMetrics,
    SymmetryMetrics,
    AlignmentMetrics,
)

__version__ = "0.1.0"

__all__ = [
    "VisionModule",
    "ImageProcessor",
    "PoseDetector",
    "LandmarkDetector",
    "Comparator",
    "AnalysisResult",
    "ComparisonResult",
    "PoseData",
    "PoseKeypoint",
    "Landmark",
    "PoseLandmarks",
    "FaceLandmarks",
    "HandLandmarks",
    "PoseMetrics",
    "ProportionMetrics",
    "SymmetryMetrics",
    "AlignmentMetrics",
]
