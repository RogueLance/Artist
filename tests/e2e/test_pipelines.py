"""
End-to-end pipeline tests.

Tests complete execution of all three pipeline types with real-world scenarios.
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

import pytest
import numpy as np
from PIL import Image, ImageDraw

from cerebrum.pipelines import (
    PhotoReferencePipeline,
    SketchCorrectionPipeline,
    AIImagePipeline,
    PipelineStage
)


def create_test_photo(width=400, height=600):
    """Create a test photo with a figure."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Complete figure
    draw.ellipse([175, 50, 225, 100], outline='black', fill='lightgray', width=2)
    draw.rectangle([180, 100, 220, 250], outline='black', fill='gray', width=2)
    draw.rectangle([120, 120, 180, 140], outline='black', fill='gray', width=2)
    draw.rectangle([220, 120, 280, 140], outline='black', fill='gray', width=2)
    draw.rectangle([180, 250, 200, 400], outline='black', fill='darkgray', width=2)
    draw.rectangle([200, 250, 220, 400], outline='black', fill='darkgray', width=2)
    
    return np.array(img)


def create_rough_sketch(width=400, height=600):
    """Create a rough sketch with proportion issues."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Rough sketch
    draw.ellipse([160, 40, 240, 120], outline='black', width=3)
    draw.line([200, 120, 200, 220], fill='black', width=3)
    draw.line([200, 140, 130, 200], fill='black', width=3)
    draw.line([200, 140, 270, 240], fill='black', width=3)
    draw.line([200, 220, 160, 380], fill='black', width=3)
    draw.line([200, 220, 240, 380], fill='black', width=3)
    
    return np.array(img)


def create_ai_image(width=400, height=600):
    """Create an AI-style image."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    draw.ellipse([170, 45, 230, 105], outline='black', fill='peachpuff', width=2)
    draw.rectangle([175, 105, 225, 280], outline='black', fill='lightblue', width=2)
    draw.ellipse([100, 180, 140, 220], outline='black', fill='peachpuff', width=2)
    draw.ellipse([260, 180, 300, 220], outline='black', fill='peachpuff', width=2)
    draw.rectangle([175, 280, 195, 450], outline='black', fill='navy', width=2)
    draw.rectangle([205, 280, 225, 450], outline='black', fill='navy', width=2)
    
    return np.array(img)


class TestPhotoPipeline:
    """Tests for photo reference pipeline."""
    
    def test_photo_pipeline_basic(self):
        """Test basic photo pipeline execution."""
        photo = create_test_photo(width=200, height=300)  # Smaller for speed
        
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1  # Reduced for speed
        )
        
        result = pipeline.execute(reference_image=photo)
        
        assert result is not None
        assert result.total_duration >= 0
        assert len(result.stages) > 0
        assert result.final_canvas is not None
    
    def test_photo_pipeline_stages(self):
        """Test that all expected stages are executed."""
        photo = create_test_photo(width=200, height=300)  # Smaller for speed
        
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1
        )
        
        result = pipeline.execute(reference_image=photo)
        
        stage_names = [s.stage.value for s in result.stages]
        
        # Key stages should be present
        assert "initialization" in stage_names
        assert "analysis" in stage_names
        assert "gesture" in stage_names
        assert "structure" in stage_names
        assert "completion" in stage_names
    
    def test_photo_pipeline_without_reference(self):
        """Test pipeline handles missing reference gracefully."""
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1
        )
        
        result = pipeline.execute(reference_image=None)
        
        # Should complete without error
        assert result is not None
        assert result.total_duration >= 0


class TestSketchPipeline:
    """Tests for sketch correction pipeline."""
    
    def test_sketch_pipeline_basic(self):
        """Test basic sketch pipeline execution."""
        sketch = create_rough_sketch(width=200, height=300)  # Smaller for speed
        
        pipeline = SketchCorrectionPipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1  # Reduced for speed
        )
        
        result = pipeline.execute(reference_image=sketch)
        
        assert result is not None
        assert result.total_duration >= 0
        assert len(result.stages) > 0
        assert result.final_canvas is not None
    
    def test_sketch_pipeline_corrections(self):
        """Test that sketch corrections are attempted."""
        sketch = create_rough_sketch(width=200, height=300)  # Smaller for speed
        
        pipeline = SketchCorrectionPipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1  # Reduced for speed
        )
        
        result = pipeline.execute(reference_image=sketch)
        
        # Find structure stage
        structure_result = result.get_stage_result(PipelineStage.STRUCTURE)
        
        if structure_result:
            # Should have attempted corrections
            assert structure_result.success


class TestAIPipeline:
    """Tests for AI image correction pipeline."""
    
    def test_ai_pipeline_basic(self):
        """Test basic AI pipeline execution."""
        ai_image = create_ai_image(width=200, height=300)  # Smaller for speed
        
        pipeline = AIImagePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1  # Reduced for speed
        )
        
        result = pipeline.execute(reference_image=ai_image)
        
        assert result is not None
        assert result.total_duration >= 0
        assert len(result.stages) > 0
        assert result.final_canvas is not None
    
    def test_ai_pipeline_error_detection(self):
        """Test that AI pipeline detects anatomical errors."""
        ai_image = create_ai_image(width=200, height=300)  # Smaller for speed
        
        pipeline = AIImagePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1  # Reduced for speed
        )
        
        result = pipeline.execute(reference_image=ai_image)
        
        # Analysis stage should identify issues
        analysis_result = result.get_stage_result(PipelineStage.ANALYSIS)
        
        if analysis_result:
            assert analysis_result.success
            # Should have identified some errors
            assert "identified_errors" in analysis_result.metrics or "error_count" in analysis_result.metrics


class TestPipelineMetrics:
    """Tests for pipeline metrics and reporting."""
    
    def test_pipeline_collects_metrics(self):
        """Test that pipelines collect metrics."""
        photo = create_test_photo(width=200, height=300)  # Smaller for speed
        
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1
        )
        
        result = pipeline.execute(reference_image=photo)
        
        assert result.metrics is not None
        assert "total_stages" in result.metrics
        assert "successful_stages" in result.metrics
    
    def test_stage_metrics(self):
        """Test that each stage has metrics."""
        photo = create_test_photo(width=200, height=300)  # Smaller for speed
        
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=200,
            canvas_height=300,
            max_iterations=1
        )
        
        result = pipeline.execute(reference_image=photo)
        
        for stage_result in result.stages:
            assert stage_result.duration >= 0
            assert stage_result.success is not None
            assert stage_result.stage is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
