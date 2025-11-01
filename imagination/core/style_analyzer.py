"""
Style analyzer for extracting style features from images.

Analyzes images to extract style characteristics like line style, contrast,
color palette, brushwork, and lighting.
"""

import time
from typing import Union, Optional, Tuple, List
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

from imagination.models.style_data import (
    StyleAnalysis,
    ColorPalette,
    BrushworkAnalysis,
    LightingAnalysis,
    FormExaggeration,
    LineStyle,
    ContrastLevel,
)


class StyleAnalyzer:
    """
    Analyzes images to extract style features.
    
    This class provides methods to analyze various aspects of an image's style,
    including color palette, contrast, brushwork characteristics, and lighting.
    """
    
    def __init__(self):
        """Initialize the style analyzer."""
        pass
    
    def analyze(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        analyze_colors: bool = True,
        analyze_brushwork: bool = True,
        analyze_lighting: bool = True,
        analyze_form: bool = False,
    ) -> StyleAnalysis:
        """
        Perform comprehensive style analysis on an image.
        
        Args:
            image: Input image (path, PIL Image, or numpy array)
            analyze_colors: Extract color palette
            analyze_brushwork: Analyze brush stroke characteristics
            analyze_lighting: Analyze lighting characteristics
            analyze_form: Analyze form exaggeration
            
        Returns:
            StyleAnalysis containing all analyzed features
        """
        start_time = time.time()
        
        # Load and prepare image
        img_array = self._load_image(image)
        
        # Initialize analysis result
        analysis = StyleAnalysis()
        
        # Analyze line style and contrast (always performed)
        analysis.line_style = self._analyze_line_style(img_array)
        analysis.contrast_level = self._analyze_contrast(img_array)
        
        # Optional detailed analyses
        if analyze_colors:
            analysis.color_palette = self._analyze_color_palette(img_array)
        
        if analyze_brushwork:
            analysis.brushwork = self._analyze_brushwork(img_array)
        
        if analyze_lighting:
            analysis.lighting = self._analyze_lighting(img_array)
        
        if analyze_form:
            analysis.form_exaggeration = self._analyze_form_exaggeration(img_array)
        
        # Set metadata
        analysis.confidence = 0.8  # Default confidence
        analysis.processing_time_ms = (time.time() - start_time) * 1000
        
        return analysis
    
    def _load_image(self, image: Union[str, Path, Image.Image, np.ndarray]) -> np.ndarray:
        """
        Load image from various sources and convert to numpy array (BGR).
        
        Args:
            image: Input image
            
        Returns:
            Image as numpy array in BGR format
        """
        if isinstance(image, (str, Path)):
            img = cv2.imread(str(image))
            if img is None:
                raise ValueError(f"Failed to load image from {image}")
            return img
        elif isinstance(image, Image.Image):
            # Convert PIL Image (RGB) to numpy array (BGR)
            img_rgb = np.array(image)
            if len(img_rgb.shape) == 2:  # Grayscale
                img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_GRAY2RGB)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            return img_bgr
        elif isinstance(image, np.ndarray):
            return image.copy()
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
    
    def _analyze_line_style(self, image: np.ndarray) -> LineStyle:
        """
        Analyze line style characteristics.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Detected line style
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Analyze edge characteristics
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calculate edge continuity (how connected the edges are)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        avg_contour_length = np.mean([len(c) for c in contours]) if contours else 0
        
        # Calculate edge smoothness (using gradient variance)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        smoothness = 1.0 - min(np.std(gradient_magnitude) / 100.0, 1.0)
        
        # Classify line style based on characteristics
        if smoothness > 0.7:
            return LineStyle.SMOOTH
        elif edge_density > 0.2:
            return LineStyle.SKETCHY
        elif avg_contour_length < 10:
            return LineStyle.BROKEN
        elif smoothness < 0.4:
            return LineStyle.ANGULAR
        else:
            return LineStyle.FLOWING
    
    def _analyze_contrast(self, image: np.ndarray) -> ContrastLevel:
        """
        Analyze contrast level.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Detected contrast level
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate contrast metrics
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        value_range = max_val - min_val
        
        # Calculate standard deviation (measure of spread)
        std_dev = np.std(gray)
        
        # Normalize contrast score
        contrast_score = (value_range / 255.0) * (std_dev / 128.0)
        
        # Classify contrast level
        if contrast_score < 0.3:
            return ContrastLevel.LOW
        elif contrast_score < 0.6:
            return ContrastLevel.MEDIUM
        elif contrast_score < 0.85:
            return ContrastLevel.HIGH
        else:
            return ContrastLevel.DRAMATIC
    
    def _analyze_color_palette(self, image: np.ndarray, n_colors: int = 5) -> ColorPalette:
        """
        Extract dominant color palette from image.
        
        Args:
            image: Input image in BGR format
            n_colors: Number of dominant colors to extract
            
        Returns:
            ColorPalette with dominant colors and characteristics
        """
        # Convert BGR to RGB for consistent color representation
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Reshape image to list of pixels
        pixels = img_rgb.reshape(-1, 3).astype(np.float32)
        
        # Use k-means to find dominant colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels, n_colors, None, criteria, 10, cv2.KMEANS_PP_CENTERS
        )
        
        # Calculate color weights
        unique, counts = np.unique(labels, return_counts=True)
        weights = counts / counts.sum()
        
        # Sort by weight
        sorted_indices = np.argsort(weights)[::-1]
        dominant_colors = [tuple(map(int, centers[i])) for i in sorted_indices]
        color_weights = [float(weights[i]) for i in sorted_indices]
        
        # Calculate temperature (warm vs cool)
        # Warm colors have more red/yellow, cool colors have more blue
        temperature = self._calculate_color_temperature(dominant_colors, color_weights)
        
        # Calculate average saturation and brightness
        saturation, brightness = self._calculate_color_metrics(img_rgb)
        
        return ColorPalette(
            dominant_colors=dominant_colors,
            color_weights=color_weights,
            temperature=temperature,
            saturation=saturation,
            brightness=brightness,
        )
    
    def _calculate_color_temperature(
        self,
        colors: List[Tuple[int, int, int]],
        weights: List[float]
    ) -> float:
        """
        Calculate color temperature (warm vs cool).
        
        Args:
            colors: List of RGB colors
            weights: Weights for each color
            
        Returns:
            Temperature value (0=cool, 1=warm)
        """
        temperature = 0.0
        for color, weight in zip(colors, weights):
            r, g, b = color
            # Warm bias: more red and yellow (red + green)
            # Cool bias: more blue
            color_temp = (r + g - b) / 510.0  # Normalize to [-1, 1]
            temperature += (color_temp + 1.0) / 2.0 * weight  # Map to [0, 1]
        return temperature
    
    def _calculate_color_metrics(self, image_rgb: np.ndarray) -> Tuple[float, float]:
        """
        Calculate average saturation and brightness.
        
        Args:
            image_rgb: Input image in RGB format
            
        Returns:
            Tuple of (saturation, brightness)
        """
        # Convert to HSV
        img_hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
        
        # Extract saturation and value channels
        saturation = np.mean(img_hsv[:, :, 1]) / 255.0
        brightness = np.mean(img_hsv[:, :, 2]) / 255.0
        
        return saturation, brightness
    
    def _analyze_brushwork(self, image: np.ndarray) -> BrushworkAnalysis:
        """
        Analyze brushwork characteristics.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            BrushworkAnalysis with stroke and texture metrics
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Analyze texture using Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_intensity = min(np.var(laplacian) / 1000.0, 1.0)
        
        # Analyze edge softness using gradient
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        gradient = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Sharp edges have high gradient, soft edges have low gradient
        edge_softness = 1.0 - min(np.mean(gradient) / 100.0, 1.0)
        
        # Estimate stroke visibility from high-frequency components
        dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
        
        # High frequencies indicate visible strokes
        h, w = magnitude.shape
        high_freq_region = magnitude[h//4:3*h//4, w//4:3*w//4]
        stroke_visibility = min(np.mean(high_freq_region) / np.mean(magnitude), 1.0)
        
        # Estimate layering from color variance
        color_variance = np.mean([np.var(image[:, :, i]) for i in range(3)])
        layering = min(color_variance / 5000.0, 1.0)
        
        return BrushworkAnalysis(
            stroke_visibility=float(stroke_visibility),
            texture_intensity=float(texture_intensity),
            edge_softness=float(edge_softness),
            layering=float(layering),
        )
    
    def _analyze_lighting(self, image: np.ndarray) -> LightingAnalysis:
        """
        Analyze lighting characteristics.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            LightingAnalysis with light direction and intensity
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate overall intensity
        intensity = np.mean(gray) / 255.0
        
        # Calculate contrast ratio
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        contrast_ratio = (max_val + 1) / (min_val + 1)
        
        # Estimate light direction from gradient
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        
        # Average gradient direction
        avg_grad_x = np.mean(sobel_x)
        avg_grad_y = np.mean(sobel_y)
        
        # Normalize direction
        magnitude = np.sqrt(avg_grad_x**2 + avg_grad_y**2)
        if magnitude > 0:
            direction = (float(avg_grad_x / magnitude), float(avg_grad_y / magnitude))
        else:
            direction = (0.0, 0.0)
        
        # Estimate ambient light from shadows (dark regions)
        dark_threshold = np.percentile(gray, 25)
        dark_regions = gray < dark_threshold
        if np.any(dark_regions):
            ambient_level = float(np.mean(gray[dark_regions]) / 255.0)
        else:
            ambient_level = 0.5
        
        return LightingAnalysis(
            direction=direction,
            intensity=float(intensity),
            contrast_ratio=float(contrast_ratio),
            ambient_level=ambient_level,
        )
    
    def _analyze_form_exaggeration(self, image: np.ndarray) -> FormExaggeration:
        """
        Analyze form exaggeration and stylization.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            FormExaggeration with proportion and emphasis metrics
        """
        # This is a placeholder for more advanced analysis
        # In a full implementation, this would use pose/landmark detection
        # to measure deviation from realistic proportions
        
        return FormExaggeration(
            proportion_shift=0.0,
            feature_emphasis=[],
            simplification=0.0,
        )
    
    def compare_styles(
        self,
        style1: StyleAnalysis,
        style2: StyleAnalysis
    ) -> float:
        """
        Compare two style analyses and return similarity score.
        
        Args:
            style1: First style analysis
            style2: Second style analysis
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        similarity = 0.0
        count = 0
        
        # Compare color palettes
        if style1.color_palette and style2.color_palette:
            temp_diff = abs(style1.color_palette.temperature - style2.color_palette.temperature)
            sat_diff = abs(style1.color_palette.saturation - style2.color_palette.saturation)
            color_sim = 1.0 - (temp_diff + sat_diff) / 2.0
            similarity += color_sim
            count += 1
        
        # Compare brushwork
        if style1.brushwork and style2.brushwork:
            brushwork_diff = sum([
                abs(style1.brushwork.stroke_visibility - style2.brushwork.stroke_visibility),
                abs(style1.brushwork.texture_intensity - style2.brushwork.texture_intensity),
                abs(style1.brushwork.edge_softness - style2.brushwork.edge_softness),
            ]) / 3.0
            brushwork_sim = 1.0 - brushwork_diff
            similarity += brushwork_sim
            count += 1
        
        # Compare lighting
        if style1.lighting and style2.lighting:
            intensity_diff = abs(style1.lighting.intensity - style2.lighting.intensity)
            lighting_sim = 1.0 - intensity_diff
            similarity += lighting_sim
            count += 1
        
        return similarity / count if count > 0 else 0.0
