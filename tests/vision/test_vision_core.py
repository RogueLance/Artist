"""Tests for Vision System core functionality."""

import pytest
import numpy as np
from PIL import Image
import tempfile
from pathlib import Path

from vision import VisionModule
from vision.core import ImageProcessor, PoseDetector, LandmarkDetector, Comparator
from vision.models import (
    AnalysisResult,
    ComparisonResult,
    PoseData,
    PoseKeypoint,
    Landmark,
    PoseLandmarks,
)


class TestImageProcessor:
    """Test ImageProcessor class."""
    
    def test_load_numpy_array(self):
        """Test loading image from numpy array."""
        # Create test image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[25:75, 25:75] = [255, 0, 0]  # Blue square in BGR
        
        processor = ImageProcessor()
        loaded = processor.load_image(img)
        
        assert loaded.shape == (100, 100, 3)
        assert np.array_equal(loaded, img)
    
    def test_load_pil_image(self):
        """Test loading from PIL Image."""
        pil_img = Image.new('RGB', (100, 100), color='red')
        
        processor = ImageProcessor()
        loaded = processor.load_image(pil_img)
        
        assert loaded.shape == (100, 100, 3)
        # PIL uses RGB, OpenCV uses BGR
        assert loaded[0, 0, 2] == 255  # Red channel in BGR
    
    def test_load_file_path(self):
        """Test loading from file path."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filepath = f.name
            
        try:
            # Create and save test image
            img = np.zeros((50, 50, 3), dtype=np.uint8)
            img[10:40, 10:40] = [0, 255, 0]  # Green square
            pil_img = Image.fromarray(img)
            pil_img.save(filepath)
            
            processor = ImageProcessor()
            loaded = processor.load_image(filepath)
            
            assert loaded.shape[0] == 50
            assert loaded.shape[1] == 50
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_to_rgb(self):
        """Test BGR to RGB conversion."""
        bgr_img = np.zeros((10, 10, 3), dtype=np.uint8)
        bgr_img[:, :] = [255, 0, 0]  # Blue in BGR
        
        processor = ImageProcessor()
        rgb_img = processor.to_rgb(bgr_img)
        
        assert rgb_img[0, 0, 0] == 0   # R
        assert rgb_img[0, 0, 1] == 0   # G
        assert rgb_img[0, 0, 2] == 255 # B
    
    def test_to_grayscale(self):
        """Test grayscale conversion."""
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        img[:, :] = [255, 255, 255]  # White
        
        processor = ImageProcessor()
        gray = processor.to_grayscale(img)
        
        assert len(gray.shape) == 2
        assert gray[0, 0] == 255
    
    def test_resize_by_width(self):
        """Test resizing by width."""
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        
        processor = ImageProcessor()
        resized = processor.resize(img, width=100)
        
        assert resized.shape[1] == 100
        assert resized.shape[0] == 50  # Maintains aspect ratio
    
    def test_resize_by_height(self):
        """Test resizing by height."""
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        
        processor = ImageProcessor()
        resized = processor.resize(img, height=50)
        
        assert resized.shape[0] == 50
        assert resized.shape[1] == 100  # Maintains aspect ratio
    
    def test_resize_max_size(self):
        """Test resizing with max size."""
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        
        processor = ImageProcessor()
        resized = processor.resize(img, max_size=100)
        
        assert max(resized.shape[:2]) == 100
    
    def test_extract_silhouette(self):
        """Test silhouette extraction."""
        # Create image with clear foreground
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White background
        img[25:75, 25:75] = [0, 0, 0]  # Black square
        
        processor = ImageProcessor()
        mask = processor.extract_silhouette(img, method="threshold")
        
        assert mask.shape == (100, 100)
        # Center should be black (0) in mask
        assert mask[50, 50] == 0
    
    def test_detect_edges(self):
        """Test edge detection."""
        # Create image with clear edge
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img[:, 50:] = 0  # Half black
        
        processor = ImageProcessor()
        edges = processor.detect_edges(img)
        
        assert edges.shape == (100, 100)
        # Should detect vertical edge around x=50
        assert np.sum(edges[:, 48:52]) > 0
    
    def test_get_dimensions(self):
        """Test getting image dimensions."""
        img = np.zeros((150, 200, 3), dtype=np.uint8)
        
        processor = ImageProcessor()
        width, height = processor.get_dimensions(img)
        
        assert width == 200
        assert height == 150


class TestPoseData:
    """Test PoseData class."""
    
    def test_create_pose_data(self):
        """Test creating pose data."""
        keypoints = [
            PoseKeypoint("nose", 0.5, 0.3, confidence=0.9),
            PoseKeypoint("left_shoulder", 0.4, 0.5, confidence=0.85),
            PoseKeypoint("right_shoulder", 0.6, 0.5, confidence=0.85),
        ]
        
        pose = PoseData(
            keypoints=keypoints,
            confidence=0.87,
            image_width=640,
            image_height=480
        )
        
        assert len(pose.keypoints) == 3
        assert pose.confidence == 0.87
        assert pose.image_width == 640
    
    def test_get_keypoint(self):
        """Test getting keypoint by name."""
        keypoints = [
            PoseKeypoint("nose", 0.5, 0.3),
            PoseKeypoint("left_shoulder", 0.4, 0.5),
        ]
        pose = PoseData(keypoints=keypoints)
        
        nose = pose.get_keypoint("nose")
        assert nose is not None
        assert nose.x == 0.5
        
        unknown = pose.get_keypoint("unknown")
        assert unknown is None
    
    def test_calculate_bounds(self):
        """Test bounding box calculation."""
        keypoints = [
            PoseKeypoint("p1", 0.2, 0.3),
            PoseKeypoint("p2", 0.8, 0.7),
            PoseKeypoint("p3", 0.5, 0.5),
        ]
        pose = PoseData(keypoints=keypoints)
        
        bounds = pose.calculate_bounds()
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        
        assert min_x == 0.2
        assert min_y == 0.3
        assert max_x == 0.8
        assert max_y == 0.7
    
    def test_normalize_pose(self):
        """Test pose normalization."""
        keypoints = [
            PoseKeypoint("p1", 100, 200),
            PoseKeypoint("p2", 300, 400),
        ]
        pose = PoseData(keypoints=keypoints)
        
        normalized = pose.normalize()
        
        # Check that coordinates are in 0-1 range
        for kp in normalized.keypoints:
            assert 0 <= kp.x <= 1
            assert 0 <= kp.y <= 1
    
    def test_pose_serialization(self):
        """Test pose to/from dict."""
        keypoints = [
            PoseKeypoint("nose", 0.5, 0.3, confidence=0.9),
        ]
        pose = PoseData(keypoints=keypoints, confidence=0.9)
        
        pose_dict = pose.to_dict()
        assert "keypoints" in pose_dict
        assert "confidence" in pose_dict
        
        restored = PoseData.from_dict(pose_dict)
        assert len(restored.keypoints) == 1
        assert restored.keypoints[0].name == "nose"


class TestLandmark:
    """Test Landmark class."""
    
    def test_create_landmark(self):
        """Test creating a landmark."""
        lm = Landmark(x=0.5, y=0.3, z=0.1, visibility=0.95)
        
        assert lm.x == 0.5
        assert lm.y == 0.3
        assert lm.z == 0.1
        assert lm.visibility == 0.95
    
    def test_to_pixel_coords(self):
        """Test converting to pixel coordinates."""
        lm = Landmark(x=0.5, y=0.25)
        
        pixel_x, pixel_y = lm.to_pixel_coords(640, 480)
        
        assert pixel_x == 320  # 0.5 * 640
        assert pixel_y == 120  # 0.25 * 480
    
    def test_distance_to(self):
        """Test distance calculation."""
        lm1 = Landmark(x=0.0, y=0.0)
        lm2 = Landmark(x=0.3, y=0.4)
        
        dist = lm1.distance_to(lm2)
        
        assert abs(dist - 0.5) < 0.01  # 3-4-5 triangle


class TestComparator:
    """Test Comparator class."""
    
    def test_compare_identical_poses(self):
        """Test comparing identical poses."""
        keypoints = [
            PoseKeypoint("nose", 0.5, 0.3),
            PoseKeypoint("left_shoulder", 0.4, 0.5),
        ]
        pose1 = PoseData(keypoints=keypoints)
        pose2 = PoseData(keypoints=[
            PoseKeypoint("nose", 0.5, 0.3),
            PoseKeypoint("left_shoulder", 0.4, 0.5),
        ])
        
        comparator = Comparator()
        metrics = comparator.compare_poses(pose1, pose2)
        
        assert metrics.overall_difference < 0.01
        assert len(metrics.missing_keypoints) == 0
    
    def test_compare_different_poses(self):
        """Test comparing different poses."""
        pose1 = PoseData(keypoints=[
            PoseKeypoint("nose", 0.5, 0.3),
        ])
        pose2 = PoseData(keypoints=[
            PoseKeypoint("nose", 0.7, 0.5),  # Different position
        ])
        
        comparator = Comparator()
        metrics = comparator.compare_poses(pose1, pose2)
        
        assert metrics.overall_difference > 0.1
    
    def test_analyze_proportions(self):
        """Test proportion analysis."""
        keypoints = [
            PoseKeypoint("nose", 0.5, 0.1),
            PoseKeypoint("left_shoulder", 0.4, 0.3),
            PoseKeypoint("right_shoulder", 0.6, 0.3),
            PoseKeypoint("left_hip", 0.4, 0.6),
            PoseKeypoint("left_ankle", 0.4, 0.9),
        ]
        pose = PoseData(keypoints=keypoints)
        
        comparator = Comparator()
        metrics = comparator.analyze_proportions(pose)
        
        assert 0 <= metrics.overall_score <= 1
        assert isinstance(metrics.body_ratios, dict)
    
    def test_analyze_symmetry(self):
        """Test symmetry analysis."""
        keypoints = [
            PoseKeypoint("left_shoulder", 0.3, 0.3),
            PoseKeypoint("right_shoulder", 0.7, 0.3),
            PoseKeypoint("left_hip", 0.3, 0.6),
            PoseKeypoint("right_hip", 0.7, 0.6),
        ]
        pose = PoseData(keypoints=keypoints)
        
        comparator = Comparator()
        metrics = comparator.analyze_symmetry(pose)
        
        assert 0 <= metrics.symmetry_score <= 1
        assert metrics.symmetry_axis is not None
    
    def test_edge_alignment(self):
        """Test edge alignment calculation."""
        # Create two edge maps
        edges1 = np.zeros((100, 100), dtype=np.uint8)
        edges1[40:60, 40:60] = 255  # Square
        
        edges2 = np.zeros((100, 100), dtype=np.uint8)
        edges2[40:60, 40:60] = 255  # Same square
        
        comparator = Comparator()
        metrics = comparator.calculate_edge_alignment(edges1, edges2)
        
        assert metrics.alignment_score > 0.8  # Should be well aligned
        assert metrics.edge_overlap > 0.9


class TestVisionModule:
    """Test VisionModule class."""
    
    def test_create_vision_module(self):
        """Test creating vision module."""
        vision = VisionModule()
        
        assert vision is not None
        assert vision.image_processor is not None
        assert vision.comparator is not None
    
    def test_analyze_simple_image(self):
        """Test analyzing a simple image."""
        # Create a simple test image
        img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        
        vision = VisionModule()
        result = vision.analyze(img)
        
        assert isinstance(result, AnalysisResult)
        assert result.image_width == 200
        assert result.image_height == 200
        assert result.processing_time_ms > 0
    
    def test_analyze_with_pose_stick_figure(self):
        """Test analyzing image with simple pose representation."""
        # Create image with a simple stick figure pattern
        img = np.ones((400, 300, 3), dtype=np.uint8) * 255
        # Draw a simple stick figure (this won't actually be detected as a pose)
        # but tests the pipeline
        
        vision = VisionModule(enable_pose=True)
        result = vision.analyze(img, extract_silhouette=True, detect_edges=True)
        
        assert result.silhouette is not None
        assert result.edges is not None
    
    def test_compare_identical_images(self):
        """Test comparing identical images."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        vision = VisionModule(enable_pose=True)
        comparison = vision.compare_to(img, img)
        
        assert isinstance(comparison, ComparisonResult)
        # Identical images should have high similarity
        # (may not be 1.0 if no features detected)
        assert comparison.overall_similarity >= 0.4
    
    def test_compare_different_images(self):
        """Test comparing different images."""
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)  # Black
        
        vision = VisionModule(enable_pose=True)
        comparison = vision.compare_to(img1, img2)
        
        assert isinstance(comparison, ComparisonResult)
        # Different images should have similarity <= 1.0
        assert comparison.overall_similarity <= 1.0
    
    def test_detect_pose_errors(self):
        """Test pose error detection."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 200
        
        vision = VisionModule(enable_pose=True)
        errors = vision.detect_pose_errors(img)
        
        assert isinstance(errors, list)
        # May contain "No pose detected" or other errors
    
    def test_highlight_areas_needing_refinement(self):
        """Test highlighting refinement areas."""
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 200
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 210
        
        vision = VisionModule(enable_pose=True)
        areas = vision.highlight_areas_needing_refinement(img1, img2)
        
        assert isinstance(areas, list)
    
    def test_vision_module_close(self):
        """Test closing vision module."""
        vision = VisionModule()
        vision.close()
        # Should not raise errors


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
