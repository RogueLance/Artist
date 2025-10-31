"""
Reference generator for creating stylized variations.

Simulates style generation through image processing techniques.
In production, this would interface with models like SDXL, Kandinsky, etc.
"""

import time
from typing import Union, Optional, Tuple, List
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2

from imagination.models.style_data import (
    StyleSuggestion,
    GenerationParams,
    StyleAnalysis,
)


class ReferenceGenerator:
    """
    Generates stylized reference images.
    
    This class simulates style generation through image processing.
    In production, this would interface with AI models like SDXL.
    
    Note:
        This is a simulation that uses image processing techniques to
        approximate style transfer. For production, integrate actual
        diffusion models or other generative AI systems.
    """
    
    def __init__(self, simulation_mode: bool = True):
        """
        Initialize the reference generator.
        
        Args:
            simulation_mode: Use simulation instead of real models
        """
        self.simulation_mode = simulation_mode
    
    def generate_stylized_reference(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        params: GenerationParams,
        style_target: Optional[StyleAnalysis] = None
    ) -> StyleSuggestion:
        """
        Generate a stylized reference image.
        
        Args:
            image: Input image to stylize
            params: Generation parameters
            style_target: Target style to apply (optional)
            
        Returns:
            StyleSuggestion with generated reference
        """
        # Load image
        img = self._load_image(image)
        
        if self.simulation_mode:
            # Use image processing simulation
            stylized = self._simulate_style_generation(img, params, style_target)
        else:
            # Placeholder for real model integration
            raise NotImplementedError("Real model integration not yet implemented")
        
        # Create mask if region specified
        mask = None
        if params.mask_region:
            mask = self._create_region_mask(img.shape[:2], params.mask_region)
        
        # Identify transferable elements based on style
        transferable = self._identify_transferable_elements(params, style_target)
        
        return StyleSuggestion(
            name=params.style_prompt or "Generated Style",
            features=self._extract_applied_features(params, style_target),
            transferable_elements=transferable,
            reference_image=stylized,
            mask=mask,
            confidence=0.8,
        )
    
    def generate_with_mask(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        mask: np.ndarray,
        params: GenerationParams
    ) -> np.ndarray:
        """
        Generate stylized content for a specific masked region.
        
        Args:
            image: Input image
            mask: Binary mask (1 for regions to regenerate)
            params: Generation parameters
            
        Returns:
            Generated image with mask applied
        """
        img = self._load_image(image)
        
        # Generate stylized version
        stylized = self._simulate_style_generation(img, params, None)
        
        # Apply mask to blend original and stylized
        mask_3ch = np.stack([mask] * 3, axis=-1).astype(np.float32)
        result = img * (1 - mask_3ch) + stylized * mask_3ch
        
        return result.astype(np.uint8)
    
    def _load_image(self, image: Union[str, Path, Image.Image, np.ndarray]) -> np.ndarray:
        """
        Load and normalize image to RGB numpy array.
        
        Args:
            image: Input image
            
        Returns:
            Image as RGB numpy array
        """
        if isinstance(image, (str, Path)):
            img = Image.open(image).convert('RGB')
            return np.array(img)
        elif isinstance(image, Image.Image):
            return np.array(image.convert('RGB'))
        elif isinstance(image, np.ndarray):
            if len(image.shape) == 2:
                # Grayscale to RGB
                return np.stack([image] * 3, axis=-1)
            elif image.shape[2] == 4:
                # RGBA to RGB
                return image[:, :, :3]
            return image.copy()
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
    
    def _simulate_style_generation(
        self,
        image: np.ndarray,
        params: GenerationParams,
        style_target: Optional[StyleAnalysis]
    ) -> np.ndarray:
        """
        Simulate style generation using image processing.
        
        Args:
            image: Input image (RGB)
            params: Generation parameters
            style_target: Target style (optional)
            
        Returns:
            Stylized image
        """
        # Convert to PIL for easier processing
        pil_img = Image.fromarray(image)
        
        # Apply various transformations based on strength
        strength = params.strength
        
        # 1. Adjust contrast based on style
        if style_target and style_target.contrast_level:
            contrast_factor = self._get_contrast_factor(style_target.contrast_level)
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(1.0 + (contrast_factor - 1.0) * strength)
        
        # 2. Adjust colors based on palette
        if style_target and style_target.color_palette:
            saturation_factor = style_target.color_palette.saturation
            enhancer = ImageEnhance.Color(pil_img)
            pil_img = enhancer.enhance(1.0 + (saturation_factor - 0.5) * strength * 2)
            
            brightness_factor = style_target.color_palette.brightness
            enhancer = ImageEnhance.Brightness(pil_img)
            pil_img = enhancer.enhance(1.0 + (brightness_factor - 0.5) * strength)
        
        # 3. Apply texture/brushwork effects
        if style_target and style_target.brushwork:
            texture_strength = style_target.brushwork.texture_intensity * strength
            if texture_strength > 0.3:
                # Add texture through noise
                img_array = np.array(pil_img).astype(np.float32)
                noise = np.random.normal(0, 10 * texture_strength, img_array.shape)
                img_array = np.clip(img_array + noise, 0, 255)
                pil_img = Image.fromarray(img_array.astype(np.uint8))
            
            edge_softness = style_target.brushwork.edge_softness
            if edge_softness > 0.5:
                # Soften edges
                radius = int(5 * edge_softness * strength)
                pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=radius))
        
        # 4. Apply edge enhancement or smoothing based on line style
        if style_target and style_target.line_style:
            line_style = style_target.line_style.value
            if line_style in ["angular", "sketchy"]:
                # Enhance edges
                pil_img = pil_img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            elif line_style in ["smooth", "flowing"]:
                # Smooth
                pil_img = pil_img.filter(ImageFilter.SMOOTH_MORE)
        
        # 5. Apply stylization filter if high strength
        if strength > 0.6:
            img_array = np.array(pil_img)
            # Convert to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Apply stylization
            stylized_bgr = cv2.stylization(img_bgr, sigma_s=60, sigma_r=0.6)
            
            # Blend with original
            blend_factor = (strength - 0.6) / 0.4  # Map [0.6, 1.0] to [0, 1]
            result_bgr = cv2.addWeighted(img_bgr, 1 - blend_factor, stylized_bgr, blend_factor, 0)
            
            # Convert back to RGB
            result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(result_rgb)
        
        return np.array(pil_img)
    
    def _get_contrast_factor(self, contrast_level) -> float:
        """
        Get contrast enhancement factor from contrast level.
        
        Args:
            contrast_level: ContrastLevel enum value
            
        Returns:
            Contrast factor (1.0 = no change)
        """
        from imagination.models.style_data import ContrastLevel
        
        contrast_map = {
            ContrastLevel.LOW: 0.7,
            ContrastLevel.MEDIUM: 1.0,
            ContrastLevel.HIGH: 1.4,
            ContrastLevel.DRAMATIC: 2.0,
        }
        return contrast_map.get(contrast_level, 1.0)
    
    def _create_region_mask(
        self,
        image_shape: Tuple[int, int],
        region: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Create a binary mask for a specific region.
        
        Args:
            image_shape: (height, width) of image
            region: (x, y, width, height) of region
            
        Returns:
            Binary mask array
        """
        mask = np.zeros(image_shape, dtype=np.float32)
        x, y, w, h = region
        
        # Ensure region is within bounds
        x = max(0, min(x, image_shape[1]))
        y = max(0, min(y, image_shape[0]))
        w = min(w, image_shape[1] - x)
        h = min(h, image_shape[0] - y)
        
        mask[y:y+h, x:x+w] = 1.0
        
        return mask
    
    def _identify_transferable_elements(
        self,
        params: GenerationParams,
        style_target: Optional[StyleAnalysis]
    ) -> List[str]:
        """
        Identify which style elements can be transferred.
        
        Args:
            params: Generation parameters
            style_target: Target style analysis
            
        Returns:
            List of transferable element names
        """
        transferable = []
        
        if style_target:
            if style_target.color_palette:
                transferable.append("color_palette")
            if style_target.brushwork:
                transferable.append("brushwork")
            if style_target.lighting:
                transferable.append("lighting_direction")
            if style_target.line_style:
                transferable.append("line_style")
            if style_target.contrast_level:
                transferable.append("contrast")
        else:
            # Add default transferable elements when no style target
            transferable.extend(["color_palette", "contrast", "line_style"])
        
        # Add generic elements based on params
        if params.style_prompt:
            if "texture" in params.style_prompt.lower():
                transferable.append("texture")
            if "detail" in params.style_prompt.lower():
                transferable.append("detail_level")
            if "paint" in params.style_prompt.lower() or "brush" in params.style_prompt.lower():
                if "brushwork" not in transferable:
                    transferable.append("brushwork")
            if "light" in params.style_prompt.lower():
                if "lighting_direction" not in transferable:
                    transferable.append("lighting_direction")
        
        return transferable
    
    def _extract_applied_features(
        self,
        params: GenerationParams,
        style_target: Optional[StyleAnalysis]
    ) -> dict:
        """
        Extract features that were applied during generation.
        
        Args:
            params: Generation parameters
            style_target: Target style analysis
            
        Returns:
            Dictionary of applied features
        """
        features = {
            "strength": params.strength,
            "guidance_scale": params.guidance_scale,
            "style_prompt": params.style_prompt,
        }
        
        if style_target:
            if style_target.color_palette:
                features["color_temperature"] = style_target.color_palette.temperature
                features["saturation"] = style_target.color_palette.saturation
            if style_target.brushwork:
                features["texture_intensity"] = style_target.brushwork.texture_intensity
            if style_target.line_style:
                features["line_style"] = style_target.line_style.value
        
        return features
    
    def suggest_alternative_styles(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        current_style: Optional[StyleAnalysis] = None,
        n_suggestions: int = 3
    ) -> List[StyleSuggestion]:
        """
        Generate multiple style suggestions.
        
        Args:
            image: Input image
            current_style: Current style analysis (optional)
            n_suggestions: Number of suggestions to generate
            
        Returns:
            List of StyleSuggestion objects
        """
        suggestions = []
        
        # Define some preset style variations
        style_presets = [
            ("Sketchy", GenerationParams(strength=0.5, style_prompt="sketchy pencil drawing")),
            ("Painterly", GenerationParams(strength=0.7, style_prompt="oil painting style")),
            ("High Contrast", GenerationParams(strength=0.6, style_prompt="high contrast dramatic")),
            ("Soft Watercolor", GenerationParams(strength=0.8, style_prompt="soft watercolor")),
            ("Bold Lines", GenerationParams(strength=0.6, style_prompt="bold ink lines")),
        ]
        
        # Generate suggestions
        for i, (name, params) in enumerate(style_presets[:n_suggestions]):
            suggestion = self.generate_stylized_reference(image, params, current_style)
            suggestion.name = name
            suggestions.append(suggestion)
        
        return suggestions
