"""
Pose data structures.

Contains dataclasses for representing complete pose information.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import numpy as np


@dataclass
class PoseKeypoint:
    """
    Represents a keypoint in a pose.
    
    Used for simplified pose representation and comparison.
    """
    name: str
    x: float
    y: float
    z: float = 0.0
    confidence: float = 1.0
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z])
    
    def distance_to(self, other: 'PoseKeypoint') -> float:
        """Calculate distance to another keypoint."""
        diff = self.to_array() - other.to_array()
        return float(np.linalg.norm(diff))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "confidence": self.confidence,
        }


@dataclass
class PoseData:
    """
    Complete pose information extracted from an image.
    
    This is the main data structure for pose analysis, containing
    all detected keypoints and metadata.
    """
    keypoints: List[PoseKeypoint] = field(default_factory=list)
    confidence: float = 0.0
    image_width: int = 0
    image_height: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_keypoint(self, name: str) -> Optional[PoseKeypoint]:
        """
        Get keypoint by name.
        
        Args:
            name: Keypoint name (e.g., "left_shoulder")
            
        Returns:
            The keypoint if found, None otherwise
        """
        for kp in self.keypoints:
            if kp.name == name:
                return kp
        return None
    
    def get_keypoint_names(self) -> List[str]:
        """Get list of all keypoint names."""
        return [kp.name for kp in self.keypoints]
    
    def get_skeleton_lines(self) -> List[Tuple[str, str]]:
        """
        Get pairs of keypoint names that form skeleton connections.
        
        Returns:
            List of (start_keypoint, end_keypoint) tuples
        """
        # Define standard skeleton connections
        return [
            # Head
            ("nose", "left_eye"),
            ("nose", "right_eye"),
            ("left_eye", "left_ear"),
            ("right_eye", "right_ear"),
            # Torso
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_hip"),
            ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            # Arms
            ("left_shoulder", "left_elbow"),
            ("left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow"),
            ("right_elbow", "right_wrist"),
            # Legs
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
        ]
    
    def calculate_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Calculate bounding box of all keypoints.
        
        Returns:
            (min_x, min_y, max_x, max_y) or None if no keypoints
        """
        if not self.keypoints:
            return None
        
        x_coords = [kp.x for kp in self.keypoints]
        y_coords = [kp.y for kp in self.keypoints]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def normalize(self) -> 'PoseData':
        """
        Normalize pose to 0-1 coordinate space.
        
        Returns:
            New normalized PoseData
        """
        bounds = self.calculate_bounds()
        if not bounds:
            return self
        
        min_x, min_y, max_x, max_y = bounds
        width = max_x - min_x
        height = max_y - min_y
        
        if width == 0 or height == 0:
            return self
        
        normalized_keypoints = []
        for kp in self.keypoints:
            norm_kp = PoseKeypoint(
                name=kp.name,
                x=(kp.x - min_x) / width,
                y=(kp.y - min_y) / height,
                z=kp.z,
                confidence=kp.confidence
            )
            normalized_keypoints.append(norm_kp)
        
        return PoseData(
            keypoints=normalized_keypoints,
            confidence=self.confidence,
            image_width=self.image_width,
            image_height=self.image_height,
            metadata={**self.metadata, "normalized": True}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "keypoints": [kp.to_dict() for kp in self.keypoints],
            "confidence": self.confidence,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PoseData':
        """Create from dictionary."""
        data = data.copy()
        data["keypoints"] = [
            PoseKeypoint(**kp) for kp in data.get("keypoints", [])
        ]
        return cls(**data)
