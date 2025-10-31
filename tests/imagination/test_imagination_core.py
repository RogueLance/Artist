"""Tests for Imagination System core functionality."""

import pytest
import numpy as np
from PIL import Image
import tempfile
from pathlib import Path

from imagination import (
    ImaginationModule,
    StyleAnalyzer,
    ReferenceGenerator,
    GenerationParams,
    StyleAnalysis,
    StyleSuggestion,
    LineStyle,
    ContrastLevel,
    ColorPalette,
    BrushworkAnalysis,
)


class TestStyleAnalyzer:
    """Test StyleAnalyzer class."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = StyleAnalyzer()
        assert analyzer is not None
    
    def test_analyze_numpy_array(self):
        """Test analyzing a numpy array image."""
        # Create test image
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        analyzer = StyleAnalyzer()
        result = analyzer.analyze(img)
        
        assert isinstance(result, StyleAnalysis)
        assert result.line_style is not None
        assert result.contrast_level is not None
    
    def test_analyze_with_color_palette(self):
        """Test color palette extraction."""
        # Create image with distinct colors
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:50, :] = [255, 0, 0]  # Red top half
        img[50:, :] = [0, 0, 255]  # Blue bottom half
        
        analyzer = StyleAnalyzer()
        result = analyzer.analyze(img, analyze_colors=True)
        
        assert result.color_palette is not None
        assert isinstance(result.color_palette, ColorPalette)
        assert len(result.color_palette.dominant_colors) > 0
        assert len(result.color_palette.color_weights) > 0
        assert 0 <= result.color_palette.temperature <= 1
        assert 0 <= result.color_palette.saturation <= 1
    
    def test_analyze_brushwork(self):
        """Test brushwork analysis."""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        analyzer = StyleAnalyzer()
        result = analyzer.analyze(img, analyze_brushwork=True)
        
        assert result.brushwork is not None
        assert isinstance(result.brushwork, BrushworkAnalysis)
        assert 0 <= result.brushwork.stroke_visibility <= 1
        assert 0 <= result.brushwork.texture_intensity <= 1
        assert 0 <= result.brushwork.edge_softness <= 1
    
    def test_analyze_lighting(self):
        """Test lighting analysis."""
        # Create image with gradient (simulating lighting)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            img[i, :] = int(255 * i / 100)
        
        analyzer = StyleAnalyzer()
        result = analyzer.analyze(img, analyze_lighting=True)
        
        assert result.lighting is not None
        assert 0 <= result.lighting.intensity <= 1
        assert result.lighting.contrast_ratio > 0
        assert 0 <= result.lighting.ambient_level <= 1
    
    def test_line_style_detection(self):
        """Test line style detection."""
        # Create image with clear edges
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[10:20, :] = 255  # Horizontal line
        img[:, 50:60] = 255  # Vertical line
        
        analyzer = StyleAnalyzer()
        result = analyzer.analyze(img)
        
        assert result.line_style in [
            LineStyle.SMOOTH,
            LineStyle.SKETCHY,
            LineStyle.ANGULAR,
            LineStyle.FLOWING,
            LineStyle.BROKEN,
            LineStyle.HATCHED,
        ]
    
    def test_contrast_detection(self):
        """Test contrast level detection."""
        # High contrast image
        high_contrast = np.zeros((100, 100, 3), dtype=np.uint8)
        high_contrast[:50, :] = 0
        high_contrast[50:, :] = 255
        
        analyzer = StyleAnalyzer()
        result = analyzer.analyze(high_contrast)
        
        assert result.contrast_level in [
            ContrastLevel.LOW,
            ContrastLevel.MEDIUM,
            ContrastLevel.HIGH,
            ContrastLevel.DRAMATIC,
        ]
    
    def test_load_from_file(self):
        """Test loading image from file."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filepath = f.name
        
        try:
            # Create and save test image
            img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
            pil_img = Image.fromarray(img)
            pil_img.save(filepath)
            
            analyzer = StyleAnalyzer()
            result = analyzer.analyze(filepath)
            
            assert isinstance(result, StyleAnalysis)
            assert result.line_style is not None
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_compare_styles(self):
        """Test style comparison."""
        # Create two similar images
        img1 = np.ones((50, 50, 3), dtype=np.uint8) * 128
        img2 = np.ones((50, 50, 3), dtype=np.uint8) * 130
        
        analyzer = StyleAnalyzer()
        style1 = analyzer.analyze(img1, analyze_colors=True, analyze_brushwork=True)
        style2 = analyzer.analyze(img2, analyze_colors=True, analyze_brushwork=True)
        
        similarity = analyzer.compare_styles(style1, style2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Should be similar


class TestReferenceGenerator:
    """Test ReferenceGenerator class."""
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = ReferenceGenerator(simulation_mode=True)
        assert generator is not None
        assert generator.simulation_mode is True
    
    def test_generate_stylized_reference(self):
        """Test generating stylized reference."""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        params = GenerationParams(strength=0.5, style_prompt="test style")
        
        generator = ReferenceGenerator(simulation_mode=True)
        suggestion = generator.generate_stylized_reference(img, params)
        
        assert isinstance(suggestion, StyleSuggestion)
        assert suggestion.reference_image is not None
        assert suggestion.reference_image.shape == img.shape
        assert len(suggestion.transferable_elements) > 0
    
    def test_generate_with_different_strengths(self):
        """Test generation with different strength values."""
        img = np.ones((50, 50, 3), dtype=np.uint8) * 128
        generator = ReferenceGenerator(simulation_mode=True)
        
        # Test various strengths
        for strength in [0.3, 0.5, 0.7, 0.9]:
            params = GenerationParams(strength=strength)
            suggestion = generator.generate_stylized_reference(img, params)
            
            assert suggestion.reference_image is not None
            assert suggestion.reference_image.shape == img.shape
    
    def test_generate_with_mask(self):
        """Test masked generation."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        mask = np.zeros((100, 100), dtype=np.float32)
        mask[25:75, 25:75] = 1.0  # Mask center region
        
        params = GenerationParams(strength=0.7)
        generator = ReferenceGenerator(simulation_mode=True)
        
        result = generator.generate_with_mask(img, mask, params)
        
        assert result is not None
        assert result.shape == img.shape
    
    def test_suggest_alternative_styles(self):
        """Test suggesting multiple style alternatives."""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        generator = ReferenceGenerator(simulation_mode=True)
        suggestions = generator.suggest_alternative_styles(img, n_suggestions=3)
        
        assert len(suggestions) == 3
        for suggestion in suggestions:
            assert isinstance(suggestion, StyleSuggestion)
            assert suggestion.reference_image is not None
            assert len(suggestion.name) > 0
    
    def test_generation_with_style_target(self):
        """Test generation with target style."""
        img = np.ones((50, 50, 3), dtype=np.uint8) * 128
        
        # Create target style
        analyzer = StyleAnalyzer()
        target_style = analyzer.analyze(img, analyze_colors=True, analyze_brushwork=True)
        
        params = GenerationParams(strength=0.6, style_prompt="target style")
        generator = ReferenceGenerator(simulation_mode=True)
        
        suggestion = generator.generate_stylized_reference(img, params, target_style)
        
        assert suggestion is not None
        assert len(suggestion.features) > 0


class TestImaginationModule:
    """Test ImaginationModule main API."""
    
    def test_initialization(self):
        """Test module initialization."""
        module = ImaginationModule(simulation_mode=True)
        assert module is not None
        assert module.analyzer is not None
        assert module.generator is not None
    
    def test_tag_style_elements(self):
        """Test tagging style elements."""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        module = ImaginationModule()
        style = module.tag_style_elements(img)
        
        assert isinstance(style, StyleAnalysis)
        assert style.line_style is not None
        assert style.contrast_level is not None
        assert len(style.get_features()) > 0
    
    def test_generate_stylized_reference(self):
        """Test generating stylized reference."""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        params = GenerationParams(
            strength=0.7,
            style_prompt="impressionist painting",
            guidance_scale=7.5
        )
        
        module = ImaginationModule()
        suggestion = module.generate_stylized_reference(img, params)
        
        assert isinstance(suggestion, StyleSuggestion)
        assert suggestion.reference_image is not None
        assert len(suggestion.transferable_elements) > 0
        assert suggestion.confidence > 0
    
    def test_suggest_alternative_style(self):
        """Test suggesting alternative styles."""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        module = ImaginationModule()
        suggestions = module.suggest_alternative_style(img, n_suggestions=3)
        
        assert len(suggestions) == 3
        for suggestion in suggestions:
            assert isinstance(suggestion, StyleSuggestion)
            assert suggestion.name is not None
            assert len(suggestion.transferable_elements) > 0
    
    def test_generate_with_mask(self):
        """Test masked generation."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        mask = np.zeros((100, 100), dtype=np.float32)
        mask[40:60, 40:60] = 1.0
        
        params = GenerationParams(strength=0.8, style_prompt="watercolor")
        
        module = ImaginationModule()
        result = module.generate_with_mask(img, mask, params)
        
        assert result is not None
        assert result.shape == img.shape
    
    def test_compare_styles(self):
        """Test style comparison."""
        img1 = np.ones((50, 50, 3), dtype=np.uint8) * 100
        img2 = np.ones((50, 50, 3), dtype=np.uint8) * 110
        
        module = ImaginationModule()
        similarity = module.compare_styles(img1, img2)
        
        assert 0 <= similarity <= 1
    
    def test_extract_transferable_elements(self):
        """Test extracting transferable elements."""
        reference = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        canvas = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        module = ImaginationModule()
        elements = module.extract_transferable_elements(reference, canvas)
        
        assert isinstance(elements, dict)
        # Elements may be empty if images are too similar
        for key, value in elements.items():
            assert isinstance(value, dict)
            assert 'confidence' in value
    
    def test_close(self):
        """Test module cleanup."""
        module = ImaginationModule()
        module.close()  # Should not raise error


class TestGenerationParams:
    """Test GenerationParams data structure."""
    
    def test_default_params(self):
        """Test default parameter values."""
        params = GenerationParams()
        
        assert params.strength == 0.75
        assert params.guidance_scale == 7.5
        assert params.steps == 50
        assert params.seed is None
        assert params.mask_region is None
        assert params.style_prompt == ""
    
    def test_custom_params(self):
        """Test custom parameter values."""
        params = GenerationParams(
            strength=0.8,
            guidance_scale=10.0,
            steps=30,
            seed=42,
            mask_region=(10, 20, 50, 60),
            style_prompt="oil painting"
        )
        
        assert params.strength == 0.8
        assert params.guidance_scale == 10.0
        assert params.steps == 30
        assert params.seed == 42
        assert params.mask_region == (10, 20, 50, 60)
        assert params.style_prompt == "oil painting"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        params = GenerationParams(
            strength=0.6,
            style_prompt="sketch"
        )
        
        params_dict = params.to_dict()
        
        assert isinstance(params_dict, dict)
        assert params_dict['strength'] == 0.6
        assert params_dict['style_prompt'] == "sketch"


class TestStyleAnalysis:
    """Test StyleAnalysis data structure."""
    
    def test_get_features(self):
        """Test getting list of features."""
        analysis = StyleAnalysis()
        
        # Empty analysis
        assert len(analysis.get_features()) == 0
        
        # Add features
        analysis.line_style = LineStyle.SMOOTH
        analysis.contrast_level = ContrastLevel.HIGH
        analysis.color_palette = ColorPalette()
        
        features = analysis.get_features()
        assert len(features) >= 3
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        analysis = StyleAnalysis()
        analysis.line_style = LineStyle.ANGULAR
        analysis.contrast_level = ContrastLevel.DRAMATIC
        analysis.confidence = 0.9
        
        result_dict = analysis.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['line_style'] == 'angular'
        assert result_dict['contrast_level'] == 'dramatic'
        assert result_dict['confidence'] == 0.9


class TestIntegration:
    """Integration tests for the full workflow."""
    
    def test_full_workflow(self):
        """Test complete imagination workflow."""
        # Create test canvas
        canvas = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Initialize module
        imagination = ImaginationModule()
        
        # 1. Analyze current style
        current_style = imagination.tag_style_elements(canvas)
        assert current_style is not None
        
        # 2. Generate reference with target style
        params = GenerationParams(strength=0.7, style_prompt="watercolor")
        suggestion = imagination.generate_stylized_reference(canvas, params, current_style)
        assert suggestion.reference_image is not None
        
        # 3. Get alternative suggestions
        alternatives = imagination.suggest_alternative_style(canvas, current_style, n_suggestions=2)
        assert len(alternatives) == 2
        
        # 4. Extract transferable elements
        elements = imagination.extract_transferable_elements(
            suggestion.reference_image,
            canvas
        )
        assert isinstance(elements, dict)
        
        # 5. Compare styles
        similarity = imagination.compare_styles(canvas, suggestion.reference_image)
        assert 0 <= similarity <= 1
        
        # Cleanup
        imagination.close()
    
    def test_workflow_with_file_io(self):
        """Test workflow with file I/O."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create and save test image
            img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            img_path = tmppath / "test.png"
            Image.fromarray(img).save(img_path)
            
            # Run analysis
            imagination = ImaginationModule()
            style = imagination.tag_style_elements(str(img_path))
            
            assert style is not None
            assert style.line_style is not None
            
            imagination.close()
