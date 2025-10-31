"""
Integration test for Brain System with Motor and Vision systems.

Tests the complete workflow of analyzing, planning, executing, and evaluating.
"""

import sys
from pathlib import Path

# Add parent directory to path to access brain, motor, vision modules
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

import pytest
import numpy as np
from PIL import Image, ImageDraw

from brain import BrainModule, TaskType
from motor import MotorInterface, ToolPresets, Stroke, StrokePoint
from vision import VisionModule


def create_test_figure(width=400, height=600):
    """Create a simple test figure."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Simple stick figure
    draw.ellipse([175, 50, 225, 100], outline='black', width=3)  # Head
    draw.line([200, 100, 200, 300], fill='black', width=3)  # Body
    draw.line([200, 150, 140, 220], fill='black', width=3)  # Left arm
    draw.line([200, 150, 260, 220], fill='black', width=3)  # Right arm
    draw.line([200, 300, 150, 480], fill='black', width=3)  # Left leg
    draw.line([200, 300, 250, 480], fill='black', width=3)  # Right leg
    
    return np.array(img)


class TestBrainIntegration:
    """Test Brain System integration with Motor and Vision."""
    
    def test_brain_motor_integration(self):
        """Test Brain-Motor integration."""
        brain = BrainModule()
        motor = MotorInterface(backend="simulation")
        
        # Set goal
        brain.set_goal("Create test drawing")
        assert brain.get_goal() == "Create test drawing"
        
        # Create canvas
        motor.create_canvas(400, 600)
        
        # Create a simple task
        from brain.models.task import Task
        task = Task(
            task_id="test-1",
            task_type=TaskType.FIX_HAND,
            description="Test task"
        )
        
        # Get action plan
        plan = brain.get_action_plan(task)
        assert plan is not None
        assert len(plan.actions) > 0
        
        # Execute actions
        for action in plan.actions:
            success = brain.delegate_to_motor(action, motor)
            assert isinstance(success, bool)
        
        motor.close()
    
    def test_brain_vision_integration(self):
        """Test Brain-Vision integration."""
        brain = BrainModule()
        vision = VisionModule()
        
        # Create test image
        test_image = create_test_figure()
        
        # Analyze with vision
        result = vision.analyze(test_image)
        
        # Create vision data for brain
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
        
        # Plan with brain
        tasks = brain.plan_next_action(vision_data)
        
        # Should be a list of tasks
        assert isinstance(tasks, list)
        
        vision.close()
    
    def test_full_workflow(self):
        """Test complete workflow: Motor -> Vision -> Brain -> Motor."""
        brain = BrainModule()
        vision = VisionModule()
        motor = MotorInterface(backend="simulation")
        
        # Set goal
        brain.set_goal("Draw accurate figure")
        
        # 1. Motor creates initial drawing
        motor.create_canvas(400, 600)
        motor.switch_tool(ToolPresets.pencil(size=2.0))
        
        points = [
            StrokePoint(x=200, y=100, pressure=0.5),
            StrokePoint(x=200, y=300, pressure=0.5)
        ]
        motor.draw_stroke(Stroke(points=points))
        
        # 2. Vision analyzes
        test_image = create_test_figure()
        result = vision.analyze(test_image)
        
        # 3. Brain plans
        vision_data = {
            "has_pose": result.has_pose(),
            "pose_errors": ["Test error"],
            "refinement_areas": [],
            "proportion_issues": True,
            "symmetry_issues": False,
            "proportion_score": 0.5,
            "symmetry_score": 0.7,
            "detection_confidence": result.detection_confidence
        }
        
        tasks = brain.plan_next_action(vision_data, auto_schedule=True)
        
        # Should create tasks
        assert len(tasks) > 0
        
        # 4. Brain executes via Motor
        next_task = brain.get_next_task()
        if next_task:
            plan = brain.get_action_plan(next_task)
            for action in plan.actions:
                brain.delegate_to_motor(action, motor)
        
        # Cleanup
        motor.close()
        vision.close()
    
    def test_iterative_refinement(self):
        """Test iterative refinement workflow."""
        brain = BrainModule()
        
        brain.set_goal("Iterative refinement")
        
        # Simulate multiple iterations
        for i in range(3):
            brain.increment_iteration()
            
            # Simulate improving quality
            quality = 0.5 + (i * 0.15)
            vision_data = {
                "has_pose": True,
                "pose_errors": [] if quality > 0.7 else ["Minor issue"],
                "refinement_areas": [],
                "proportion_issues": quality < 0.7,
                "symmetry_issues": False,
                "proportion_score": quality,
                "symmetry_score": quality + 0.1
            }
            
            tasks = brain.plan_next_action(vision_data, auto_schedule=True)
            
            # Process tasks
            if tasks:
                from brain.models.brain_state import ExecutionResult
                
                for task in tasks:
                    # Simulate execution
                    vision_before = vision_data
                    vision_after = {
                        "proportion_score": quality + 0.1,
                        "symmetry_score": quality + 0.15
                    }
                    
                    result = brain.evaluate_result(task, vision_before, vision_after)
                    assert result in [ExecutionResult.SUCCESS, ExecutionResult.PARTIAL, ExecutionResult.FAILURE]
        
        # Check statistics
        stats = brain.get_statistics()
        assert stats["iteration_count"] == 3
    
    def test_task_retry_workflow(self):
        """Test task retry in workflow."""
        brain = BrainModule()
        
        # Create task that will fail
        vision_data = {
            "has_pose": True,
            "pose_errors": ["Critical error"],
            "refinement_areas": [],
            "proportion_issues": True,
            "symmetry_issues": False,
            "proportion_score": 0.3,
            "symmetry_score": 0.4
        }
        
        tasks = brain.plan_next_action(vision_data, auto_schedule=True)
        assert len(tasks) > 0
        
        # Simulate failure and retry
        task = tasks[0]
        
        # First attempt - fail
        vision_before = {"proportion_score": 0.3}
        vision_after = {"proportion_score": 0.35}  # Small improvement
        
        result = brain.evaluate_result(task, vision_before, vision_after)
        
        # Should either fail or partial (depending on improvement)
        from brain.models.brain_state import ExecutionResult
        assert result in [ExecutionResult.FAILURE, ExecutionResult.PARTIAL]


def main():
    """Run integration tests."""
    print("=" * 60)
    print("Brain System Integration Tests")
    print("=" * 60)
    
    test = TestBrainIntegration()
    
    print("\n1. Testing Brain-Motor integration...")
    test.test_brain_motor_integration()
    print("✓ Brain-Motor integration test passed")
    
    print("\n2. Testing Brain-Vision integration...")
    test.test_brain_vision_integration()
    print("✓ Brain-Vision integration test passed")
    
    print("\n3. Testing full workflow...")
    test.test_full_workflow()
    print("✓ Full workflow test passed")
    
    print("\n4. Testing iterative refinement...")
    test.test_iterative_refinement()
    print("✓ Iterative refinement test passed")
    
    print("\n5. Testing task retry workflow...")
    test.test_task_retry_workflow()
    print("✓ Task retry workflow test passed")
    
    print("\n" + "=" * 60)
    print("All integration tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
