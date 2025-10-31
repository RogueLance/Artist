"""
Analysis result data structures.

Contains the main result objects returned by vision analysis operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np

from vision.models.landmarks import FaceLandmarks, HandLandmarks, PoseLandmarks
from vision.models.pose_data import PoseData
from vision.models.comparison_metrics import (
    PoseMetrics,
    ProportionMetrics,
    SymmetryMetrics,
    AlignmentMetrics,
)


@dataclass
class AnalysisResult:
    """
    Result of analyzing a single image.
    
    Contains all detected features, landmarks, and metadata from the analysis.
    """
    # Image info
    image_width: int = 0
    image_height: int = 0
    
    # Detected features
    pose: Optional[PoseData] = None
    face_landmarks: Optional[FaceLandmarks] = None
    hand_landmarks: List[HandLandmarks] = field(default_factory=list)
    pose_landmarks: Optional[PoseLandmarks] = None
    
    # Image analysis
    silhouette: Optional[np.ndarray] = None  # Binary mask
    edges: Optional[np.ndarray] = None  # Edge detection result
    
    # Metrics
    proportion_metrics: Optional[ProportionMetrics] = None
    symmetry_metrics: Optional[SymmetryMetrics] = None
    
    # Metadata
    detection_confidence: float = 0.0
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_pose(self) -> bool:
        """Check if pose was detected."""
        return self.pose is not None or self.pose_landmarks is not None
    
    def has_face(self) -> bool:
        """Check if face was detected."""
        return self.face_landmarks is not None
    
    def has_hands(self) -> bool:
        """Check if hands were detected."""
        return len(self.hand_landmarks) > 0
    
    def get_detected_features(self) -> List[str]:
        """Get list of detected features."""
        features = []
        if self.has_pose():
            features.append("pose")
        if self.has_face():
            features.append("face")
        if self.has_hands():
            features.append(f"hands({len(self.hand_landmarks)})")
        return features
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes large numpy arrays)."""
        result = {
            "image_width": self.image_width,
            "image_height": self.image_height,
            "has_pose": self.has_pose(),
            "has_face": self.has_face(),
            "has_hands": self.has_hands(),
            "detection_confidence": self.detection_confidence,
            "processing_time_ms": self.processing_time_ms,
            "detected_features": self.get_detected_features(),
            "metadata": self.metadata,
        }
        
        if self.pose:
            result["pose"] = self.pose.to_dict()
        if self.face_landmarks:
            result["face_landmarks"] = self.face_landmarks.to_dict()
        if self.hand_landmarks:
            result["hand_landmarks"] = [h.to_dict() for h in self.hand_landmarks]
        if self.pose_landmarks:
            result["pose_landmarks"] = self.pose_landmarks.to_dict()
        if self.proportion_metrics:
            result["proportion_metrics"] = self.proportion_metrics.to_dict()
        if self.symmetry_metrics:
            result["symmetry_metrics"] = self.symmetry_metrics.to_dict()
        
        # Include array shapes but not data
        if self.silhouette is not None:
            result["silhouette_shape"] = self.silhouette.shape
        if self.edges is not None:
            result["edges_shape"] = self.edges.shape
        
        return result


@dataclass
class ComparisonResult:
    """
    Result of comparing two images or analysis results.
    
    Contains metrics and visualizations comparing canvas to reference.
    """
    # Comparison metrics
    pose_metrics: Optional[PoseMetrics] = None
    proportion_metrics: Optional[ProportionMetrics] = None
    symmetry_metrics: Optional[SymmetryMetrics] = None
    alignment_metrics: Optional[AlignmentMetrics] = None
    
    # Overall assessment
    overall_similarity: float = 0.0  # 0.0 = completely different, 1.0 = identical
    confidence: float = 0.0
    
    # Identified issues
    pose_errors: List[str] = field(default_factory=list)
    proportion_issues: List[str] = field(default_factory=list)
    areas_needing_refinement: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_all_issues(self) -> List[str]:
        """Get combined list of all issues."""
        return self.pose_errors + self.proportion_issues
    
    def get_priority_issues(self, max_count: int = 5) -> List[str]:
        """
        Get highest priority issues to address.
        
        Args:
            max_count: Maximum number of issues to return
            
        Returns:
            List of issue descriptions
        """
        all_issues = self.get_all_issues()
        return all_issues[:max_count]
    
    def has_significant_differences(self, threshold: float = 0.3) -> bool:
        """
        Check if there are significant differences requiring attention.
        
        Args:
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            True if differences exceed threshold
        """
        return self.overall_similarity < (1.0 - threshold)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "overall_similarity": self.overall_similarity,
            "confidence": self.confidence,
            "pose_errors": self.pose_errors,
            "proportion_issues": self.proportion_issues,
            "areas_needing_refinement": self.areas_needing_refinement,
            "processing_time_ms": self.processing_time_ms,
            "has_significant_differences": self.has_significant_differences(),
            "metadata": self.metadata,
        }
        
        if self.pose_metrics:
            result["pose_metrics"] = self.pose_metrics.to_dict()
        if self.proportion_metrics:
            result["proportion_metrics"] = self.proportion_metrics.to_dict()
        if self.symmetry_metrics:
            result["symmetry_metrics"] = self.symmetry_metrics.to_dict()
        if self.alignment_metrics:
            result["alignment_metrics"] = self.alignment_metrics.to_dict()
        
        return result
