"""
Image processing utilities.

Handles loading, preprocessing, and basic image operations using OpenCV.
"""

from typing import Union, Optional, Tuple
from pathlib import Path
import numpy as np
import cv2
from PIL import Image


class ImageProcessor:
    """
    Handles image loading, preprocessing, and basic operations.
    
    This class provides utilities for working with images from various sources
    and preparing them for vision analysis.
    """
    
    @staticmethod
    def load_image(source: Union[str, Path, Image.Image, np.ndarray]) -> np.ndarray:
        """
        Load image from various sources.
        
        Args:
            source: Image source (file path, PIL Image, or numpy array)
            
        Returns:
            Image as numpy array in BGR format (OpenCV convention)
            
        Raises:
            ValueError: If source type is not supported
            FileNotFoundError: If file path does not exist
        """
        if isinstance(source, np.ndarray):
            # Already a numpy array
            if len(source.shape) == 2:
                # Grayscale, convert to BGR
                return cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
            elif source.shape[2] == 3:
                return source
            elif source.shape[2] == 4:
                # RGBA, convert to BGR
                return cv2.cvtColor(source, cv2.COLOR_RGBA2BGR)
            return source
        
        elif isinstance(source, Image.Image):
            # PIL Image
            if source.mode == 'RGB':
                # Convert RGB to BGR
                return cv2.cvtColor(np.array(source), cv2.COLOR_RGB2BGR)
            elif source.mode == 'RGBA':
                return cv2.cvtColor(np.array(source), cv2.COLOR_RGBA2BGR)
            elif source.mode == 'L':
                return cv2.cvtColor(np.array(source), cv2.COLOR_GRAY2BGR)
            else:
                # Convert to RGB first, then to BGR
                rgb_image = source.convert('RGB')
                return cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)
        
        elif isinstance(source, (str, Path)):
            # File path
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            
            image = cv2.imread(str(path))
            if image is None:
                raise ValueError(f"Failed to load image from: {path}")
            return image
        
        else:
            raise ValueError(f"Unsupported image source type: {type(source)}")
    
    @staticmethod
    def to_rgb(image: np.ndarray) -> np.ndarray:
        """
        Convert BGR image to RGB.
        
        Args:
            image: BGR image
            
        Returns:
            RGB image
        """
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale.
        
        Args:
            image: Input image
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def resize(
        image: np.ndarray,
        width: Optional[int] = None,
        height: Optional[int] = None,
        max_size: Optional[int] = None,
        interpolation: int = cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        Resize image with various options.
        
        Args:
            image: Input image
            width: Target width (None to maintain aspect ratio)
            height: Target height (None to maintain aspect ratio)
            max_size: Maximum dimension (maintains aspect ratio)
            interpolation: Interpolation method
            
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        
        if max_size is not None:
            # Scale to fit within max_size
            scale = max_size / max(h, w)
            width = int(w * scale)
            height = int(h * scale)
        elif width is not None and height is None:
            # Scale by width, maintain aspect ratio
            scale = width / w
            height = int(h * scale)
        elif height is not None and width is None:
            # Scale by height, maintain aspect ratio
            scale = height / h
            width = int(w * scale)
        elif width is None and height is None:
            return image
        
        return cv2.resize(image, (width, height), interpolation=interpolation)
    
    @staticmethod
    def extract_silhouette(
        image: np.ndarray,
        method: str = "grabcut",
        threshold: int = 127
    ) -> np.ndarray:
        """
        Extract silhouette/foreground mask from image.
        
        Args:
            image: Input image
            method: Extraction method ("threshold", "grabcut", "adaptive")
            threshold: Threshold value for simple thresholding
            
        Returns:
            Binary mask (0 or 255)
        """
        gray = ImageProcessor.to_grayscale(image)
        
        if method == "threshold":
            _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
            return mask
        
        elif method == "adaptive":
            mask = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            return mask
        
        elif method == "grabcut":
            # GrabCut algorithm for more sophisticated segmentation
            mask = np.zeros(image.shape[:2], np.uint8)
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # Define rectangle around the foreground
            h, w = image.shape[:2]
            rect = (10, 10, w - 20, h - 20)
            
            try:
                cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
                # Create binary mask
                binary_mask = np.where((mask == 2) | (mask == 0), 0, 255).astype('uint8')
                return binary_mask
            except (cv2.error, ValueError) as e:
                # Fallback to threshold if GrabCut fails
                # This can happen with very small images or images with too few colors
                _, binary_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
                return binary_mask
        
        else:
            raise ValueError(f"Unknown silhouette extraction method: {method}")
    
    @staticmethod
    def detect_edges(
        image: np.ndarray,
        low_threshold: int = 50,
        high_threshold: int = 150
    ) -> np.ndarray:
        """
        Detect edges in image using Canny edge detection.
        
        Args:
            image: Input image
            low_threshold: Lower threshold for Canny
            high_threshold: Upper threshold for Canny
            
        Returns:
            Edge map (binary image)
        """
        gray = ImageProcessor.to_grayscale(image)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)
        
        return edges
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalize image to 0-1 range.
        
        Args:
            image: Input image
            
        Returns:
            Normalized image (float32, 0-1 range)
        """
        return image.astype(np.float32) / 255.0
    
    @staticmethod
    def denormalize_image(image: np.ndarray) -> np.ndarray:
        """
        Convert normalized image back to 0-255 range.
        
        Args:
            image: Normalized image (0-1 range)
            
        Returns:
            Image in 0-255 range (uint8)
        """
        return (image * 255).astype(np.uint8)
    
    @staticmethod
    def get_dimensions(image: np.ndarray) -> Tuple[int, int]:
        """
        Get image dimensions.
        
        Args:
            image: Input image
            
        Returns:
            (width, height) tuple
        """
        h, w = image.shape[:2]
        return w, h
