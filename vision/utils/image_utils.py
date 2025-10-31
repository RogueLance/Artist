"""
Image utility functions.

Additional image processing helpers beyond the core ImageProcessor.
"""

from typing import Tuple, Optional
import numpy as np
import cv2


class ImageUtils:
    """
    Utility functions for image operations.
    """
    
    @staticmethod
    def crop_to_bounds(
        image: np.ndarray,
        bounds: Tuple[int, int, int, int],
        padding: int = 0
    ) -> np.ndarray:
        """
        Crop image to bounding box with optional padding.
        
        Args:
            image: Input image
            bounds: (x, y, width, height)
            padding: Padding to add around bounds
            
        Returns:
            Cropped image
        """
        x, y, w, h = bounds
        h_img, w_img = image.shape[:2]
        
        # Add padding
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w_img, x + w + padding)
        y2 = min(h_img, y + h + padding)
        
        return image[y1:y2, x1:x2]
    
    @staticmethod
    def blend_images(
        image1: np.ndarray,
        image2: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Blend two images together.
        
        Args:
            image1: First image
            image2: Second image
            alpha: Blend factor (0.0 = all image1, 1.0 = all image2)
            
        Returns:
            Blended image
        """
        # Ensure same size
        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
        
        return cv2.addWeighted(image1, 1 - alpha, image2, alpha, 0)
    
    @staticmethod
    def apply_mask(
        image: np.ndarray,
        mask: np.ndarray,
        background_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> np.ndarray:
        """
        Apply binary mask to image.
        
        Args:
            image: Input image
            mask: Binary mask (0 or 255)
            background_color: Color for masked areas
            
        Returns:
            Masked image
        """
        # Ensure mask is same size
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
        
        # Ensure mask is single channel
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        
        # Create output
        output = image.copy()
        
        # Apply mask
        bg = np.full_like(image, background_color)
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        output = np.where(mask_3ch > 0, image, bg)
        
        return output
    
    @staticmethod
    def calculate_histogram(image: np.ndarray, bins: int = 256) -> np.ndarray:
        """
        Calculate image histogram.
        
        Args:
            image: Input image
            bins: Number of bins
            
        Returns:
            Histogram array
        """
        if len(image.shape) == 3:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        hist = cv2.calcHist([gray], [0], None, [bins], [0, 256])
        return hist.flatten()
    
    @staticmethod
    def match_histogram(
        source: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """
        Match histogram of source to reference.
        
        Args:
            source: Source image
            reference: Reference image
            
        Returns:
            Source image with matched histogram
        """
        # Convert to grayscale if needed
        if len(source.shape) == 3:
            # Process each channel
            matched = np.zeros_like(source)
            for i in range(3):
                matched[:, :, i] = ImageUtils._match_histogram_channel(
                    source[:, :, i],
                    reference[:, :, i] if len(reference.shape) == 3 else reference
                )
            return matched
        else:
            return ImageUtils._match_histogram_channel(source, reference)
    
    @staticmethod
    def _match_histogram_channel(
        source: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """Match histogram for single channel."""
        # Calculate CDFs
        source_hist = cv2.calcHist([source], [0], None, [256], [0, 256])
        reference_hist = cv2.calcHist([reference], [0], None, [256], [0, 256])
        
        source_cdf = source_hist.cumsum()
        reference_cdf = reference_hist.cumsum()
        
        # Normalize CDFs
        source_cdf = source_cdf / source_cdf[-1]
        reference_cdf = reference_cdf / reference_cdf[-1]
        
        # Create lookup table
        lookup = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            j = np.argmin(np.abs(reference_cdf - source_cdf[i]))
            lookup[i] = j
        
        # Apply lookup
        return lookup[source]
    
    @staticmethod
    def calculate_difference(
        image1: np.ndarray,
        image2: np.ndarray
    ) -> np.ndarray:
        """
        Calculate absolute difference between images.
        
        Args:
            image1: First image
            image2: Second image
            
        Returns:
            Difference image
        """
        # Ensure same size
        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
        
        return cv2.absdiff(image1, image2)
