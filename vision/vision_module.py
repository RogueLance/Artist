"""
Main Vision Module API.

This is the primary interface for vision analysis, providing high-level methods
for analyzing canvas state, comparing to references, and detecting issues.
"""

from typing import Union, Optional, List, Dict, Any
from pathlib import Path
import time
import numpy as np
from PIL import Image

from vision.core.image_processor import ImageProcessor
from vision.core.pose_detector import PoseDetector
from vision.core.landmark_detector import LandmarkDetector
from vision.core.comparator import Comparator
from vision.models.analysis_result import AnalysisResult, ComparisonResult
from vision.models.pose_data import PoseData
from vision.models.comparison_metrics import PoseMetrics, ProportionMetrics, SymmetryMetrics


class VisionModule:
    """
    Main Vision Module for canvas analysis and comparison.
    
    This class provides the primary API for the Vision System, allowing
    analysis of canvas state, comparison to reference images, and detection
    of pose/anatomy issues.
    
    Example:
        >>> vision = VisionModule()
        >>> result = vision.analyze(canvas_image)
        >>> if result.has_pose():
        ...     print(f"Pose detected with {len(result.pose.keypoints)} keypoints")
        >>> comparison = vision.compare_to(canvas_image, reference_image)
        >>> errors = vision.detect_pose_errors(canvas_image, reference_image)
    """
    
    def __init__(
        self,
        enable_pose: bool = True,
        enable_face: bool = True,
        enable_hands: bool = True,
        min_detection_confidence: float = 0.5
    ):
        """
        Initialize Vision Module.
        
        Args:
            enable_pose: Enable pose detection
            enable_face: Enable face detection
            enable_hands: Enable hand detection
            min_detection_confidence: Minimum confidence threshold
        """
        self.enable_pose = enable_pose
        self.enable_face = enable_face
        self.enable_hands = enable_hands
        self.min_detection_confidence = min_detection_confidence
        
        # Initialize components
        self.image_processor = ImageProcessor()
        
        if enable_pose:
            self.pose_detector = PoseDetector(
                min_detection_confidence=min_detection_confidence
            )
        else:
            self.pose_detector = None
        
        if enable_face or enable_hands:
            self.landmark_detector = LandmarkDetector(
                enable_face=enable_face,
                enable_hands=enable_hands,
                min_detection_confidence=min_detection_confidence
            )
        else:
            self.landmark_detector = None
        
        self.comparator = Comparator()
    
    def analyze(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        extract_silhouette: bool = True,
        detect_edges: bool = True
    ) -> AnalysisResult:
        """
        Analyze an image and extract features.
        
        Args:
            image: Input image (path, PIL Image, or numpy array)
            extract_silhouette: Extract foreground silhouette
            detect_edges: Detect edges in image
            
        Returns:
            AnalysisResult containing detected features and metrics
        """
        start_time = time.time()
        
        # Load image
        img_bgr = self.image_processor.load_image(image)
        h, w = img_bgr.shape[:2]
        
        # Initialize result
        result = AnalysisResult(
            image_width=w,
            image_height=h
        )
        
        # Detect pose
        if self.enable_pose and self.pose_detector:
            pose_data = self.pose_detector.detect(img_bgr)
            if pose_data:
                result.pose = pose_data
                result.pose_landmarks = self.pose_detector.detect_landmarks(img_bgr)
                result.detection_confidence = max(result.detection_confidence, pose_data.confidence)
        
        # Detect face
        if self.enable_face and self.landmark_detector:
            face_landmarks = self.landmark_detector.detect_face(img_bgr)
            if face_landmarks:
                result.face_landmarks = face_landmarks
                result.detection_confidence = max(result.detection_confidence, face_landmarks.confidence)
        
        # Detect hands
        if self.enable_hands and self.landmark_detector:
            hand_landmarks = self.landmark_detector.detect_hands(img_bgr)
            if hand_landmarks:
                result.hand_landmarks = hand_landmarks
                # Update confidence with max hand confidence
                max_hand_conf = max(h.confidence for h in hand_landmarks)
                result.detection_confidence = max(result.detection_confidence, max_hand_conf)
        
        # Extract silhouette
        if extract_silhouette:
            result.silhouette = self.image_processor.extract_silhouette(img_bgr)
        
        # Detect edges
        if detect_edges:
            result.edges = self.image_processor.detect_edges(img_bgr)
        
        # Analyze proportions if pose detected
        if result.pose:
            result.proportion_metrics = self.comparator.analyze_proportions(result.pose)
        
        # Analyze symmetry if pose detected
        if result.pose:
            result.symmetry_metrics = self.comparator.analyze_symmetry(result.pose)
        
        # Record processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def compare_to(
        self,
        canvas_image: Union[str, Path, Image.Image, np.ndarray],
        reference_image: Union[str, Path, Image.Image, np.ndarray]
    ) -> ComparisonResult:
        """
        Compare canvas to reference image.
        
        Args:
            canvas_image: Current canvas state
            reference_image: Reference image to compare against
            
        Returns:
            ComparisonResult with comparison metrics and identified issues
        """
        start_time = time.time()
        
        # Analyze both images
        canvas_analysis = self.analyze(canvas_image)
        reference_analysis = self.analyze(reference_image)
        
        # Initialize result
        result = ComparisonResult()
        
        # Compare poses
        if canvas_analysis.pose and reference_analysis.pose:
            result.pose_metrics = self.comparator.compare_poses(
                canvas_analysis.pose,
                reference_analysis.pose
            )
            
            # Extract pose errors
            if result.pose_metrics.overall_difference > 0.3:
                largest_diffs = result.pose_metrics.get_largest_differences(5)
                for keypoint, diff in largest_diffs:
                    if diff > 0.2:
                        result.pose_errors.append(
                            f"{keypoint} position differs by {diff:.1%}"
                        )
        
        # Compare proportions
        if canvas_analysis.proportion_metrics and reference_analysis.proportion_metrics:
            result.proportion_metrics = canvas_analysis.proportion_metrics
            major_issues = result.proportion_metrics.get_major_issues()
            for ratio_name, deviation in major_issues:
                result.proportion_issues.append(
                    f"{ratio_name} off by {deviation:.1%}"
                )
        
        # Analyze symmetry
        if canvas_analysis.symmetry_metrics:
            result.symmetry_metrics = canvas_analysis.symmetry_metrics
        
        # Compare edges for alignment
        if canvas_analysis.edges is not None and reference_analysis.edges is not None:
            result.alignment_metrics = self.comparator.calculate_edge_alignment(
                canvas_analysis.edges,
                reference_analysis.edges
            )
            
            # Identify misaligned regions
            if result.alignment_metrics.misaligned_regions:
                for x, y, w, h in result.alignment_metrics.misaligned_regions[:5]:
                    result.areas_needing_refinement.append({
                        "type": "alignment",
                        "region": (x, y, w, h),
                        "severity": "medium"
                    })
        
        # Calculate overall similarity
        similarity_scores = []
        if result.pose_metrics:
            similarity_scores.append(1.0 - result.pose_metrics.overall_difference)
        if result.alignment_metrics:
            similarity_scores.append(result.alignment_metrics.alignment_score)
        
        if similarity_scores:
            result.overall_similarity = sum(similarity_scores) / len(similarity_scores)
        else:
            result.overall_similarity = 0.5  # Neutral if no metrics
        
        # Calculate confidence
        confidence_scores = []
        if canvas_analysis.detection_confidence > 0:
            confidence_scores.append(canvas_analysis.detection_confidence)
        if reference_analysis.detection_confidence > 0:
            confidence_scores.append(reference_analysis.detection_confidence)
        
        if confidence_scores:
            result.confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Record processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def detect_pose_errors(
        self,
        canvas_image: Union[str, Path, Image.Image, np.ndarray],
        reference_image: Optional[Union[str, Path, Image.Image, np.ndarray]] = None
    ) -> List[str]:
        """
        Detect pose and anatomy errors in canvas.
        
        Args:
            canvas_image: Canvas image to check
            reference_image: Optional reference image for comparison
            
        Returns:
            List of detected errors
        """
        errors = []
        
        # Analyze canvas
        canvas_analysis = self.analyze(canvas_image)
        
        if not canvas_analysis.has_pose():
            errors.append("No pose detected in canvas")
            return errors
        
        # Check proportions
        if canvas_analysis.proportion_metrics:
            if canvas_analysis.proportion_metrics.overall_score < 0.7:
                errors.extend(canvas_analysis.proportion_metrics.issues)
        
        # Check symmetry
        if canvas_analysis.symmetry_metrics:
            if canvas_analysis.symmetry_metrics.symmetry_score < 0.6:
                asymmetric = canvas_analysis.symmetry_metrics.get_asymmetric_pairs()
                for pair, diff in asymmetric[:3]:
                    errors.append(f"Asymmetry detected in {pair}: {diff:.1%}")
        
        # Compare to reference if provided
        if reference_image:
            comparison = self.compare_to(canvas_image, reference_image)
            errors.extend(comparison.pose_errors[:5])
        
        return errors
    
    def highlight_areas_needing_refinement(
        self,
        canvas_image: Union[str, Path, Image.Image, np.ndarray],
        reference_image: Union[str, Path, Image.Image, np.ndarray]
    ) -> List[Dict[str, Any]]:
        """
        Identify specific areas that need refinement.
        
        Args:
            canvas_image: Canvas image
            reference_image: Reference image
            
        Returns:
            List of areas with refinement recommendations
        """
        comparison = self.compare_to(canvas_image, reference_image)
        
        areas = []
        
        # Add areas from comparison result
        areas.extend(comparison.areas_needing_refinement)
        
        # Add areas based on pose differences
        if comparison.pose_metrics:
            largest_diffs = comparison.pose_metrics.get_largest_differences(3)
            
            # Analyze canvas to get keypoint locations
            canvas_analysis = self.analyze(canvas_image)
            if canvas_analysis.pose:
                for keypoint_name, diff in largest_diffs:
                    if diff > 0.2:
                        kp = canvas_analysis.pose.get_keypoint(keypoint_name)
                        if kp:
                            # Create region around keypoint
                            w, h = canvas_analysis.image_width, canvas_analysis.image_height
                            x = int(kp.x * w) - 50
                            y = int(kp.y * h) - 50
                            areas.append({
                                "type": "pose_error",
                                "keypoint": keypoint_name,
                                "region": (max(0, x), max(0, y), 100, 100),
                                "difference": diff,
                                "severity": "high" if diff > 0.4 else "medium"
                            })
        
        return areas
    
    def close(self):
        """Release resources."""
        if self.pose_detector:
            self.pose_detector.close()
        if self.landmark_detector:
            self.landmark_detector.close()
