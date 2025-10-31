"""
Comparison metrics data structures.

Contains dataclasses for various comparison metrics between images/poses.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import numpy as np


@dataclass
class PoseMetrics:
    """
    Metrics comparing two poses.
    
    Measures differences in joint positions and angles.
    """
    overall_difference: float = 0.0  # 0.0 = identical, 1.0 = completely different
    keypoint_differences: Dict[str, float] = field(default_factory=dict)
    angle_differences: Dict[str, float] = field(default_factory=dict)
    missing_keypoints: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def get_largest_differences(self, n: int = 5) -> List[Tuple[str, float]]:
        """
        Get the N keypoints with largest differences.
        
        Args:
            n: Number of differences to return
            
        Returns:
            List of (keypoint_name, difference) tuples
        """
        sorted_diffs = sorted(
            self.keypoint_differences.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_diffs[:n]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_difference": self.overall_difference,
            "keypoint_differences": self.keypoint_differences,
            "angle_differences": self.angle_differences,
            "missing_keypoints": self.missing_keypoints,
            "confidence": self.confidence,
        }


@dataclass
class ProportionMetrics:
    """
    Metrics for anatomical proportions.
    
    Measures ratios and relationships between body parts.
    """
    body_ratios: Dict[str, float] = field(default_factory=dict)
    deviation_from_standard: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 1.0  # 1.0 = perfect proportions, 0.0 = poor
    issues: List[str] = field(default_factory=list)
    
    def get_major_issues(self, threshold: float = 0.2) -> List[Tuple[str, float]]:
        """
        Get proportion issues that exceed threshold.
        
        Args:
            threshold: Deviation threshold (0.0-1.0)
            
        Returns:
            List of (ratio_name, deviation) tuples
        """
        major_issues = []
        for name, deviation in self.deviation_from_standard.items():
            if abs(deviation) > threshold:
                major_issues.append((name, deviation))
        return major_issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "body_ratios": self.body_ratios,
            "deviation_from_standard": self.deviation_from_standard,
            "overall_score": self.overall_score,
            "issues": self.issues,
        }


@dataclass
class SymmetryMetrics:
    """
    Metrics for bilateral symmetry analysis.
    
    Measures left-right symmetry of poses and anatomy.
    """
    symmetry_score: float = 1.0  # 1.0 = perfectly symmetric, 0.0 = asymmetric
    left_right_differences: Dict[str, float] = field(default_factory=dict)
    asymmetric_features: List[str] = field(default_factory=list)
    symmetry_axis: Optional[Tuple[float, float, float, float]] = None  # (x1, y1, x2, y2)
    
    def get_asymmetric_pairs(self, threshold: float = 0.15) -> List[Tuple[str, float]]:
        """
        Get left-right pairs with significant asymmetry.
        
        Args:
            threshold: Asymmetry threshold (0.0-1.0)
            
        Returns:
            List of (pair_name, difference) tuples
        """
        asymmetric = []
        for name, diff in self.left_right_differences.items():
            if abs(diff) > threshold:
                asymmetric.append((name, diff))
        return asymmetric
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symmetry_score": self.symmetry_score,
            "left_right_differences": self.left_right_differences,
            "asymmetric_features": self.asymmetric_features,
            "symmetry_axis": self.symmetry_axis,
        }


@dataclass
class AlignmentMetrics:
    """
    Metrics for edge and feature alignment.
    
    Measures how well edges and features align between two images.
    """
    alignment_score: float = 0.0  # 0.0 = no alignment, 1.0 = perfect alignment
    edge_overlap: float = 0.0  # Percentage of overlapping edges
    heatmap: Optional[np.ndarray] = None  # Alignment heatmap
    misaligned_regions: List[Tuple[int, int, int, int]] = field(default_factory=list)  # (x, y, w, h)
    
    def get_worst_regions(self, n: int = 3) -> List[Tuple[int, int, int, int]]:
        """
        Get the N regions with worst alignment.
        
        Args:
            n: Number of regions to return
            
        Returns:
            List of (x, y, w, h) bounding boxes
        """
        return self.misaligned_regions[:n]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "alignment_score": self.alignment_score,
            "edge_overlap": self.edge_overlap,
            "misaligned_regions": self.misaligned_regions,
        }
        if self.heatmap is not None:
            result["heatmap_shape"] = self.heatmap.shape
        return result
