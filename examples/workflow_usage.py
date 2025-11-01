"""
Example demonstrating the complete Artistic Workflow Pipeline.

This example shows how to use the Workflow system to simulate a complete
iterative drawing process from rough sketch to refined artwork.
"""

from motor.core.canvas import Canvas
from motor.core.stroke import Stroke, StrokePoint
from workflow.core.workflow_executor import WorkflowExecutor
from workflow.models.drawing_phase import DrawingPhase
from workflow.models.stroke_intent import StrokeIntent, StrokeIntentHelper


def create_example_stroke(start_x, start_y, end_x, end_y, num_points=10):
    """Create an example stroke between two points."""
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        x = start_x + t * (end_x - start_x)
        y = start_y + t * (end_y - start_y)
        pressure = 0.5 + 0.5 * abs(0.5 - t) * 2  # Vary pressure
        points.append(StrokePoint(x=x, y=y, pressure=pressure))
    return Stroke(points=points)


def simulate_sketch_phase(executor):
    """Simulate the sketch/block-in phase."""
    print("\n=== SKETCH PHASE ===")
    print("Quick gesture strokes for initial layout and proportions...")
    
    # Gesture strokes for rough figure
    strokes = [
        (100, 200, 150, 400),  # Center line
        (50, 250, 200, 250),   # Shoulder line
        (100, 400, 80, 550),   # Left leg
        (100, 400, 120, 550),  # Right leg
    ]
    
    for start_x, start_y, end_x, end_y in strokes:
        stroke = create_example_stroke(start_x, start_y, end_x, end_y)
        executor.execute_stroke(
            stroke,
            intent=StrokeIntent.GESTURE,
            purpose="Rough gesture for initial proportions",
        )
    
    print(f"Executed {len(strokes)} gesture strokes")
    print(f"Total strokes: {executor.workflow_state.total_strokes}")


def simulate_refinement_phase(executor):
    """Simulate the refinement phase."""
    print("\n=== REFINEMENT PHASE ===")
    print("Contour strokes for anatomy and structure...")
    
    # Transition to refinement
    executor.transition_to_phase(
        DrawingPhase.REFINEMENT,
        reason="Sketch phase complete, proportions established",
    )
    
    # Contour strokes for structure
    strokes = [
        (120, 220, 150, 250),  # Head outline
        (60, 250, 90, 320),    # Left arm
        (160, 250, 190, 320),  # Right arm
        (90, 350, 110, 400),   # Torso definition
    ]
    
    for start_x, start_y, end_x, end_y in strokes:
        stroke = create_example_stroke(start_x, start_y, end_x, end_y, num_points=15)
        executor.execute_stroke(
            stroke,
            intent=StrokeIntent.CONTOUR,
            purpose="Define anatomical structure",
        )
    
    print(f"Executed {len(strokes)} contour strokes")
    print(f"Total strokes: {executor.workflow_state.total_strokes}")


def simulate_stylization_phase(executor):
    """Simulate the stylization phase."""
    print("\n=== STYLIZATION PHASE ===")
    print("Clean line work and expressive strokes...")
    
    # Transition to stylization
    executor.transition_to_phase(
        DrawingPhase.STYLIZATION,
        reason="Structure refined, ready for line work",
    )
    
    # Detail and cleanup strokes
    detail_strokes = [
        (125, 225, 128, 230),  # Eye detail
        (142, 225, 145, 230),  # Eye detail
        (135, 240, 135, 245),  # Nose
    ]
    
    for start_x, start_y, end_x, end_y in detail_strokes:
        stroke = create_example_stroke(start_x, start_y, end_x, end_y, num_points=8)
        executor.execute_stroke(
            stroke,
            intent=StrokeIntent.DETAIL,
            purpose="Add facial details",
        )
    
    print(f"Executed {len(detail_strokes)} detail strokes")
    print(f"Total strokes: {executor.workflow_state.total_strokes}")


def simulate_rendering_phase(executor):
    """Simulate the rendering phase."""
    print("\n=== RENDERING PHASE ===")
    print("Shading and final touches...")
    
    # Transition to rendering
    executor.transition_to_phase(
        DrawingPhase.RENDERING,
        reason="Line work complete, ready for rendering",
    )
    
    # Shading strokes
    shading_strokes = [
        (70, 280, 85, 310),    # Shadow on arm
        (95, 360, 105, 390),   # Shadow on torso
    ]
    
    for start_x, start_y, end_x, end_y in shading_strokes:
        stroke = create_example_stroke(start_x, start_y, end_x, end_y, num_points=20)
        executor.execute_stroke(
            stroke,
            intent=StrokeIntent.SHADING,
            purpose="Add shading and depth",
        )
    
    print(f"Executed {len(shading_strokes)} shading strokes")
    print(f"Total strokes: {executor.workflow_state.total_strokes}")


def demonstrate_checkpoint_rollback(executor):
    """Demonstrate checkpoint and rollback functionality."""
    print("\n=== CHECKPOINT & ROLLBACK DEMO ===")
    
    # Get current state
    current_strokes = len(executor.stroke_history)
    current_phase = executor.workflow_state.current_phase
    
    print(f"Current state: {current_strokes} strokes, phase: {current_phase.value}")
    
    # Create manual checkpoint
    checkpoint_id = executor.create_checkpoint(
        description="Before experimenting with new strokes"
    )
    print(f"Created checkpoint: {checkpoint_id}")
    
    # Add experimental strokes
    for _ in range(3):
        stroke = create_example_stroke(200, 200, 220, 220)
        executor.execute_stroke(stroke, purpose="Experimental stroke")
    
    print(f"After experiments: {len(executor.stroke_history)} strokes")
    
    # Rollback to checkpoint
    print("Rolling back to checkpoint...")
    executor.rollback_to_checkpoint(checkpoint_id)
    
    print(f"After rollback: {len(executor.stroke_history)} strokes")
    print(f"Successfully reverted to checkpoint!")


def demonstrate_phase_regression(executor):
    """Demonstrate regression to earlier phase."""
    print("\n=== PHASE REGRESSION DEMO ===")
    
    print(f"Current phase: {executor.workflow_state.current_phase.value}")
    
    # Simulate poor quality requiring regression
    print("Detecting quality issues, regressing to refinement...")
    
    executor.transition_to_phase(
        DrawingPhase.REFINEMENT,
        reason="Quality issues detected in rendering, need to refine structure",
    )
    
    print(f"Regressed to phase: {executor.workflow_state.current_phase.value}")
    
    # Do some corrective strokes
    stroke = create_example_stroke(100, 300, 110, 350)
    executor.execute_stroke(
        stroke,
        intent=StrokeIntent.CONTOUR,
        purpose="Correcting structural issues",
    )
    
    print("Applied corrective strokes in refinement phase")


def print_workflow_summary(executor):
    """Print comprehensive workflow summary."""
    print("\n" + "=" * 60)
    print("WORKFLOW SUMMARY")
    print("=" * 60)
    
    summary = executor.get_workflow_summary()
    state_summary = summary["workflow_state"]
    
    print(f"\nWorkflow ID: {state_summary['workflow_id']}")
    print(f"Current Phase: {state_summary['current_phase']}")
    print(f"Is Complete: {state_summary['is_complete']}")
    print(f"Total Strokes: {summary['total_strokes']}")
    print(f"Total Checkpoints: {summary['checkpoint_count']}")
    print(f"Phase Transitions: {state_summary['total_transitions']}")
    
    # Stroke breakdown by intent
    print("\nStrokes by Intent:")
    for intent in StrokeIntent:
        count = executor.get_stroke_count_by_intent(intent)
        if count > 0:
            print(f"  {intent.value}: {count}")
    
    # Stroke breakdown by phase
    print("\nStrokes by Phase:")
    for phase in DrawingPhase:
        count = executor.get_phase_stroke_count(phase)
        if count > 0:
            print(f"  {phase.value}: {count}")
    
    # Decision log summary
    if executor.decision_logger:
        decision_summary = summary["decision_log"]
        print(f"\nDecision Log:")
        print(f"  Total phases logged: {decision_summary['total_phases']}")
        print(f"  Total decisions: {decision_summary['total_strokes']}")


def print_phase_history(executor):
    """Print phase transition history."""
    print("\n" + "=" * 60)
    print("PHASE TRANSITION HISTORY")
    print("=" * 60)
    
    for i, transition in enumerate(executor.workflow_state.phase_history, 1):
        print(f"\n{i}. {transition.from_phase.value} → {transition.to_phase.value}")
        print(f"   Reason: {transition.reason}")
        print(f"   Confidence: {transition.confidence}")
        if transition.metrics:
            print(f"   Metrics: {transition.metrics}")


def main():
    """Main example function."""
    print("=" * 60)
    print("ARTISTIC WORKFLOW PIPELINE EXAMPLE")
    print("=" * 60)
    print("\nThis example demonstrates a complete iterative drawing workflow")
    print("from rough sketch to refined artwork with checkpoints and rollback.")
    
    # Create canvas and workflow executor
    canvas = Canvas(width=800, height=600, name="Example Artwork")
    executor = WorkflowExecutor(
        canvas=canvas,
        max_checkpoints=10,
        enable_logging=True,
    )
    
    print(f"\nInitialized workflow on {canvas.width}x{canvas.height} canvas")
    print(f"Starting phase: {executor.get_current_phase().value}")
    
    # Simulate complete workflow
    simulate_sketch_phase(executor)
    
    # Create checkpoint after sketch
    executor.create_checkpoint(
        description="Sketch phase complete",
        metadata={"phase": "sketch", "milestone": True}
    )
    
    simulate_refinement_phase(executor)
    
    # Create checkpoint after refinement
    executor.create_checkpoint(
        description="Refinement phase complete",
        metadata={"phase": "refinement", "milestone": True}
    )
    
    simulate_stylization_phase(executor)
    simulate_rendering_phase(executor)
    
    # Demonstrate checkpoint/rollback
    demonstrate_checkpoint_rollback(executor)
    
    # Demonstrate phase regression
    demonstrate_phase_regression(executor)
    
    # Mark as complete
    executor.transition_to_phase(
        DrawingPhase.COMPLETE,
        reason="Artwork finished after corrections",
    )
    
    # Print summaries
    print_workflow_summary(executor)
    print_phase_history(executor)
    
    # Export workflow
    print("\n" + "=" * 60)
    print("EXPORTING WORKFLOW")
    print("=" * 60)
    
    workflow_data = executor.export_workflow()
    print(f"\nWorkflow exported successfully!")
    print(f"Export contains:")
    print(f"  - Canvas state: {workflow_data['canvas']['width']}x{workflow_data['canvas']['height']}")
    print(f"  - {len(workflow_data['stroke_history'])} strokes")
    print(f"  - {len(workflow_data['checkpoints'])} checkpoints")
    print(f"  - Complete decision log")
    
    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)
    print("\nThe workflow system successfully demonstrated:")
    print("  ✓ Phase-based workflow progression")
    print("  ✓ Stroke intent classification")
    print("  ✓ Checkpoint creation and rollback")
    print("  ✓ Phase regression for corrections")
    print("  ✓ Complete decision logging")
    print("  ✓ Workflow state tracking")
    print("  ✓ Full workflow export")


if __name__ == "__main__":
    main()
