"""
Pose detection using MediaPipe.

Handles pose estimation and landmark detection for body poses.
"""

from typing import Optional
import numpy as np
import cv2
import mediapipe as mp

from vision.models.pose_data import PoseData, PoseKeypoint
from vision.models.landmarks import PoseLandmarks, Landmark
from vision.core.image_processor import ImageProcessor


class PoseDetector:
    """
    Detects human poses in images using MediaPipe Pose.
    
    This detector identifies body landmarks and provides structured pose data
    that can be used for comparison and analysis.
    """
    
    # MediaPipe landmark name mapping
    LANDMARK_NAMES = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer",
        "right_eye_inner", "right_eye", "right_eye_outer",
        "left_ear", "right_ear", "mouth_left", "mouth_right",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky",
        "left_index", "right_index", "left_thumb", "right_thumb",
        "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel",
        "left_foot_index", "right_foot_index"
    ]
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1
    ):
        """
        Initialize pose detector.
        
        Args:
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
            model_complexity: Model complexity (0, 1, or 2)
        """
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_complexity = model_complexity
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
    
    def detect(self, image: np.ndarray) -> Optional[PoseData]:
        """
        Detect pose in image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            PoseData if pose detected, None otherwise
        """
        # Convert to RGB for MediaPipe
        rgb_image = ImageProcessor.to_rgb(image)
        
        # Process image
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        h, w = image.shape[:2]
        keypoints = []
        
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            if idx < len(self.LANDMARK_NAMES):
                keypoint = PoseKeypoint(
                    name=self.LANDMARK_NAMES[idx],
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                    confidence=landmark.visibility
                )
                keypoints.append(keypoint)
        
        # Create PoseData
        pose_data = PoseData(
            keypoints=keypoints,
            confidence=self._calculate_overall_confidence(keypoints),
            image_width=w,
            image_height=h
        )
        
        return pose_data
    
    def detect_landmarks(self, image: np.ndarray) -> Optional[PoseLandmarks]:
        """
        Detect pose landmarks in image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            PoseLandmarks if pose detected, None otherwise
        """
        # Convert to RGB for MediaPipe
        rgb_image = ImageProcessor.to_rgb(image)
        
        # Process image
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            lm = Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility
            )
            landmarks.append(lm)
        
        pose_landmarks = PoseLandmarks(
            landmarks=landmarks,
            confidence=self._calculate_overall_confidence_from_landmarks(landmarks)
        )
        
        return pose_landmarks
    
    def _calculate_overall_confidence(self, keypoints: list) -> float:
        """Calculate overall confidence from keypoints."""
        if not keypoints:
            return 0.0
        
        confidences = [kp.confidence for kp in keypoints]
        return sum(confidences) / len(confidences)
    
    def _calculate_overall_confidence_from_landmarks(self, landmarks: list) -> float:
        """Calculate overall confidence from landmarks."""
        if not landmarks:
            return 0.0
        
        visibilities = [lm.visibility for lm in landmarks]
        return sum(visibilities) / len(visibilities)
    
    def visualize_pose(
        self,
        image: np.ndarray,
        pose_data: PoseData,
        color: tuple = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw pose skeleton on image.
        
        Args:
            image: Input image
            pose_data: Detected pose data
            color: Line color (BGR)
            thickness: Line thickness
            
        Returns:
            Image with pose drawn
        """
        output = image.copy()
        h, w = image.shape[:2]
        
        # Draw skeleton connections
        for start_name, end_name in pose_data.get_skeleton_lines():
            start_kp = pose_data.get_keypoint(start_name)
            end_kp = pose_data.get_keypoint(end_name)
            
            if start_kp and end_kp:
                start_pt = (int(start_kp.x * w), int(start_kp.y * h))
                end_pt = (int(end_kp.x * w), int(end_kp.y * h))
                cv2.line(output, start_pt, end_pt, color, thickness)
        
        # Draw keypoints
        for kp in pose_data.keypoints:
            if kp.confidence > 0.5:
                pt = (int(kp.x * w), int(kp.y * h))
                cv2.circle(output, pt, 4, color, -1)
                cv2.circle(output, pt, 4, (255, 255, 255), 1)
        
        return output
    
    def close(self):
        """Release resources."""
        if hasattr(self, 'pose'):
            self.pose.close()
