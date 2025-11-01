"""
Main Imagination Module API.

This is the primary interface for the Imagination System, providing high-level
methods for style analysis, generation, and suggestions.
"""

import logging
from typing import Union, Optional, List
from pathlib import Path
import numpy as np
from PIL import Image

from imagination.core.style_analyzer import StyleAnalyzer
from imagination.core.reference_generator import ReferenceGenerator
from imagination.models.style_data import (
    StyleAnalysis,
    StyleSuggestion,
    GenerationParams,
)

logger = logging.getLogger(__name__)


class ImaginationModule:
    """
    Main Imagination Module for style suggestion and generation.
    
    This class provides the primary API for the Imagination System, which
    suggests alternative stylistic directions and generates reference images
    for inspiration without blindly copying AI-generated content.
    
    The module follows the principle that AI-generated images are reference
    material for inspiration, not final output. It analyzes style features
    and suggests transferable elements rather than replacing the artist's work.
    
    Example:
        >>> imagination = ImaginationModule()
        >>> 
        >>> # Analyze current style
        >>> style = imagination.tag_style_elements("canvas.png")
        >>> print(f"Line style: {style.line_style}")
        >>> print(f"Contrast: {style.contrast_level}")
        >>> 
        >>> # Generate stylized reference
        >>> params = GenerationParams(strength=0.7, style_prompt="oil painting")
        >>> suggestion = imagination.generate_stylized_reference("canvas.png", params)
        >>> 
        >>> # Get multiple style alternatives
        >>> suggestions = imagination.suggest_alternative_style("canvas.png")
        >>> for s in suggestions:
        ...     print(f"Try: {s.name}")
    """
    
    def __init__(self, simulation_mode: bool = True):
        """
        Initialize Imagination Module.
        
        Args:
            simulation_mode: Use simulation instead of real AI models.
                           In simulation mode, style generation is approximated
                           using image processing techniques.
        """
        self.simulation_mode = simulation_mode
        self.analyzer = StyleAnalyzer()
        self.generator = ReferenceGenerator(simulation_mode=simulation_mode)
        logger.info(f"ImaginationModule initialized (simulation_mode={simulation_mode})")
    
    def tag_style_elements(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        analyze_colors: bool = True,
        analyze_brushwork: bool = True,
        analyze_lighting: bool = True,
        analyze_form: bool = False,
    ) -> StyleAnalysis:
        """
        Analyze and tag style elements in an image.
        
        This method extracts style features like line style, contrast,
        color palette, brushwork characteristics, and lighting.
        
        Args:
            image: Input image (path, PIL Image, or numpy array)
            analyze_colors: Extract color palette
            analyze_brushwork: Analyze brush stroke characteristics
            analyze_lighting: Analyze lighting characteristics
            analyze_form: Analyze form exaggeration
            
        Returns:
            StyleAnalysis containing all detected style features
            
        Example:
            >>> style = imagination.tag_style_elements("artwork.png")
            >>> if style.color_palette:
            ...     print(f"Dominant colors: {style.color_palette.dominant_colors[:3]}")
            >>> if style.brushwork:
            ...     print(f"Stroke visibility: {style.brushwork.stroke_visibility:.2f}")
        """
        logger.info(f"Analyzing style elements for image")
        
        analysis = self.analyzer.analyze(
            image=image,
            analyze_colors=analyze_colors,
            analyze_brushwork=analyze_brushwork,
            analyze_lighting=analyze_lighting,
            analyze_form=analyze_form,
        )
        
        logger.info(f"Style analysis complete. Features: {analysis.get_features()}")
        return analysis
    
    def generate_stylized_reference(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        params: GenerationParams,
        target_style: Optional[StyleAnalysis] = None
    ) -> StyleSuggestion:
        """
        Generate a stylized reference image.
        
        This method creates a stylized version of the input image that can
        serve as inspiration. The result includes analysis of which elements
        are transferable to the working canvas.
        
        Important: The generated image is reference material, not a final output.
        It should be analyzed for transferable elements like lighting direction,
        color palette, or compositional choices.
        
        Args:
            image: Input image to stylize
            params: Generation parameters controlling the stylization
            target_style: Optional target style to apply
            
        Returns:
            StyleSuggestion containing the reference image, transferable
            elements, and applied features
            
        Example:
            >>> params = GenerationParams(
            ...     strength=0.75,
            ...     style_prompt="impressionist painting",
            ...     guidance_scale=7.5
            ... )
            >>> suggestion = imagination.generate_stylized_reference("sketch.png", params)
            >>> print(f"Transferable: {suggestion.transferable_elements}")
            >>> # Use suggestion.reference_image as inspiration
        """
        logger.info(f"Generating stylized reference with prompt: {params.style_prompt}")
        
        suggestion = self.generator.generate_stylized_reference(
            image=image,
            params=params,
            style_target=target_style,
        )
        
        logger.info(f"Generated reference: {suggestion.name}")
        logger.info(f"Transferable elements: {suggestion.transferable_elements}")
        
        return suggestion
    
    def suggest_alternative_style(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        current_style: Optional[StyleAnalysis] = None,
        n_suggestions: int = 3
    ) -> List[StyleSuggestion]:
        """
        Suggest multiple alternative stylistic directions.
        
        This method generates several stylized variations that explore
        different artistic directions. Each suggestion includes analysis
        of which style elements can be transferred to the actual artwork.
        
        Args:
            image: Input image (current WIP)
            current_style: Current style analysis (optional)
            n_suggestions: Number of style alternatives to generate
            
        Returns:
            List of StyleSuggestion objects, each with a different style
            
        Example:
            >>> suggestions = imagination.suggest_alternative_style("wip.png")
            >>> for suggestion in suggestions:
            ...     print(f"\\n{suggestion.name}:")
            ...     print(f"  Confidence: {suggestion.confidence:.1%}")
            ...     print(f"  Transferable: {', '.join(suggestion.transferable_elements)}")
            ...     # Display suggestion.reference_image for review
        """
        logger.info(f"Generating {n_suggestions} style suggestions")
        
        suggestions = self.generator.suggest_alternative_styles(
            image=image,
            current_style=current_style,
            n_suggestions=n_suggestions,
        )
        
        logger.info(f"Generated {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions):
            logger.debug(f"  {i+1}. {suggestion.name}: {suggestion.transferable_elements}")
        
        return suggestions
    
    def generate_with_mask(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        mask: np.ndarray,
        params: GenerationParams
    ) -> np.ndarray:
        """
        Generate stylized content for a specific masked region.
        
        This is useful for regenerating or restyling specific parts of an
        image while keeping the rest intact (inpainting/region-specific
        style transfer).
        
        Args:
            image: Input image
            mask: Binary mask (1.0 for regions to regenerate, 0.0 to keep)
            params: Generation parameters
            
        Returns:
            Image with mask-applied stylization
            
        Example:
            >>> # Create mask for specific region
            >>> mask = np.zeros((height, width), dtype=np.float32)
            >>> mask[100:200, 150:250] = 1.0  # Mark region to restyle
            >>> 
            >>> params = GenerationParams(strength=0.8, style_prompt="watercolor")
            >>> result = imagination.generate_with_mask("canvas.png", mask, params)
        """
        logger.info("Generating stylized content with mask")
        
        result = self.generator.generate_with_mask(
            image=image,
            mask=mask,
            params=params,
        )
        
        logger.info("Masked generation complete")
        return result
    
    def compare_styles(
        self,
        image1: Union[str, Path, Image.Image, np.ndarray],
        image2: Union[str, Path, Image.Image, np.ndarray]
    ) -> float:
        """
        Compare styles of two images.
        
        This method analyzes both images and compares their style
        characteristics, returning a similarity score.
        
        Args:
            image1: First image
            image2: Second image
            
        Returns:
            Similarity score (0-1, where 1 is identical style)
            
        Example:
            >>> similarity = imagination.compare_styles("canvas.png", "reference.png")
            >>> print(f"Style similarity: {similarity:.1%}")
        """
        logger.info("Comparing styles of two images")
        
        style1 = self.analyzer.analyze(image1)
        style2 = self.analyzer.analyze(image2)
        
        similarity = self.analyzer.compare_styles(style1, style2)
        
        logger.info(f"Style similarity: {similarity:.2%}")
        return similarity
    
    def extract_transferable_elements(
        self,
        reference: Union[str, Path, Image.Image, np.ndarray],
        current_canvas: Union[str, Path, Image.Image, np.ndarray]
    ) -> dict:
        """
        Analyze a reference image and identify which elements can be
        transferred to the current canvas.
        
        This helps artists decide what to learn from generated references
        without copying the entire image.
        
        Args:
            reference: Generated or reference image
            current_canvas: Current working canvas
            
        Returns:
            Dictionary describing transferable elements with scores
            
        Example:
            >>> elements = imagination.extract_transferable_elements(
            ...     "generated_ref.png",
            ...     "my_canvas.png"
            ... )
            >>> for element, info in elements.items():
            ...     print(f"{element}: confidence={info['confidence']:.1%}")
        """
        logger.info("Extracting transferable elements from reference")
        
        # Analyze both images
        ref_style = self.analyzer.analyze(reference)
        canvas_style = self.analyzer.analyze(current_canvas)
        
        transferable = {}
        
        # Compare color palettes
        if ref_style.color_palette and canvas_style.color_palette:
            temp_diff = abs(ref_style.color_palette.temperature - 
                          canvas_style.color_palette.temperature)
            if temp_diff > 0.2:
                transferable["color_temperature"] = {
                    "current": canvas_style.color_palette.temperature,
                    "suggested": ref_style.color_palette.temperature,
                    "confidence": 0.9,
                }
        
        # Compare lighting
        if ref_style.lighting and canvas_style.lighting:
            intensity_diff = abs(ref_style.lighting.intensity - 
                               canvas_style.lighting.intensity)
            if intensity_diff > 0.2:
                transferable["lighting_intensity"] = {
                    "current": canvas_style.lighting.intensity,
                    "suggested": ref_style.lighting.intensity,
                    "confidence": 0.85,
                }
            
            # Light direction
            transferable["lighting_direction"] = {
                "suggested": ref_style.lighting.direction,
                "confidence": 0.75,
            }
        
        # Compare brushwork
        if ref_style.brushwork and canvas_style.brushwork:
            texture_diff = abs(ref_style.brushwork.texture_intensity - 
                             canvas_style.brushwork.texture_intensity)
            if texture_diff > 0.3:
                transferable["texture_intensity"] = {
                    "current": canvas_style.brushwork.texture_intensity,
                    "suggested": ref_style.brushwork.texture_intensity,
                    "confidence": 0.8,
                }
        
        logger.info(f"Found {len(transferable)} transferable elements")
        return transferable
    
    def close(self):
        """
        Clean up resources.
        
        Call this when done using the module to release any resources.
        """
        logger.info("ImaginationModule closed")
