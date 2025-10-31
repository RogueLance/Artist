"""
End-to-End Workflow Example.

Demonstrates complete art generation workflow using pipelines,
recording, and failure logging.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image, ImageDraw

from cerebrum.pipelines import PhotoReferencePipeline, SketchCorrectionPipeline, AIImagePipeline
from cerebrum.recording import SessionRecorder, TimelapseGenerator
from cerebrum.logging import FailureLogger, FailureSeverity


def create_sample_reference(width=800, height=1000):
    """Create a sample reference image."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a figure
    # Head
    draw.ellipse([350, 100, 450, 200], outline='black', fill='lightgray', width=3)
    
    # Body
    draw.rectangle([360, 200, 440, 500], outline='black', fill='gray', width=3)
    
    # Arms
    draw.rectangle([240, 250, 360, 280], outline='black', fill='gray', width=3)
    draw.rectangle([440, 250, 560, 280], outline='black', fill='gray', width=3)
    
    # Legs
    draw.rectangle([360, 500, 390, 800], outline='black', fill='darkgray', width=3)
    draw.rectangle([410, 500, 440, 800], outline='black', fill='darkgray', width=3)
    
    return np.array(img)


def example_photo_pipeline():
    """Example 1: Photo reference to stylized art."""
    print("=" * 70)
    print("Example 1: Photo Reference Pipeline")
    print("=" * 70)
    
    # Create sample reference
    print("\n1. Creating reference image...")
    reference = create_sample_reference()
    print("✓ Reference created")
    
    # Setup recording
    print("\n2. Setting up session recording...")
    recorder = SessionRecorder(session_name="photo_pipeline_example")
    recorder.start()
    print("✓ Recording started")
    
    # Setup failure logging
    failure_logger = FailureLogger(session_name="photo_pipeline_example")
    
    # Create and execute pipeline
    print("\n3. Creating pipeline...")
    pipeline = PhotoReferencePipeline(
        motor_backend="simulation",
        canvas_width=800,
        canvas_height=1000,
        max_iterations=3,
        quality_threshold=0.7
    )
    print("✓ Pipeline created")
    
    print("\n4. Executing pipeline...")
    try:
        result = pipeline.execute(
            reference_image=reference,
            goal="Create stylized artwork from reference"
        )
        
        print(f"\n✓ Pipeline completed in {result.total_duration:.2f}s")
        print(f"  - Stages executed: {len(result.stages)}")
        print(f"  - Success: {result.success}")
        
        # Record final snapshot
        if result.final_canvas is not None:
            recorder.record_snapshot(
                canvas_data=result.final_canvas,
                stage="final",
                metrics=result.metrics,
                notes="Pipeline completed"
            )
        
        # Display stage results
        print("\n5. Stage Results:")
        for stage_result in result.stages:
            status = "✓" if stage_result.success else "✗"
            print(f"  {status} {stage_result.stage.value}: {stage_result.duration:.2f}s")
        
        # Display metrics
        print("\n6. Metrics:")
        for key, value in result.metrics.items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        failure_logger.log_pipeline_failure(
            description=str(e),
            severity=FailureSeverity.CRITICAL
        )
    
    finally:
        recorder.stop()
    
    # Save recording
    print("\n7. Saving outputs...")
    output_dir = Path("/tmp/cerebrum_examples/photo_pipeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    recorder.save(output_dir)
    failure_logger.save(output_dir)
    
    # Generate timelapse
    if recorder.snapshots:
        print("\n8. Generating visualizations...")
        generator = TimelapseGenerator(recorder)
        
        # Save grid
        generator.generate_image_grid(
            output_dir / "progress_grid.png",
            cols=3
        )
        print(f"✓ Progress grid saved")
        
        # Save GIF
        generator.generate_gif(
            output_dir / "timelapse.gif",
            fps=1
        )
        print(f"✓ Timelapse GIF saved")
    
    print(f"\n✓ All outputs saved to {output_dir}")
    
    # Display summary
    print("\n9. Recording Summary:")
    summary = recorder.get_summary()
    for key, value in summary.items():
        print(f"  - {key}: {value}")
    
    print("\n" + "=" * 70)


def example_sketch_correction():
    """Example 2: Sketch correction workflow."""
    print("\n\n" + "=" * 70)
    print("Example 2: Sketch Correction Pipeline")
    print("=" * 70)
    
    # Create rough sketch
    print("\n1. Creating rough sketch...")
    img = Image.new('RGB', (800, 1000), 'white')
    draw = ImageDraw.Draw(img)
    
    # Intentionally rough and uneven
    draw.ellipse([320, 80, 480, 240], outline='black', width=5)  # Large head
    draw.line([400, 240, 400, 500], fill='black', width=5)  # Short body
    draw.line([400, 300, 280, 450], fill='black', width=5)  # Left arm
    draw.line([400, 300, 520, 480], fill='black', width=5)  # Right arm (longer)
    draw.line([400, 500, 340, 850], fill='black', width=5)  # Left leg
    draw.line([400, 500, 460, 850], fill='black', width=5)  # Right leg
    
    sketch = np.array(img)
    print("✓ Rough sketch created")
    
    # Create pipeline
    print("\n2. Creating sketch correction pipeline...")
    pipeline = SketchCorrectionPipeline(
        motor_backend="simulation",
        canvas_width=800,
        canvas_height=1000,
        max_iterations=3
    )
    
    # Execute
    print("\n3. Executing correction...")
    result = pipeline.execute(reference_image=sketch)
    
    print(f"\n✓ Correction completed in {result.total_duration:.2f}s")
    
    # Find structure stage
    from cerebrum.pipelines import PipelineStage
    structure_result = result.get_stage_result(PipelineStage.STRUCTURE)
    
    if structure_result and structure_result.metrics:
        corrections = structure_result.metrics.get('corrections_made', 0)
        print(f"  - Structural corrections applied: {corrections}")
    
    print("\n" + "=" * 70)


def example_ai_correction():
    """Example 3: AI image correction workflow."""
    print("\n\n" + "=" * 70)
    print("Example 3: AI Image Correction Pipeline")
    print("=" * 70)
    
    # Create AI-style image with issues
    print("\n1. Creating AI-generated image...")
    img = Image.new('RGB', (800, 1000), 'white')
    draw = ImageDraw.Draw(img)
    
    # Stylized but with typical AI issues
    draw.ellipse([340, 90, 460, 210], outline='black', fill='peachpuff', width=3)
    draw.rectangle([350, 210, 450, 560], outline='black', fill='lightblue', width=3)
    
    # Malformed hands
    draw.ellipse([200, 360, 280, 440], outline='black', fill='peachpuff', width=3)
    draw.ellipse([520, 360, 600, 440], outline='black', fill='peachpuff', width=3)
    
    # Legs
    draw.rectangle([350, 560, 390, 880], outline='black', fill='navy', width=3)
    draw.rectangle([410, 560, 450, 880], outline='black', fill='navy', width=3)
    
    ai_image = np.array(img)
    print("✓ AI image created")
    
    # Create pipeline
    print("\n2. Creating AI correction pipeline...")
    pipeline = AIImagePipeline(
        motor_backend="simulation",
        canvas_width=800,
        canvas_height=1000,
        max_iterations=3
    )
    
    # Execute
    print("\n3. Executing correction...")
    result = pipeline.execute(reference_image=ai_image)
    
    print(f"\n✓ Correction completed in {result.total_duration:.2f}s")
    
    # Show identified errors
    from cerebrum.pipelines import PipelineStage
    analysis_result = result.get_stage_result(PipelineStage.ANALYSIS)
    
    if analysis_result and analysis_result.metrics:
        errors = analysis_result.metrics.get('identified_errors', [])
        print(f"  - Errors identified: {len(errors)}")
        for error in errors:
            print(f"    • {error}")
    
    print("\n" + "=" * 70)


def example_failure_logging():
    """Example 4: Failure logging and analysis."""
    print("\n\n" + "=" * 70)
    print("Example 4: Failure Logging and Analysis")
    print("=" * 70)
    
    from cerebrum.logging import FailureComponent
    
    # Create logger
    print("\n1. Creating failure logger...")
    logger = FailureLogger(session_name="example_failures")
    print("✓ Logger created")
    
    # Simulate various failures
    print("\n2. Logging sample failures...")
    
    logger.log_motor_failure(
        description="Stroke execution timeout",
        severity=FailureSeverity.MEDIUM,
        stroke_id="stroke_123",
        timeout_seconds=5.0
    )
    
    logger.log_vision_failure(
        description="Pose detection failed - low confidence",
        severity=FailureSeverity.LOW,
        confidence=0.3,
        image_quality="poor"
    )
    
    logger.log_brain_failure(
        description="Task planning failed - no valid actions",
        severity=FailureSeverity.HIGH,
        task_id="task_456"
    )
    
    logger.log_integration_failure(
        description="Motor-Vision sync issue",
        severity=FailureSeverity.HIGH,
        component_a="motor",
        component_b="vision"
    )
    
    print("✓ Sample failures logged")
    
    # Generate report
    print("\n3. Failure Report:")
    print(logger.generate_report())
    
    # Get statistics
    print("\n4. Statistics by Component:")
    stats = logger.get_statistics()
    for component, count in stats["by_component"].items():
        print(f"  - {component}: {count}")
    
    # Save
    output_dir = Path("/tmp/cerebrum_examples/failures")
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.save(output_dir)
    print(f"\n✓ Failure log saved to {output_dir}")
    
    print("\n" + "=" * 70)


def main():
    """Run all examples."""
    print("\n╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Cerebrum End-to-End Examples" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        example_photo_pipeline()
        example_sketch_correction()
        example_ai_correction()
        example_failure_logging()
        
        print("\n\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print("\nOutputs saved to /tmp/cerebrum_examples/")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
