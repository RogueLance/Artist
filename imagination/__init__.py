"""
Imagination System - Style Suggestion Engine for Cerebrum AI Art Platform.

The Imagination System provides style analysis and generation capabilities
that help explore alternative artistic directions. It follows the principle
that AI-generated images are reference material, not final output.

Main Components:
    - ImaginationModule: Primary API for style operations
    - StyleAnalyzer: Analyzes and tags style features
    - ReferenceGenerator: Generates stylized references
    - Style models: Data structures for style representation

Design Principles:
    - AI-generated images are inspiration, not output
    - Structure and anatomy correctness take precedence
    - Only suggest transferable elements (lighting, palette, etc.)
    - All generation is traceable and intentional

Example:
    >>> from imagination import ImaginationModule, GenerationParams
    >>> 
    >>> # Initialize
    >>> imagination = ImaginationModule()
    >>> 
    >>> # Analyze current work
    >>> style = imagination.tag_style_elements("canvas.png")
    >>> print(f"Current style: {style.line_style}, {style.contrast_level}")
    >>> 
    >>> # Generate reference for inspiration
    >>> params = GenerationParams(strength=0.7, style_prompt="impressionist")
    >>> suggestion = imagination.generate_stylized_reference("canvas.png", params)
    >>> 
    >>> # Examine transferable elements
    >>> print(f"Can transfer: {suggestion.transferable_elements}")
    >>> 
    >>> # Get alternative suggestions
    >>> alternatives = imagination.suggest_alternative_style("canvas.png", n_suggestions=3)
    >>> for alt in alternatives:
    ...     print(f"Try: {alt.name}")
"""

from imagination.imagination_module import ImaginationModule
from imagination.core import StyleAnalyzer, ReferenceGenerator
from imagination.models import (
    StyleFeature,
    LineStyle,
    ContrastLevel,
    ColorPalette,
    BrushworkAnalysis,
    LightingAnalysis,
    FormExaggeration,
    StyleAnalysis,
    StyleSuggestion,
    GenerationParams,
)

__version__ = "0.1.0"

__all__ = [
    "ImaginationModule",
    "StyleAnalyzer",
    "ReferenceGenerator",
    "StyleFeature",
    "LineStyle",
    "ContrastLevel",
    "ColorPalette",
    "BrushworkAnalysis",
    "LightingAnalysis",
    "FormExaggeration",
    "StyleAnalysis",
    "StyleSuggestion",
    "GenerationParams",
]
