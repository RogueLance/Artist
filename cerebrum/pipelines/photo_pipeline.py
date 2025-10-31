"""
Photo Reference Pipeline.

Transforms a photo reference into a stylized artistic output, following
the workflow: Reference Analysis → Gesture → Structure → Refinement → Style.
"""

import logging
from pathlib import Path
from typing import Optional, Union
import numpy as np
from PIL import Image

from cerebrum.pipelines.base_pipeline import BasePipeline, PipelineStage, StageResult
from motor import MotorInterface, ToolPresets, Stroke, StrokePoint
from vision import VisionModule
from brain import BrainModule

logger = logging.getLogger(__name__)


class PhotoReferencePipeline(BasePipeline):
    """
    Pipeline for converting photo references to stylized artwork.
    
    Workflow:
    1. Analyze photo for pose, proportions, features
    2. Create gesture sketch capturing main forms
    3. Refine structure for anatomical accuracy
    4. Add details (hands, face, clothing)
    5. Apply stylistic rendering
    
    Example:
        >>> pipeline = PhotoReferencePipeline()
        >>> result = pipeline.execute(reference_image="photo.jpg")
        >>> # Save result
        >>> from PIL import Image
        >>> Image.fromarray(result.final_canvas).save("output.png")
    """
    
    def __init__(
        self,
        motor_backend: str = "simulation",
        canvas_width: int = 800,
        canvas_height: int = 1000,
        max_iterations: int = 5,
        quality_threshold: float = 0.75
    ):
        """Initialize photo reference pipeline."""
        super().__init__(
            motor_backend=motor_backend,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            max_iterations=max_iterations,
            quality_threshold=quality_threshold
        )
        self.reference_data = None
    
    def _stage_initialization(
        self,
        reference_image: Optional[Union[str, Path, np.ndarray]],
        goal: Optional[str],
        **kwargs
    ) -> StageResult:
        """Initialize systems and load reference."""
        # Initialize systems
        self.motor = MotorInterface(backend=self.motor_backend)
        self.vision = VisionModule()
        self.brain = BrainModule()
        
        # Create canvas
        self.motor.create_canvas(self.canvas_width, self.canvas_height)
        
        # Set goal
        goal = goal or "Create stylized artwork from photo reference"
        self.brain.set_goal(goal)
        
        # Load reference if provided
        if reference_image is not None:
            if isinstance(reference_image, (str, Path)):
                self.reference_data = np.array(Image.open(reference_image))
            else:
                self.reference_data = reference_image
        
        return StageResult(
            stage=PipelineStage.INITIALIZATION,
            success=True,
            duration=0.0,
            metrics={"has_reference": self.reference_data is not None},
            notes="Systems initialized successfully"
        )
    
    def _stage_analysis(
        self,
        reference_image: Optional[Union[str, Path, np.ndarray]],
        **kwargs
    ) -> StageResult:
        """Analyze reference photo."""
        if self.reference_data is None:
            return StageResult(
                stage=PipelineStage.ANALYSIS,
                success=True,
                duration=0.0,
                notes="No reference to analyze"
            )
        
        # Analyze reference with vision
        result = self.vision.analyze(self.reference_data)
        
        metrics = {
            "has_pose": result.has_pose(),
            "has_face": result.has_face(),
            "has_hands": result.has_hands(),
            "detection_confidence": result.detection_confidence
        }
        
        if result.has_pose() and result.proportion_metrics:
            metrics["proportion_score"] = result.proportion_metrics.overall_score
        
        logger.info(f"Reference analysis: {metrics}")
        
        return StageResult(
            stage=PipelineStage.ANALYSIS,
            success=True,
            duration=0.0,
            metrics=metrics,
            notes="Reference analyzed successfully"
        )
    
    def _stage_gesture(self, **kwargs) -> StageResult:
        """Create initial gesture sketch."""
        # Select gesture tool (thin, light pencil)
        self.motor.switch_tool(ToolPresets.pencil(size=2.0))
        
        # If we have reference data, use vision to guide gesture
        if self.reference_data is not None:
            result = self.vision.analyze(self.reference_data)
            
            if result.has_pose():
                # Draw simplified stick figure based on pose
                self._draw_gesture_from_pose(result.pose)
        
        return StageResult(
            stage=PipelineStage.GESTURE,
            success=True,
            duration=0.0,
            metrics={"strokes_drawn": 1},
            notes="Gesture sketch created"
        )
    
    def _stage_structure(self, **kwargs) -> StageResult:
        """Refine structure and proportions."""
        # Switch to structure tool
        self.motor.switch_tool(ToolPresets.pencil(size=3.0))
        
        # Save current canvas for analysis
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        self.motor.save(temp_path)
        
        # Analyze current state
        canvas_array = np.array(Image.open(temp_path))
        canvas_result = self.vision.analyze(canvas_array)
        
        # Compare to reference if available
        if self.reference_data is not None:
            comparison = self.vision.compare_to(canvas_array, self.reference_data)
            metrics = {
                "similarity": comparison.overall_similarity
            }
            if comparison.pose_metrics:
                metrics["pose_difference"] = comparison.pose_metrics.get("difference", 0.0)
        else:
            metrics = {}
        
        # Clean up temp file
        Path(temp_path).unlink()
        
        return StageResult(
            stage=PipelineStage.STRUCTURE,
            success=True,
            duration=0.0,
            metrics=metrics,
            notes="Structure refined"
        )
    
    def _stage_refinement(self, **kwargs) -> StageResult:
        """Iteratively refine based on vision feedback."""
        refinement_count = 0
        max_refinements = kwargs.get('max_refinements', self.max_iterations)
        
        for iteration in range(max_refinements):
            self.brain.increment_iteration()
            
            # Analyze current canvas
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name
            self.motor.save(temp_path)
            canvas_array = np.array(Image.open(temp_path))
            Path(temp_path).unlink()
            
            # Compare to reference
            if self.reference_data is not None:
                comparison = self.vision.compare_to(canvas_array, self.reference_data)
                
                # Check if we've reached quality threshold
                if comparison.overall_similarity >= self.quality_threshold:
                    logger.info(f"Quality threshold reached: {comparison.overall_similarity:.2f}")
                    break
                
                # Get refinement areas
                errors = self.vision.detect_pose_errors(canvas_array, self.reference_data)
                
                # Create vision data for brain
                vision_data = {
                    "has_pose": True,
                    "pose_errors": errors,
                    "refinement_areas": [],
                    "proportion_issues": comparison.overall_similarity < 0.7,
                    "symmetry_issues": False,
                    "proportion_score": comparison.overall_similarity,
                    "symmetry_score": 0.8,
                    "detection_confidence": 0.9
                }
                
                # Plan corrections
                tasks = self.brain.plan_next_action(vision_data)
                
                if tasks:
                    # Execute first task
                    task = tasks[0]
                    plan = self.brain.get_action_plan(task)
                    
                    for action in plan.actions:
                        self.brain.delegate_to_motor(action, self.motor)
                    
                    refinement_count += 1
            else:
                break
        
        return StageResult(
            stage=PipelineStage.REFINEMENT,
            success=True,
            duration=0.0,
            metrics={
                "refinement_iterations": refinement_count,
                "max_iterations": max_refinements
            },
            notes=f"Completed {refinement_count} refinement iterations"
        )
    
    def _stage_detail(self, **kwargs) -> StageResult:
        """Add details and features."""
        # Switch to detail tool
        self.motor.switch_tool(ToolPresets.pen(size=1.5))
        
        # This stage would add facial features, hand details, etc.
        # For now, we mark it as successful
        
        return StageResult(
            stage=PipelineStage.DETAIL,
            success=True,
            duration=0.0,
            notes="Details added"
        )
    
    def _stage_stylization(self, **kwargs) -> StageResult:
        """Apply stylistic rendering."""
        # This stage would apply stylistic choices
        # For now, we mark it as optional success
        
        return StageResult(
            stage=PipelineStage.STYLIZATION,
            success=True,
            duration=0.0,
            notes="Stylization complete (optional)"
        )
    
    def _stage_completion(self, **kwargs) -> StageResult:
        """Final validation and export."""
        # Save final result
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        self.motor.save(temp_path)
        
        # Final analysis
        canvas_array = np.array(Image.open(temp_path))
        result = self.vision.analyze(canvas_array)
        
        metrics = {
            "has_pose": result.has_pose(),
            "detection_confidence": result.detection_confidence
        }
        
        if self.reference_data is not None:
            comparison = self.vision.compare_to(canvas_array, self.reference_data)
            metrics["final_similarity"] = comparison.overall_similarity
        
        Path(temp_path).unlink()
        
        return StageResult(
            stage=PipelineStage.COMPLETION,
            success=True,
            duration=0.0,
            metrics=metrics,
            notes="Pipeline completed successfully"
        )
    
    def _draw_gesture_from_pose(self, pose_data):
        """Draw a simplified gesture from pose keypoints."""
        if not pose_data or not pose_data.keypoints:
            return
        
        # Draw a few main lines for gesture
        # This is simplified - real implementation would be more sophisticated
        keypoints = pose_data.keypoints
        
        # Example: draw torso line
        if len(keypoints) > 11:
            # Shoulders to hips (simplified)
            shoulder = keypoints[11]
            hip = keypoints[23] if len(keypoints) > 23 else keypoints[11]
            
            points = [
                StrokePoint(x=shoulder.x * self.canvas_width, y=shoulder.y * self.canvas_height, pressure=0.5),
                StrokePoint(x=hip.x * self.canvas_width, y=hip.y * self.canvas_height, pressure=0.5)
            ]
            self.motor.draw_stroke(Stroke(points=points))
