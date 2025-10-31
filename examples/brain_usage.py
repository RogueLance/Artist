"""
Brain System Usage Example.

Demonstrates the Brain System capabilities:
- Setting goals
- Analyzing vision feedback
- Creating tasks
- Planning actions
- Executing with Motor System
- Evaluating results
- Iterative refinement
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain import BrainModule, TaskType, TaskPriority
from motor import MotorInterface, ToolPresets, Stroke, StrokePoint
from vision import VisionModule
import numpy as np
from PIL import Image, ImageDraw


def create_test_canvas(width=400, height=600):
    """Create a simple test canvas with a figure."""
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
    
    return np.array(img)


def example_1_basic_usage():
    """Example 1: Basic Brain System usage."""
    print("=" * 60)
    print("Example 1: Basic Brain System Usage")
    print("=" * 60)
    
    # Initialize Brain System
    print("\n1. Initializing Brain Module...")
    brain = BrainModule()
    print("✓ Brain Module initialized")
    
    # Set goal
    print("\n2. Setting artistic goal...")
    brain.set_goal("Draw an accurate human figure")
    print(f"✓ Goal set: {brain.get_goal()}")
    
    # Simulate vision feedback
    print("\n3. Analyzing vision feedback...")
    vision_data = {
        "has_pose": True,
        "pose_errors": [
            "Left arm proportions incorrect",
            "Hand details missing"
        ],
        "refinement_areas": [
            {"type": "hand", "region": {"x": 140, "y": 180, "width": 30, "height": 40}},
            {"type": "face", "region": {"x": 175, "y": 50, "width": 50, "height": 50}}
        ],
        "proportion_issues": True,
        "symmetry_issues": False,
        "proportion_score": 0.65,
        "symmetry_score": 0.82,
        "detection_confidence": 0.9
    }
    
    # Plan next actions
    tasks = brain.plan_next_action(vision_data)
    
    print(f"✓ Created {len(tasks)} tasks:")
    for task in tasks:
        print(f"  - [{task.priority.name}] {task.description}")
    
    # Get statistics
    print("\n4. Brain Statistics:")
    stats = brain.get_statistics()
    print(f"  - Total tasks: {stats['task_stats']['total']}")
    print(f"  - Pending tasks: {stats['task_stats']['pending']}")
    print(f"  - Iteration count: {stats['iteration_count']}")


def example_2_task_execution():
    """Example 2: Task execution with Motor System."""
    print("\n" + "=" * 60)
    print("Example 2: Task Execution")
    print("=" * 60)
    
    # Initialize systems
    print("\n1. Initializing systems...")
    brain = BrainModule()
    motor = MotorInterface(backend="simulation")
    print("✓ Brain and Motor initialized")
    
    # Create canvas
    print("\n2. Creating canvas...")
    motor.create_canvas(400, 600)
    print("✓ Canvas created (400x600)")
    
    # Create a task manually
    print("\n3. Creating task...")
    from brain.models.task import Task
    task = Task(
        task_id="task-1",
        task_type=TaskType.FIX_HAND,
        description="Fix left hand",
        priority=TaskPriority.HIGH,
        target_area={"x": 140, "y": 180, "width": 30, "height": 40}
    )
    print(f"✓ Task created: {task.description}")
    
    # Get action plan
    print("\n4. Creating action plan...")
    plan = brain.get_action_plan(task)
    print(f"✓ Action plan created:")
    print(f"  - Plan ID: {plan.plan_id}")
    print(f"  - Actions: {len(plan.actions)}")
    print(f"  - Estimated duration: {plan.estimated_total_duration:.1f}s")
    
    # Execute actions
    print("\n5. Executing actions...")
    for i, action in enumerate(plan.actions, 1):
        print(f"  Action {i}: {action.description}")
        success = brain.delegate_to_motor(action, motor)
        print(f"    {'✓' if success else '✗'} {'Success' if success else 'Failed'}")
    
    # Save result
    print("\n6. Saving result...")
    motor.save("/tmp/brain_example_result.png")
    print("✓ Result saved to /tmp/brain_example_result.png")
    
    motor.close()


def example_3_evaluation():
    """Example 3: Result evaluation."""
    print("\n" + "=" * 60)
    print("Example 3: Result Evaluation")
    print("=" * 60)
    
    # Initialize
    brain = BrainModule()
    
    # Create task
    from brain.models.task import Task
    task = Task(
        task_id="task-1",
        task_type=TaskType.FIX_PROPORTIONS,
        description="Fix body proportions"
    )
    
    # Simulate before/after vision results
    print("\n1. Simulating vision analysis...")
    vision_before = {
        "proportion_score": 0.55,
        "symmetry_score": 0.60,
        "detection_confidence": 0.85,
        "overall_similarity": 0.50
    }
    
    vision_after = {
        "proportion_score": 0.82,
        "symmetry_score": 0.78,
        "detection_confidence": 0.90,
        "overall_similarity": 0.75
    }
    
    print("  Before:")
    print(f"    - Proportion score: {vision_before['proportion_score']:.2f}")
    print(f"    - Symmetry score: {vision_before['symmetry_score']:.2f}")
    
    print("  After:")
    print(f"    - Proportion score: {vision_after['proportion_score']:.2f}")
    print(f"    - Symmetry score: {vision_after['symmetry_score']:.2f}")
    
    # Evaluate result
    print("\n2. Evaluating execution result...")
    result = brain.evaluate_result(task, vision_before, vision_after)
    print(f"✓ Execution result: {result.value.upper()}")
    
    if result.value == "success":
        print("  Task completed successfully!")
    elif result.value == "partial":
        print("  Task partially completed - may need refinement")
    else:
        print("  Task failed - will retry")


def example_4_iterative_refinement():
    """Example 4: Iterative refinement loop."""
    print("\n" + "=" * 60)
    print("Example 4: Iterative Refinement")
    print("=" * 60)
    
    # Initialize systems
    brain = BrainModule()
    motor = MotorInterface(backend="simulation")
    
    brain.set_goal("Create accurate figure drawing")
    
    print("\n1. Starting iterative refinement...")
    
    # Create initial canvas
    motor.create_canvas(400, 600)
    
    # Simulate refinement iterations
    max_iterations = 3
    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1}/{max_iterations} ---")
        
        brain.increment_iteration()
        
        # Simulate vision analysis with improving scores
        quality_score = 0.5 + (iteration * 0.15)
        vision_data = {
            "has_pose": True,
            "pose_errors": [] if quality_score > 0.7 else ["Minor issues"],
            "refinement_areas": [],
            "proportion_issues": quality_score < 0.7,
            "symmetry_issues": False,
            "proportion_score": quality_score,
            "symmetry_score": quality_score + 0.1,
            "detection_confidence": 0.9
        }
        
        print(f"  Quality score: {quality_score:.2f}")
        
        # Plan actions
        tasks = brain.plan_next_action(vision_data)
        
        if not tasks:
            print("  ✓ No more tasks - refinement complete!")
            break
        
        print(f"  Created {len(tasks)} tasks")
        
        # Execute first task (simulate)
        if tasks:
            task = tasks[0]
            print(f"  Executing: {task.description}")
            
            # Simulate execution and improvement
            vision_after = {
                "proportion_score": quality_score + 0.1,
                "symmetry_score": quality_score + 0.15
            }
            
            result = brain.evaluate_result(task, vision_data, vision_after)
            print(f"  Result: {result.value}")
    
    # Final statistics
    print("\n2. Final Statistics:")
    stats = brain.get_statistics()
    print(f"  - Completed tasks: {stats['task_stats']['completed']}")
    print(f"  - Total iterations: {stats['iteration_count']}")
    
    motor.close()


def example_5_integration():
    """Example 5: Full Motor-Vision-Brain integration."""
    print("\n" + "=" * 60)
    print("Example 5: Full System Integration")
    print("=" * 60)
    
    # Initialize all systems
    print("\n1. Initializing all systems...")
    brain = BrainModule()
    vision = VisionModule()
    motor = MotorInterface(backend="simulation")
    print("✓ Brain, Vision, and Motor initialized")
    
    # Set goal
    print("\n2. Setting goal...")
    brain.set_goal("Draw a well-proportioned figure")
    print(f"✓ Goal: {brain.get_goal()}")
    
    # Create initial drawing
    print("\n3. Creating initial drawing...")
    motor.create_canvas(400, 600)
    
    # Draw simple strokes
    motor.switch_tool(ToolPresets.pencil(size=3.0))
    
    # Draw a line (simulate body)
    points = [
        StrokePoint(x=200, y=100, pressure=0.5),
        StrokePoint(x=200, y=300, pressure=0.5)
    ]
    motor.draw_stroke(Stroke(points=points))
    
    # Save canvas
    motor.save("/tmp/initial_canvas.png")
    print("✓ Initial canvas created")
    
    # Analyze with Vision
    print("\n4. Analyzing with Vision System...")
    canvas_array = create_test_canvas()
    result = vision.analyze(canvas_array)
    
    print(f"✓ Vision analysis complete:")
    print(f"  - Image size: {result.image_width}x{result.image_height}")
    print(f"  - Detection confidence: {result.detection_confidence:.2%}")
    print(f"  - Features detected: {', '.join(result.get_detected_features()) or 'None'}")
    
    # Create vision data for Brain
    vision_data = {
        "has_pose": result.has_pose(),
        "pose_errors": [],
        "refinement_areas": [],
        "proportion_issues": False,
        "symmetry_issues": False,
        "proportion_score": 0.7,
        "symmetry_score": 0.75,
        "detection_confidence": result.detection_confidence
    }
    
    # Plan with Brain
    print("\n5. Planning with Brain System...")
    tasks = brain.plan_next_action(vision_data)
    print(f"✓ Created {len(tasks)} tasks")
    
    # Get statistics
    print("\n6. System Status:")
    brain_stats = brain.get_statistics()
    print(f"  Brain:")
    print(f"    - Pending tasks: {brain_stats['task_stats']['pending']}")
    print(f"    - Iteration: {brain_stats['iteration_count']}")
    
    # Cleanup
    motor.close()
    vision.close()
    print("\n✓ All systems closed")


def main():
    """Run all examples."""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "Brain System - Usage Examples" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_1_basic_usage()
        example_2_task_execution()
        example_3_evaluation()
        example_4_iterative_refinement()
        example_5_integration()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
