"""
Visualization utilities.

Functions for drawing annotations, overlays, and debug visualizations.
"""

from typing import List, Tuple, Optional
import numpy as np
import cv2

from vision.models.pose_data import PoseData
from vision.models.landmarks import PoseLandmarks
from vision.models.comparison_metrics import AlignmentMetrics


class VisualizationUtils:
    """
    Utility functions for visualization and annotation.
    """
    
    @staticmethod
    def draw_text(
        image: np.ndarray,
        text: str,
        position: Tuple[int, int],
        font_scale: float = 0.6,
        color: Tuple[int, int, int] = (255, 255, 255),
        thickness: int = 2,
        background: Optional[Tuple[int, int, int]] = None
    ) -> np.ndarray:
        """
        Draw text on image with optional background.
        
        Args:
            image: Input image
            text: Text to draw
            position: Position (x, y)
            font_scale: Font scale
            color: Text color (BGR)
            thickness: Text thickness
            background: Background color (BGR), None for no background
            
        Returns:
            Image with text
        """
        output = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        x, y = position
        
        # Draw background if requested
        if background is not None:
            padding = 5
            cv2.rectangle(
                output,
                (x - padding, y - text_height - padding),
                (x + text_width + padding, y + baseline + padding),
                background,
                -1
            )
        
        # Draw text
        cv2.putText(
            output, text, (x, y),
            font, font_scale, color, thickness, cv2.LINE_AA
        )
        
        return output
    
    @staticmethod
    def draw_bounding_box(
        image: np.ndarray,
        box: Tuple[int, int, int, int],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
        label: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw bounding box on image.
        
        Args:
            image: Input image
            box: Bounding box (x, y, width, height)
            color: Box color (BGR)
            thickness: Line thickness
            label: Optional label text
            
        Returns:
            Image with bounding box
        """
        output = image.copy()
        x, y, w, h = box
        
        # Draw rectangle
        cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)
        
        # Draw label if provided
        if label:
            output = VisualizationUtils.draw_text(
                output, label, (x, y - 5), color=color, background=(0, 0, 0)
            )
        
        return output
    
    @staticmethod
    def draw_keypoints(
        image: np.ndarray,
        keypoints: List[Tuple[int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        radius: int = 4
    ) -> np.ndarray:
        """
        Draw keypoints on image.
        
        Args:
            image: Input image
            keypoints: List of keypoint positions [(x, y), ...]
            color: Point color (BGR)
            radius: Point radius
            
        Returns:
            Image with keypoints
        """
        output = image.copy()
        
        for x, y in keypoints:
            cv2.circle(output, (x, y), radius, color, -1)
            cv2.circle(output, (x, y), radius, (255, 255, 255), 1)
        
        return output
    
    @staticmethod
    def draw_skeleton(
        image: np.ndarray,
        pose_data: PoseData,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw pose skeleton on image.
        
        Args:
            image: Input image
            pose_data: Pose data
            color: Line color (BGR)
            thickness: Line thickness
            
        Returns:
            Image with skeleton
        """
        output = image.copy()
        h, w = image.shape[:2]
        
        # Draw connections
        for start_name, end_name in pose_data.get_skeleton_lines():
            start_kp = pose_data.get_keypoint(start_name)
            end_kp = pose_data.get_keypoint(end_name)
            
            if start_kp and end_kp and start_kp.confidence > 0.3 and end_kp.confidence > 0.3:
                start_pt = (int(start_kp.x * w), int(start_kp.y * h))
                end_pt = (int(end_kp.x * w), int(end_kp.y * h))
                cv2.line(output, start_pt, end_pt, color, thickness)
        
        # Draw keypoints
        keypoint_positions = []
        for kp in pose_data.keypoints:
            if kp.confidence > 0.3:
                keypoint_positions.append((int(kp.x * w), int(kp.y * h)))
        
        output = VisualizationUtils.draw_keypoints(output, keypoint_positions, color)
        
        return output
    
    @staticmethod
    def create_heatmap_overlay(
        image: np.ndarray,
        heatmap: np.ndarray,
        colormap: int = cv2.COLORMAP_JET,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Create heatmap overlay on image.
        
        Args:
            image: Base image
            heatmap: Heatmap array (0-1 range)
            colormap: OpenCV colormap
            alpha: Overlay transparency
            
        Returns:
            Image with heatmap overlay
        """
        # Ensure heatmap is right size
        if heatmap.shape[:2] != image.shape[:2]:
            heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
        
        # Convert to uint8
        heatmap_uint8 = (heatmap * 255).astype(np.uint8)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
        
        # Blend with image
        output = cv2.addWeighted(image, 1 - alpha, heatmap_colored, alpha, 0)
        
        return output
    
    @staticmethod
    def visualize_comparison(
        canvas_image: np.ndarray,
        reference_image: np.ndarray,
        canvas_pose: Optional[PoseData] = None,
        reference_pose: Optional[PoseData] = None
    ) -> np.ndarray:
        """
        Create side-by-side comparison visualization.
        
        Args:
            canvas_image: Canvas image
            reference_image: Reference image
            canvas_pose: Optional canvas pose data
            reference_pose: Optional reference pose data
            
        Returns:
            Combined visualization
        """
        # Ensure same height
        h1, w1 = canvas_image.shape[:2]
        h2, w2 = reference_image.shape[:2]
        
        if h1 != h2:
            # Resize to match heights
            target_height = max(h1, h2)
            if h1 < target_height:
                canvas_image = cv2.resize(canvas_image, (int(w1 * target_height / h1), target_height))
            if h2 < target_height:
                reference_image = cv2.resize(reference_image, (int(w2 * target_height / h2), target_height))
        
        # Draw poses if provided
        if canvas_pose:
            canvas_image = VisualizationUtils.draw_skeleton(
                canvas_image, canvas_pose, color=(0, 255, 0)
            )
        
        if reference_pose:
            reference_image = VisualizationUtils.draw_skeleton(
                reference_image, reference_pose, color=(255, 0, 0)
            )
        
        # Add labels
        canvas_image = VisualizationUtils.draw_text(
            canvas_image, "Canvas", (10, 30),
            color=(0, 255, 0), background=(0, 0, 0)
        )
        reference_image = VisualizationUtils.draw_text(
            reference_image, "Reference", (10, 30),
            color=(255, 0, 0), background=(0, 0, 0)
        )
        
        # Concatenate horizontally
        output = np.hstack([canvas_image, reference_image])
        
        return output
    
    @staticmethod
    def draw_difference_markers(
        image: np.ndarray,
        areas: List[Tuple[int, int, int, int]],
        color: Tuple[int, int, int] = (0, 0, 255),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw markers for areas needing refinement.
        
        Args:
            image: Input image
            areas: List of (x, y, w, h) bounding boxes
            color: Marker color (BGR)
            thickness: Line thickness
            
        Returns:
            Image with markers
        """
        output = image.copy()
        
        for idx, (x, y, w, h) in enumerate(areas):
            # Draw bounding box
            cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)
            
            # Draw number
            label = str(idx + 1)
            output = VisualizationUtils.draw_text(
                output, label, (x, y - 5),
                color=color, background=(0, 0, 0)
            )
        
        return output
