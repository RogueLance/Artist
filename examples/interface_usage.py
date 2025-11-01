"""
Interface Usage Example.

Demonstrates the CLI interface for the Cerebrum system, showing how to:
- Start a session
- Set goals
- Submit references and sketches
- Analyze canvas with Vision
- Plan actions with Brain
- Execute tasks and evaluate results
- Control iterations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interface import CLIInterface, SessionConfig
from PIL import Image, ImageDraw
import numpy as np


def create_sample_sketch(path: Path, width: int = 400, height: int = 600):
    """Create a sample sketch for testing."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple stick figure
    # Head
    draw.ellipse([175, 50, 225, 100], outline='black', width=3)
    
    # Body
    draw.line([200, 100, 200, 300], fill='black', width=3)
    
    # Arms
    draw.line([200, 150, 140, 220], fill='black', width=3)  # Left arm
    draw.line([200, 150, 260, 220], fill='black', width=3)  # Right arm
    
    # Legs
    draw.line([200, 300, 150, 480], fill='black', width=3)  # Left leg
    draw.line([200, 300, 250, 480], fill='black', width=3)  # Right leg
    
    img.save(path)
    print(f"Sample sketch created: {path}")


def example_1_basic_usage():
    """Example 1: Basic interface usage."""
    print("=" * 70)
    print("Example 1: Basic Interface Usage")
    print("=" * 70)
    
    # Create configuration
    config = SessionConfig(
        canvas_width=400,
        canvas_height=600,
        max_iterations=5,
        auto_save=True,
        output_dir=Path("examples/output/interface_example1"),
        interactive=False  # Non-interactive for automated example
    )
    
    # Initialize interface
    print("\n1. Initializing CLI interface...")
    interface = CLIInterface(config)
    
    # Start session
    print("\n2. Starting session...")
    session_id = interface.start_session()
    print(f"✓ Session started: {session_id}")
    
    # Set goal
    print("\n3. Setting artistic goal...")
    interface.set_goal("Draw an accurate human figure")
    
    # Create blank canvas
    print("\n4. Creating blank canvas...")
    interface.create_blank_canvas()
    
    # Analyze canvas
    print("\n5. Analyzing canvas with Vision...")
    result = interface.analyze_canvas()
    
    # Display session summary
    print("\n6. Session summary:")
    interface.display_session_summary()
    
    # End session
    print("\n7. Ending session...")
    interface.end_session()
    
    print("\n✓ Example 1 complete!")


def example_2_with_sketch():
    """Example 2: Interface with sketch submission."""
    print("\n" + "=" * 70)
    print("Example 2: Interface with Sketch Submission")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("examples/output/interface_example2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample sketch
    sketch_path = output_dir / "sample_sketch.png"
    create_sample_sketch(sketch_path)
    
    # Create configuration
    config = SessionConfig(
        canvas_width=400,
        canvas_height=600,
        max_iterations=5,
        output_dir=output_dir,
        interactive=False
    )
    
    # Initialize and start session
    print("\n1. Starting session...")
    interface = CLIInterface(config)
    session_id = interface.start_session()
    
    # Set goal
    print("\n2. Setting goal...")
    interface.set_goal("Improve figure proportions and add details")
    
    # Submit sketch
    print("\n3. Submitting sketch...")
    interface.submit_sketch(sketch_path)
    
    # Analyze canvas
    print("\n4. Analyzing canvas...")
    interface.analyze_canvas()
    
    # Plan next action
    print("\n5. Planning next action with Brain...")
    tasks = interface.plan_next_action()
    
    if tasks:
        print(f"✓ Created {len(tasks)} tasks")
    else:
        print("No tasks created")
    
    # Display summary and end
    interface.display_session_summary()
    interface.end_session()
    
    print("\n✓ Example 2 complete!")


def example_3_with_reference():
    """Example 3: Interface with reference comparison."""
    print("\n" + "=" * 70)
    print("Example 3: Interface with Reference Comparison")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("examples/output/interface_example3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample sketch and reference
    sketch_path = output_dir / "sketch.png"
    reference_path = output_dir / "reference.png"
    
    create_sample_sketch(sketch_path, 400, 600)
    create_sample_sketch(reference_path, 400, 600)
    
    # Create configuration
    config = SessionConfig(
        canvas_width=400,
        canvas_height=600,
        output_dir=output_dir,
        interactive=False
    )
    
    # Initialize
    print("\n1. Starting session...")
    interface = CLIInterface(config)
    interface.start_session()
    
    # Set goal
    print("\n2. Setting goal...")
    interface.set_goal("Match reference pose and proportions")
    
    # Submit sketch and reference
    print("\n3. Submitting sketch and reference...")
    interface.submit_sketch(sketch_path)
    interface.submit_reference(reference_path)
    
    # Analyze and compare
    print("\n4. Analyzing canvas...")
    interface.analyze_canvas()
    
    print("\n5. Comparing to reference...")
    interface.compare_to_reference()
    
    # Display summary and end
    interface.display_session_summary()
    interface.end_session()
    
    print("\n✓ Example 3 complete!")


def example_4_iteration_loop():
    """Example 4: Running iteration loop."""
    print("\n" + "=" * 70)
    print("Example 4: Iteration Loop")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("examples/output/interface_example4")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample sketch
    sketch_path = output_dir / "initial_sketch.png"
    create_sample_sketch(sketch_path)
    
    # Create configuration
    config = SessionConfig(
        canvas_width=400,
        canvas_height=600,
        max_iterations=3,
        output_dir=output_dir,
        interactive=False
    )
    
    # Initialize
    print("\n1. Starting session...")
    interface = CLIInterface(config)
    interface.start_session()
    
    # Set goal
    print("\n2. Setting goal...")
    interface.set_goal("Create well-proportioned figure with refinements")
    
    # Submit sketch
    print("\n3. Submitting initial sketch...")
    interface.submit_sketch(sketch_path)
    
    # Run single iteration
    print("\n4. Running single iteration...")
    interface.run_iteration(auto_approve=True)
    
    # Run batch iterations
    print("\n5. Running batch iterations (2 more)...")
    interface.run_batch_iterations(2, auto_approve=True)
    
    # Display final summary
    print("\n6. Final summary:")
    interface.display_session_summary()
    
    interface.end_session()
    
    print("\n✓ Example 4 complete!")


def example_5_full_workflow():
    """Example 5: Complete workflow demonstration."""
    print("\n" + "=" * 70)
    print("Example 5: Full Workflow")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("examples/output/interface_example5")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample files
    sketch_path = output_dir / "sketch.png"
    reference_path = output_dir / "reference.png"
    
    create_sample_sketch(sketch_path, 400, 600)
    create_sample_sketch(reference_path, 400, 600)
    
    # Create configuration
    config = SessionConfig(
        canvas_width=400,
        canvas_height=600,
        max_iterations=3,
        output_dir=output_dir,
        interactive=False,
        enable_vision=True,
        enable_brain=True
    )
    
    # Start session
    print("\n1. Starting full workflow session...")
    interface = CLIInterface(config)
    session_id = interface.start_session()
    print(f"✓ Session: {session_id}")
    
    # Set goal
    print("\n2. Setting artistic goal...")
    interface.set_goal("Draw stylized female portrait with accurate proportions")
    
    # Submit inputs
    print("\n3. Submitting inputs...")
    interface.submit_sketch(sketch_path)
    interface.submit_reference(reference_path)
    
    # Initial analysis
    print("\n4. Initial analysis...")
    interface.analyze_canvas()
    interface.compare_to_reference()
    
    # Run iterations
    print("\n5. Running refinement iterations...")
    completed = interface.run_batch_iterations(3, auto_approve=True)
    print(f"✓ Completed {completed} iterations")
    
    # Final analysis
    print("\n6. Final analysis...")
    interface.analyze_canvas()
    interface.compare_to_reference()
    
    # Display summary
    print("\n7. Complete workflow summary:")
    interface.display_session_summary()
    
    # End session
    interface.end_session()
    
    print("\n✓ Example 5 complete!")
    print(f"\nCheck output directory for results: {output_dir}")


def main():
    """Run all examples."""
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Interface System - Usage Examples" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Run examples
        example_1_basic_usage()
        example_2_with_sketch()
        example_3_with_reference()
        example_4_iteration_loop()
        example_5_full_workflow()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
