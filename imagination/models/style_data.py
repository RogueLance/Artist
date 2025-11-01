"""
Style data structures for the Imagination System.

Contains data classes for representing style features, analysis results,
and generated references.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import numpy as np


class StyleFeature(Enum):
    """Types of style features that can be analyzed."""
    LINE_STYLE = "line_style"
    CONTRAST = "contrast"
    COLOR_PALETTE = "color_palette"
    BRUSHWORK = "brushwork"
    FORM_EXAGGERATION = "form_exaggeration"
    LIGHTING = "lighting"
    TEXTURE = "texture"
    COMPOSITION = "composition"


class LineStyle(Enum):
    """Line style characteristics."""
    SMOOTH = "smooth"
    SKETCHY = "sketchy"
    ANGULAR = "angular"
    FLOWING = "flowing"
    BROKEN = "broken"
    HATCHED = "hatched"


class ContrastLevel(Enum):
    """Contrast intensity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    DRAMATIC = "dramatic"


@dataclass
class ColorPalette:
    """
    Represents a color palette extracted from an image.
    
    Attributes:
        dominant_colors: List of dominant colors as (R, G, B) tuples
        color_weights: Weights for each dominant color (sum to 1.0)
        temperature: Warm (>0.5) vs Cool (<0.5) color bias
        saturation: Average saturation level (0-1)
        brightness: Average brightness level (0-1)
    """
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    color_weights: List[float] = field(default_factory=list)
    temperature: float = 0.5  # 0=cool, 1=warm
    saturation: float = 0.5
    brightness: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dominant_colors": self.dominant_colors,
            "color_weights": self.color_weights,
            "temperature": self.temperature,
            "saturation": self.saturation,
            "brightness": self.brightness,
        }


@dataclass
class BrushworkAnalysis:
    """
    Analysis of brushwork characteristics.
    
    Attributes:
        stroke_visibility: How visible individual brush strokes are (0-1)
        texture_intensity: Amount of texture/grain (0-1)
        edge_softness: How soft/blended the edges are (0-1)
        layering: Evidence of paint layering (0-1)
    """
    stroke_visibility: float = 0.5
    texture_intensity: float = 0.5
    edge_softness: float = 0.5
    layering: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stroke_visibility": self.stroke_visibility,
            "texture_intensity": self.texture_intensity,
            "edge_softness": self.edge_softness,
            "layering": self.layering,
        }


@dataclass
class LightingAnalysis:
    """
    Analysis of lighting characteristics.
    
    Attributes:
        direction: Primary light direction as (x, y) normalized vector
        intensity: Overall light intensity (0-1)
        contrast_ratio: Ratio between lightest and darkest areas
        ambient_level: Amount of ambient/fill light (0-1)
    """
    direction: Tuple[float, float] = (0.0, 0.0)
    intensity: float = 0.5
    contrast_ratio: float = 1.0
    ambient_level: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "direction": self.direction,
            "intensity": self.intensity,
            "contrast_ratio": self.contrast_ratio,
            "ambient_level": self.ambient_level,
        }


@dataclass
class FormExaggeration:
    """
    Analysis of form exaggeration/stylization.
    
    Attributes:
        proportion_shift: How much proportions deviate from realistic (0-1)
        feature_emphasis: Which features are emphasized
        simplification: Level of detail simplification (0-1)
    """
    proportion_shift: float = 0.0
    feature_emphasis: List[str] = field(default_factory=list)
    simplification: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proportion_shift": self.proportion_shift,
            "feature_emphasis": self.feature_emphasis,
            "simplification": self.simplification,
        }


@dataclass
class StyleAnalysis:
    """
    Comprehensive style analysis result.
    
    Contains all analyzed style features from an image.
    """
    # Basic style metrics
    line_style: Optional[LineStyle] = None
    contrast_level: Optional[ContrastLevel] = None
    
    # Detailed analyses
    color_palette: Optional[ColorPalette] = None
    brushwork: Optional[BrushworkAnalysis] = None
    lighting: Optional[LightingAnalysis] = None
    form_exaggeration: Optional[FormExaggeration] = None
    
    # Metadata
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_features(self) -> List[StyleFeature]:
        """Get list of analyzed style features."""
        features = []
        if self.line_style is not None:
            features.append(StyleFeature.LINE_STYLE)
        if self.contrast_level is not None:
            features.append(StyleFeature.CONTRAST)
        if self.color_palette is not None:
            features.append(StyleFeature.COLOR_PALETTE)
        if self.brushwork is not None:
            features.append(StyleFeature.BRUSHWORK)
        if self.lighting is not None:
            features.append(StyleFeature.LIGHTING)
        if self.form_exaggeration is not None:
            features.append(StyleFeature.FORM_EXAGGERATION)
        return features
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "line_style": self.line_style.value if self.line_style else None,
            "contrast_level": self.contrast_level.value if self.contrast_level else None,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
        }
        
        if self.color_palette:
            result["color_palette"] = self.color_palette.to_dict()
        if self.brushwork:
            result["brushwork"] = self.brushwork.to_dict()
        if self.lighting:
            result["lighting"] = self.lighting.to_dict()
        if self.form_exaggeration:
            result["form_exaggeration"] = self.form_exaggeration.to_dict()
        
        return result


@dataclass
class StyleSuggestion:
    """
    A suggested style alternative.
    
    Attributes:
        name: Name/description of the style
        features: Style features to apply
        transferable_elements: Specific elements that can be transferred
        reference_image: Generated reference image (numpy array)
        mask: Optional mask for region-specific application
        confidence: Confidence in the suggestion (0-1)
    """
    name: str
    features: Dict[str, Any] = field(default_factory=dict)
    transferable_elements: List[str] = field(default_factory=list)
    reference_image: Optional[np.ndarray] = None
    mask: Optional[np.ndarray] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes image data)."""
        return {
            "name": self.name,
            "features": self.features,
            "transferable_elements": self.transferable_elements,
            "has_reference": self.reference_image is not None,
            "has_mask": self.mask is not None,
            "confidence": self.confidence,
        }


@dataclass
class GenerationParams:
    """
    Parameters for style generation.
    
    Attributes:
        strength: How much to alter the original image (0-1)
        guidance_scale: How closely to follow the style prompt (1-20)
        steps: Number of diffusion steps
        seed: Random seed for reproducibility
        mask_region: Optional region to apply generation to
        style_prompt: Text prompt for style guidance
    """
    strength: float = 0.75
    guidance_scale: float = 7.5
    steps: int = 50
    seed: Optional[int] = None
    mask_region: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
    style_prompt: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strength": self.strength,
            "guidance_scale": self.guidance_scale,
            "steps": self.steps,
            "seed": self.seed,
            "mask_region": self.mask_region,
            "style_prompt": self.style_prompt,
        }
