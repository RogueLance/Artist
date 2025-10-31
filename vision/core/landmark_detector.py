"""
Landmark detection for faces and hands using MediaPipe.

Handles detection of facial landmarks and hand landmarks.
"""

from typing import List, Optional
import numpy as np
import cv2
import mediapipe as mp

from vision.models.landmarks import FaceLandmarks, HandLandmarks, Landmark
from vision.core.image_processor import ImageProcessor


class LandmarkDetector:
    """
    Detects facial and hand landmarks using MediaPipe.
    
    Provides detection of fine-grained features for detailed analysis.
    """
    
    def __init__(
        self,
        enable_face: bool = True,
        enable_hands: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize landmark detector.
        
        Args:
            enable_face: Enable face landmark detection
            enable_hands: Enable hand landmark detection
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.enable_face = enable_face
        self.enable_hands = enable_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe components
        if enable_face:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
        
        if enable_hands:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
    
    def detect_face(self, image: np.ndarray) -> Optional[FaceLandmarks]:
        """
        Detect facial landmarks.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            FaceLandmarks if face detected, None otherwise
        """
        if not self.enable_face:
            return None
        
        # Convert to RGB
        rgb_image = ImageProcessor.to_rgb(image)
        
        # Process image
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return None
        
        # Get first face
        face_landmarks_raw = results.multi_face_landmarks[0]
        
        # Convert to our Landmark format
        landmarks = []
        for landmark in face_landmarks_raw.landmark:
            lm = Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=1.0  # Face mesh doesn't provide visibility
            )
            landmarks.append(lm)
        
        face_landmarks = FaceLandmarks(
            landmarks=landmarks,
            confidence=1.0  # Face mesh doesn't provide overall confidence
        )
        
        return face_landmarks
    
    def detect_hands(self, image: np.ndarray) -> List[HandLandmarks]:
        """
        Detect hand landmarks.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of HandLandmarks (one per detected hand)
        """
        if not self.enable_hands:
            return []
        
        # Convert to RGB
        rgb_image = ImageProcessor.to_rgb(image)
        
        # Process image
        results = self.hands.process(rgb_image)
        
        if not results.multi_hand_landmarks:
            return []
        
        # Process each detected hand
        hand_landmarks_list = []
        
        for idx, hand_landmarks_raw in enumerate(results.multi_hand_landmarks):
            # Get handedness
            handedness = "Unknown"
            if results.multi_handedness and idx < len(results.multi_handedness):
                handedness_info = results.multi_handedness[idx]
                handedness = handedness_info.classification[0].label
            
            # Convert landmarks
            landmarks = []
            for landmark in hand_landmarks_raw.landmark:
                lm = Landmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                    visibility=1.0  # Hand landmarks don't provide visibility
                )
                landmarks.append(lm)
            
            # Get confidence
            confidence = 1.0
            if results.multi_handedness and idx < len(results.multi_handedness):
                confidence = results.multi_handedness[idx].classification[0].score
            
            hand_landmarks = HandLandmarks(
                landmarks=landmarks,
                handedness=handedness,
                confidence=confidence
            )
            hand_landmarks_list.append(hand_landmarks)
        
        return hand_landmarks_list
    
    def visualize_face(
        self,
        image: np.ndarray,
        face_landmarks: FaceLandmarks,
        color: tuple = (0, 255, 0)
    ) -> np.ndarray:
        """
        Draw face landmarks on image.
        
        Args:
            image: Input image
            face_landmarks: Detected face landmarks
            color: Point color (BGR)
            
        Returns:
            Image with face landmarks drawn
        """
        output = image.copy()
        h, w = image.shape[:2]
        
        # Draw landmarks
        for landmark in face_landmarks.landmarks:
            pt = landmark.to_pixel_coords(w, h)
            cv2.circle(output, pt, 1, color, -1)
        
        # Draw contour
        contour = face_landmarks.get_contour()
        if len(contour) > 1:
            points = [lm.to_pixel_coords(w, h) for lm in contour]
            for i in range(len(points) - 1):
                cv2.line(output, points[i], points[i + 1], color, 1)
        
        return output
    
    def visualize_hands(
        self,
        image: np.ndarray,
        hand_landmarks_list: List[HandLandmarks],
        color: tuple = (0, 255, 0)
    ) -> np.ndarray:
        """
        Draw hand landmarks on image.
        
        Args:
            image: Input image
            hand_landmarks_list: List of detected hand landmarks
            color: Point color (BGR)
            
        Returns:
            Image with hand landmarks drawn
        """
        output = image.copy()
        h, w = image.shape[:2]
        
        # MediaPipe hand connections
        hand_connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        for hand_landmarks in hand_landmarks_list:
            # Draw connections
            for start_idx, end_idx in hand_connections:
                if start_idx < len(hand_landmarks.landmarks) and end_idx < len(hand_landmarks.landmarks):
                    start_pt = hand_landmarks.landmarks[start_idx].to_pixel_coords(w, h)
                    end_pt = hand_landmarks.landmarks[end_idx].to_pixel_coords(w, h)
                    cv2.line(output, start_pt, end_pt, color, 2)
            
            # Draw landmarks
            for landmark in hand_landmarks.landmarks:
                pt = landmark.to_pixel_coords(w, h)
                cv2.circle(output, pt, 3, color, -1)
                cv2.circle(output, pt, 3, (255, 255, 255), 1)
        
        return output
    
    def close(self):
        """Release resources."""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'hands'):
            self.hands.close()
