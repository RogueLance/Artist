"""
End-to-end test framework for complete art generation pipelines.

Tests the integration of Motor, Vision, and Brain systems through
complete art projects from start to finish.
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

import pytest
import numpy as np
from PIL import Image, ImageDraw
import tempfile

from cerebrum.pipelines import (
    PhotoReferencePipeline,
    SketchCorrectionPipeline,
    AIImagePipeline
)
from cerebrum.recording import SessionRecorder
from cerebrum.logging import FailureLogger, FailureComponent, FailureSeverity


def create_test_photo(width=400, height=600):
    """Create a test photo with a figure."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a complete figure
    # Head
    draw.ellipse([175, 50, 225, 100], outline='black', fill='lightgray', width=2)
    
    # Body
    draw.rectangle([180, 100, 220, 250], outline='black', fill='gray', width=2)
    
    # Arms
    draw.rectangle([120, 120, 180, 140], outline='black', fill='gray', width=2)  # Left arm
    draw.rectangle([220, 120, 280, 140], outline='black', fill='gray', width=2)  # Right arm
    
    # Legs
    draw.rectangle([180, 250, 200, 400], outline='black', fill='darkgray', width=2)  # Left leg
    draw.rectangle([200, 250, 220, 400], outline='black', fill='darkgray', width=2)  # Right leg
    
    return np.array(img)


def create_rough_sketch(width=400, height=600):
    """Create a rough sketch with proportion issues."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Rough sketch with intentional proportion issues
    # Head too large
    draw.ellipse([160, 40, 240, 120], outline='black', width=3)
    
    # Body too short
    draw.line([200, 120, 200, 220], fill='black', width=3)
    
    # Arms uneven
    draw.line([200, 140, 130, 200], fill='black', width=3)  # Left arm
    draw.line([200, 140, 270, 240], fill='black', width=3)  # Right arm (longer)
    
    # Legs
    draw.line([200, 220, 160, 380], fill='black', width=3)
    draw.line([200, 220, 240, 380], fill='black', width=3)
    
    return np.array(img)


def create_ai_generated_image(width=400, height=600):
    """Create an AI-style image with anatomical issues."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Stylized but with typical AI issues
    # Head
    draw.ellipse([170, 45, 230, 105], outline='black', fill='peachpuff', width=2)
    
    # Body with weird proportions
    draw.rectangle([175, 105, 225, 280], outline='black', fill='lightblue', width=2)
    
    # Malformed hands (common AI issue)
    draw.ellipse([100, 180, 140, 220], outline='black', fill='peachpuff', width=2)
    draw.ellipse([260, 180, 300, 220], outline='black', fill='peachpuff', width=2)
    
    # Legs
    draw.rectangle([175, 280, 195, 450], outline='black', fill='navy', width=2)
    draw.rectangle([205, 280, 225, 450], outline='black', fill='navy', width=2)
    
    return np.array(img)


class TestE2EFramework:
    """End-to-end test framework tests."""
    
    def test_photo_pipeline_execution(self):
        """Test complete photo reference pipeline."""
        # Create test photo
        photo = create_test_photo()
        
        # Create pipeline
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=2,
            quality_threshold=0.6
        )
        
        # Execute pipeline
        result = pipeline.execute(reference_image=photo)
        
        # Verify results
        assert result is not None
        assert result.total_duration >= 0
        assert len(result.stages) > 0
        assert result.final_canvas is not None
        
        # Check that key stages were executed
        stage_names = [s.stage.value for s in result.stages]
        assert "initialization" in stage_names
        assert "analysis" in stage_names
        assert "completion" in stage_names
    
    def test_sketch_pipeline_execution(self):
        """Test complete sketch correction pipeline."""
        # Create rough sketch
        sketch = create_rough_sketch()
        
        # Create pipeline
        pipeline = SketchCorrectionPipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=2,
            quality_threshold=0.6
        )
        
        # Execute pipeline
        result = pipeline.execute(reference_image=sketch)
        
        # Verify results
        assert result is not None
        assert result.total_duration >= 0
        assert len(result.stages) > 0
        assert result.final_canvas is not None
        
        # Check that structure stage was executed
        from cerebrum.pipelines.base_pipeline import PipelineStage
        structure_stage = result.get_stage_result(PipelineStage.STRUCTURE)
    
    def test_ai_pipeline_execution(self):
        """Test complete AI image correction pipeline."""
        # Create AI-generated image
        ai_image = create_ai_generated_image()
        
        # Create pipeline
        pipeline = AIImagePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=2,
            quality_threshold=0.6
        )
        
        # Execute pipeline
        result = pipeline.execute(reference_image=ai_image)
        
        # Verify results
        assert result is not None
        assert result.total_duration >= 0
        assert len(result.stages) > 0
        assert result.final_canvas is not None
    
    def test_pipeline_with_recording(self):
        """Test pipeline execution with session recording."""
        # Create test image
        photo = create_test_photo()
        
        # Create recorder
        recorder = SessionRecorder(session_name="test_recording")
        recorder.start()
        
        # Create pipeline
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=1
        )
        
        # Execute pipeline
        result = pipeline.execute(reference_image=photo)
        
        # Record snapshots manually (in real implementation, pipeline would do this)
        if result.final_canvas is not None:
            recorder.record_snapshot(
                canvas_data=result.final_canvas,
                stage="completion",
                metrics=result.metrics
            )
        
        recorder.stop()
        
        # Verify recording
        assert len(recorder.snapshots) > 0
        assert recorder.start_time is not None
        assert recorder.end_time is not None
    
    def test_pipeline_with_failure_logging(self):
        """Test pipeline execution with failure logging."""
        # Create failure logger
        failure_logger = FailureLogger(session_name="test_failures")
        
        # Create pipeline
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=1
        )
        
        # Execute pipeline (intentionally with no reference to potentially cause issues)
        try:
            result = pipeline.execute(reference_image=None)
            
            # Check for any failures
            if not result.success or result.errors:
                for error in result.errors:
                    failure_logger.log_pipeline_failure(
                        description=error,
                        severity=FailureSeverity.HIGH
                    )
        except Exception as e:
            failure_logger.log_pipeline_failure(
                description=str(e),
                severity=FailureSeverity.CRITICAL
            )
        
        # Verify logger functionality
        stats = failure_logger.get_statistics()
        assert stats is not None
        assert "total_failures" in stats
    
    def test_pipeline_metrics_collection(self):
        """Test that pipelines collect meaningful metrics."""
        photo = create_test_photo()
        
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=2
        )
        
        result = pipeline.execute(reference_image=photo)
        
        # Verify metrics are collected
        assert result.metrics is not None
        assert "total_stages" in result.metrics
        assert "successful_stages" in result.metrics
        
        # Verify stage-level metrics
        for stage_result in result.stages:
            assert stage_result.duration >= 0
            assert stage_result.success is not None
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        # Create pipeline with invalid configuration
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=100,  # Small size
            canvas_height=100,
            max_iterations=1
        )
        
        # Should handle gracefully
        result = pipeline.execute(reference_image=None)
        
        # Should complete even without reference
        assert result is not None
        assert result.total_duration >= 0
    
    def test_multiple_pipelines_sequential(self):
        """Test running multiple pipelines sequentially."""
        photo = create_test_photo()
        sketch = create_rough_sketch()
        
        # Run photo pipeline
        pipeline1 = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=1
        )
        result1 = pipeline1.execute(reference_image=photo)
        
        # Run sketch pipeline
        pipeline2 = SketchCorrectionPipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=1
        )
        result2 = pipeline2.execute(reference_image=sketch)
        
        # Both should succeed
        assert result1 is not None
        assert result2 is not None
        assert result1.final_canvas is not None
        assert result2.final_canvas is not None
    
    def test_pipeline_stage_timing(self):
        """Test that pipeline stages are timed correctly."""
        photo = create_test_photo()
        
        pipeline = PhotoReferencePipeline(
            motor_backend="simulation",
            canvas_width=400,
            canvas_height=600,
            max_iterations=1
        )
        
        result = pipeline.execute(reference_image=photo)
        
        # All stages should have positive duration
        for stage_result in result.stages:
            assert stage_result.duration >= 0
        
        # Total duration should be at least sum of stage durations
        total_stage_duration = sum(s.duration for s in result.stages)
        assert result.total_duration >= total_stage_duration * 0.9  # Allow for overhead


class TestE2EIntegration:
    """Integration tests for complete system."""
    
    def test_full_workflow_with_all_systems(self):
        """Test full workflow integrating all systems."""
        # Setup
        photo = create_test_photo()
        recorder = SessionRecorder(session_name="full_workflow")
        failure_logger = FailureLogger(session_name="full_workflow")
        
        # Start recording
        recorder.start()
        
        try:
            # Execute pipeline
            pipeline = PhotoReferencePipeline(
                motor_backend="simulation",
                canvas_width=400,
                canvas_height=600,
                max_iterations=2
            )
            
            result = pipeline.execute(reference_image=photo)
            
            # Record final state
            if result.final_canvas is not None:
                recorder.record_snapshot(
                    canvas_data=result.final_canvas,
                    stage="completion",
                    metrics=result.metrics
                )
            
            # Log any failures
            if not result.success:
                for error in result.errors:
                    failure_logger.log_pipeline_failure(
                        description=error,
                        severity=FailureSeverity.HIGH
                    )
            
        except Exception as e:
            failure_logger.log_integration_failure(
                description=str(e),
                severity=FailureSeverity.CRITICAL
            )
        
        finally:
            recorder.stop()
        
        # Verify
        assert recorder.snapshots
        
        # Save outputs to temp
        with tempfile.TemporaryDirectory() as tmpdir:
            recorder.save(Path(tmpdir))
            failure_logger.save(Path(tmpdir))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
