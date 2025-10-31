"""
Comparison engine for analyzing differences between images.

Provides metrics for pose differences, proportions, symmetry, and alignment.
"""

from typing import Optional, Tuple, List, Dict, Any
import numpy as np
import cv2

from vision.models.pose_data import PoseData
from vision.models.analysis_result import AnalysisResult, ComparisonResult
from vision.models.comparison_metrics import (
    PoseMetrics,
    ProportionMetrics,
    SymmetryMetrics,
    AlignmentMetrics,
)


class Comparator:
    """
    Compares images and poses to identify differences and issues.
    
    This class provides the core comparison functionality for evaluating
    canvas state against reference images.
    """
    
    def __init__(self):
        """Initialize comparator."""
        pass
    
    def compare_poses(
        self,
        pose1: PoseData,
        pose2: PoseData,
        normalize: bool = True
    ) -> PoseMetrics:
        """
        Compare two poses and calculate differences.
        
        Args:
            pose1: First pose (e.g., canvas)
            pose2: Second pose (e.g., reference)
            normalize: Normalize poses before comparison
            
        Returns:
            PoseMetrics with comparison results
        """
        # Normalize if requested
        if normalize:
            pose1 = pose1.normalize()
            pose2 = pose2.normalize()
        
        # Calculate keypoint differences
        keypoint_differences = {}
        missing_keypoints = []
        
        for kp1 in pose1.keypoints:
            kp2 = pose2.get_keypoint(kp1.name)
            if kp2:
                distance = kp1.distance_to(kp2)
                keypoint_differences[kp1.name] = distance
            else:
                missing_keypoints.append(kp1.name)
        
        # Check for keypoints in pose2 not in pose1
        for kp2 in pose2.keypoints:
            if pose1.get_keypoint(kp2.name) is None:
                missing_keypoints.append(kp2.name)
        
        # Calculate overall difference (average of all keypoint differences)
        if keypoint_differences:
            overall_difference = sum(keypoint_differences.values()) / len(keypoint_differences)
        else:
            overall_difference = 1.0
        
        # Calculate angle differences
        angle_differences = self._calculate_angle_differences(pose1, pose2)
        
        # Calculate confidence based on missing keypoints
        total_keypoints = len(pose1.keypoints) + len(pose2.keypoints)
        confidence = 1.0 - (len(missing_keypoints) / max(total_keypoints, 1))
        
        return PoseMetrics(
            overall_difference=min(overall_difference, 1.0),
            keypoint_differences=keypoint_differences,
            angle_differences=angle_differences,
            missing_keypoints=missing_keypoints,
            confidence=confidence
        )
    
    def _calculate_angle_differences(
        self,
        pose1: PoseData,
        pose2: PoseData
    ) -> Dict[str, float]:
        """Calculate differences in joint angles."""
        angle_differences = {}
        
        # Define angle triplets (point1, joint, point2)
        angle_triplets = [
            ("left_shoulder", "left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow", "right_wrist"),
            ("left_hip", "left_knee", "left_ankle"),
            ("right_hip", "right_knee", "right_ankle"),
        ]
        
        for p1_name, joint_name, p2_name in angle_triplets:
            angle1 = self._calculate_angle(pose1, p1_name, joint_name, p2_name)
            angle2 = self._calculate_angle(pose2, p1_name, joint_name, p2_name)
            
            if angle1 is not None and angle2 is not None:
                diff = abs(angle1 - angle2)
                # Normalize to 0-1 range (180 degrees = 1.0)
                angle_differences[joint_name] = min(diff / 180.0, 1.0)
        
        return angle_differences
    
    def _calculate_angle(
        self,
        pose: PoseData,
        point1_name: str,
        joint_name: str,
        point2_name: str
    ) -> Optional[float]:
        """Calculate angle at a joint."""
        p1 = pose.get_keypoint(point1_name)
        joint = pose.get_keypoint(joint_name)
        p2 = pose.get_keypoint(point2_name)
        
        if not all([p1, joint, p2]):
            return None
        
        # Convert to arrays
        v1 = np.array([p1.x - joint.x, p1.y - joint.y])
        v2 = np.array([p2.x - joint.x, p2.y - joint.y])
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def analyze_proportions(
        self,
        pose: PoseData,
        standard_ratios: Optional[Dict[str, float]] = None
    ) -> ProportionMetrics:
        """
        Analyze anatomical proportions of a pose.
        
        Args:
            pose: Pose to analyze
            standard_ratios: Standard proportion ratios (None for defaults)
            
        Returns:
            ProportionMetrics with analysis results
        """
        # Default standard human proportions
        if standard_ratios is None:
            standard_ratios = {
                "head_to_body": 1 / 7.5,  # Head is ~1/7.5 of total height
                "torso_to_legs": 1.0,  # Torso and legs roughly equal
                "upper_arm_to_forearm": 1.0,  # Equal length
                "thigh_to_shin": 1.0,  # Equal length
            }
        
        # Calculate actual ratios
        body_ratios = {}
        deviation_from_standard = {}
        issues = []
        
        # Calculate body segment lengths
        segments = self._calculate_body_segments(pose)
        
        if "head_height" in segments and "total_height" in segments:
            if segments["total_height"] > 0:
                ratio = segments["head_height"] / segments["total_height"]
                body_ratios["head_to_body"] = ratio
                if "head_to_body" in standard_ratios:
                    deviation = ratio - standard_ratios["head_to_body"]
                    deviation_from_standard["head_to_body"] = deviation
                    if abs(deviation) > 0.05:
                        issues.append(f"Head proportion off by {deviation:.2%}")
        
        # Calculate overall score (1.0 - average deviation)
        if deviation_from_standard:
            avg_deviation = sum(abs(d) for d in deviation_from_standard.values()) / len(deviation_from_standard)
            overall_score = max(0.0, 1.0 - avg_deviation * 5)
        else:
            overall_score = 0.5  # Neutral if no data
        
        return ProportionMetrics(
            body_ratios=body_ratios,
            deviation_from_standard=deviation_from_standard,
            overall_score=overall_score,
            issues=issues
        )
    
    def _calculate_body_segments(self, pose: PoseData) -> Dict[str, float]:
        """Calculate lengths of body segments."""
        segments = {}
        
        # Helper to calculate distance
        def dist(kp1_name: str, kp2_name: str) -> Optional[float]:
            kp1 = pose.get_keypoint(kp1_name)
            kp2 = pose.get_keypoint(kp2_name)
            if kp1 and kp2:
                return kp1.distance_to(kp2)
            return None
        
        # Head height (nose to center of shoulders)
        left_shoulder = pose.get_keypoint("left_shoulder")
        right_shoulder = pose.get_keypoint("right_shoulder")
        nose = pose.get_keypoint("nose")
        if left_shoulder and right_shoulder and nose:
            # Calculate shoulder center
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            shoulder_center_z = (left_shoulder.z + right_shoulder.z) / 2
            # Calculate distance from nose to shoulder center
            dx = nose.x - shoulder_center_x
            dy = nose.y - shoulder_center_y
            dz = nose.z - shoulder_center_z
            segments["head_height"] = float(np.sqrt(dx*dx + dy*dy + dz*dz))
        
        # Total height (nose to ankle)
        left_ankle_dist = dist("nose", "left_ankle")
        right_ankle_dist = dist("nose", "right_ankle")
        if left_ankle_dist or right_ankle_dist:
            segments["total_height"] = max(left_ankle_dist or 0, right_ankle_dist or 0)
        
        # Torso (shoulder to hip)
        torso_dist = dist("left_shoulder", "left_hip")
        if torso_dist:
            segments["torso_length"] = torso_dist
        
        # Legs (hip to ankle)
        leg_dist = dist("left_hip", "left_ankle")
        if leg_dist:
            segments["leg_length"] = leg_dist
        
        return segments
    
    def analyze_symmetry(self, pose: PoseData) -> SymmetryMetrics:
        """
        Analyze bilateral symmetry of a pose.
        
        Args:
            pose: Pose to analyze
            
        Returns:
            SymmetryMetrics with symmetry analysis
        """
        left_right_differences = {}
        asymmetric_features = []
        
        # Define left-right pairs
        pairs = [
            ("left_shoulder", "right_shoulder"),
            ("left_elbow", "right_elbow"),
            ("left_wrist", "right_wrist"),
            ("left_hip", "right_hip"),
            ("left_knee", "right_knee"),
            ("left_ankle", "right_ankle"),
        ]
        
        # Calculate symmetry axis (vertical line through center)
        bounds = pose.calculate_bounds()
        if bounds:
            min_x, min_y, max_x, max_y = bounds
            center_x = (min_x + max_x) / 2
            symmetry_axis = (center_x, min_y, center_x, max_y)
        else:
            symmetry_axis = None
        
        # Compare left-right pairs
        for left_name, right_name in pairs:
            left_kp = pose.get_keypoint(left_name)
            right_kp = pose.get_keypoint(right_name)
            
            if left_kp and right_kp and symmetry_axis:
                # Calculate distance from symmetry axis for each
                center_x = symmetry_axis[0]
                left_dist = abs(left_kp.x - center_x)
                right_dist = abs(right_kp.x - center_x)
                
                # Calculate difference
                diff = abs(left_dist - right_dist)
                left_right_differences[f"{left_name}_{right_name}"] = diff
                
                if diff > 0.15:
                    asymmetric_features.append(f"{left_name}/{right_name}")
        
        # Calculate overall symmetry score
        if left_right_differences:
            avg_diff = sum(left_right_differences.values()) / len(left_right_differences)
            symmetry_score = max(0.0, 1.0 - avg_diff * 3)
        else:
            symmetry_score = 0.5
        
        return SymmetryMetrics(
            symmetry_score=symmetry_score,
            left_right_differences=left_right_differences,
            asymmetric_features=asymmetric_features,
            symmetry_axis=symmetry_axis
        )
    
    def calculate_edge_alignment(
        self,
        edges1: np.ndarray,
        edges2: np.ndarray
    ) -> AlignmentMetrics:
        """
        Calculate alignment between edge maps.
        
        Args:
            edges1: First edge map (canvas)
            edges2: Second edge map (reference)
            
        Returns:
            AlignmentMetrics with alignment analysis
        """
        # Ensure same size
        if edges1.shape != edges2.shape:
            edges2 = cv2.resize(edges2, (edges1.shape[1], edges1.shape[0]))
        
        # Calculate overlap
        overlap = np.logical_and(edges1 > 0, edges2 > 0)
        edge1_pixels = np.sum(edges1 > 0)
        edge2_pixels = np.sum(edges2 > 0)
        overlap_pixels = np.sum(overlap)
        
        # Calculate edge overlap percentage
        if edge1_pixels > 0 or edge2_pixels > 0:
            edge_overlap = overlap_pixels / max(edge1_pixels, edge2_pixels)
        else:
            edge_overlap = 0.0
        
        # Create alignment heatmap (XOR shows misalignment)
        heatmap = np.logical_xor(edges1 > 0, edges2 > 0).astype(np.float32)
        
        # Calculate alignment score (1.0 - misalignment)
        alignment_score = 1.0 - (np.sum(heatmap) / heatmap.size)
        
        # Find misaligned regions (simplified - uses contours)
        misaligned_regions = self._find_misaligned_regions(heatmap)
        
        return AlignmentMetrics(
            alignment_score=alignment_score,
            edge_overlap=edge_overlap,
            heatmap=heatmap,
            misaligned_regions=misaligned_regions
        )
    
    def _find_misaligned_regions(
        self,
        heatmap: np.ndarray,
        min_area: int = 100
    ) -> List[Tuple[int, int, int, int]]:
        """Find regions with significant misalignment."""
        # Convert to uint8 for contour detection
        heatmap_uint8 = (heatmap * 255).astype(np.uint8)
        
        # Find contours
        contours, _ = cv2.findContours(
            heatmap_uint8,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Extract bounding boxes for large misaligned regions
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area:
                x, y, w, h = cv2.boundingRect(contour)
                regions.append((x, y, w, h))
        
        # Sort by area (largest first)
        regions.sort(key=lambda r: r[2] * r[3], reverse=True)
        
        return regions
