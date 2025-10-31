"""
Landmark data structures for face, hands, and pose detection.

Contains dataclasses for representing detected landmarks from MediaPipe.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class Landmark:
    """
    Represents a single landmark point.
    
    Landmarks are key points detected on the body, face, or hands.
    Coordinates are normalized (0.0-1.0) relative to image dimensions.
    """
    x: float  # Normalized x coordinate (0.0-1.0)
    y: float  # Normalized y coordinate (0.0-1.0)
    z: float = 0.0  # Normalized z coordinate (depth)
    visibility: float = 1.0  # Confidence score (0.0-1.0)
    
    def to_pixel_coords(self, image_width: int, image_height: int) -> Tuple[int, int]:
        """
        Convert normalized coordinates to pixel coordinates.
        
        Args:
            image_width: Image width in pixels
            image_height: Image height in pixels
            
        Returns:
            Tuple of (x, y) pixel coordinates
        """
        return (int(self.x * image_width), int(self.y * image_height))
    
    def distance_to(self, other: 'Landmark') -> float:
        """
        Calculate Euclidean distance to another landmark.
        
        Args:
            other: Another landmark
            
        Returns:
            Distance value
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return float(np.sqrt(dx*dx + dy*dy + dz*dz))
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "visibility": self.visibility,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Landmark':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class FaceLandmarks:
    """
    Face landmarks detected by MediaPipe Face Mesh.
    
    Contains 468 3D face landmarks.
    """
    landmarks: List[Landmark] = field(default_factory=list)
    confidence: float = 0.0
    
    def get_contour(self) -> List[Landmark]:
        """Get face contour landmarks."""
        # Face mesh contour indices
        contour_indices = list(range(0, 17))
        return [self.landmarks[i] for i in contour_indices if i < len(self.landmarks)]
    
    def get_eyes(self) -> Tuple[List[Landmark], List[Landmark]]:
        """
        Get left and right eye landmarks.
        
        Returns:
            Tuple of (left_eye, right_eye) landmark lists
        """
        # Simplified eye indices for face mesh
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        left_eye = [self.landmarks[i] for i in left_eye_indices if i < len(self.landmarks)]
        right_eye = [self.landmarks[i] for i in right_eye_indices if i < len(self.landmarks)]
        return left_eye, right_eye
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "landmarks": [lm.to_dict() for lm in self.landmarks],
            "confidence": self.confidence,
        }


@dataclass
class HandLandmarks:
    """
    Hand landmarks detected by MediaPipe Hands.
    
    Contains 21 3D hand landmarks per hand.
    """
    landmarks: List[Landmark] = field(default_factory=list)
    handedness: str = "Unknown"  # "Left" or "Right"
    confidence: float = 0.0
    
    def get_wrist(self) -> Optional[Landmark]:
        """Get wrist landmark."""
        return self.landmarks[0] if self.landmarks else None
    
    def get_fingertips(self) -> List[Landmark]:
        """Get fingertip landmarks."""
        # Fingertip indices: thumb, index, middle, ring, pinky
        tip_indices = [4, 8, 12, 16, 20]
        return [self.landmarks[i] for i in tip_indices if i < len(self.landmarks)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "landmarks": [lm.to_dict() for lm in self.landmarks],
            "handedness": self.handedness,
            "confidence": self.confidence,
        }


@dataclass
class PoseLandmarks:
    """
    Pose landmarks detected by MediaPipe Pose.
    
    Contains 33 3D pose landmarks representing body keypoints.
    """
    landmarks: List[Landmark] = field(default_factory=list)
    confidence: float = 0.0
    
    # Landmark indices following MediaPipe Pose convention
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
    
    def get_landmark(self, index: int) -> Optional[Landmark]:
        """Get landmark by index."""
        return self.landmarks[index] if index < len(self.landmarks) else None
    
    def get_shoulders(self) -> Tuple[Optional[Landmark], Optional[Landmark]]:
        """Get left and right shoulder landmarks."""
        return self.get_landmark(self.LEFT_SHOULDER), self.get_landmark(self.RIGHT_SHOULDER)
    
    def get_hips(self) -> Tuple[Optional[Landmark], Optional[Landmark]]:
        """Get left and right hip landmarks."""
        return self.get_landmark(self.LEFT_HIP), self.get_landmark(self.RIGHT_HIP)
    
    def get_torso_center(self) -> Optional[Landmark]:
        """Calculate center point of torso."""
        left_shoulder = self.get_landmark(self.LEFT_SHOULDER)
        right_shoulder = self.get_landmark(self.RIGHT_SHOULDER)
        left_hip = self.get_landmark(self.LEFT_HIP)
        right_hip = self.get_landmark(self.RIGHT_HIP)
        
        if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
            return None
        
        # Calculate center of shoulders and hips
        center_x = (left_shoulder.x + right_shoulder.x + left_hip.x + right_hip.x) / 4
        center_y = (left_shoulder.y + right_shoulder.y + left_hip.y + right_hip.y) / 4
        center_z = (left_shoulder.z + right_shoulder.z + left_hip.z + right_hip.z) / 4
        
        return Landmark(x=center_x, y=center_y, z=center_z, visibility=1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "landmarks": [lm.to_dict() for lm in self.landmarks],
            "confidence": self.confidence,
        }
