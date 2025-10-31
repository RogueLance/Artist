"""
Base pipeline class for end-to-end art generation workflows.

This module provides the foundation for building complete art generation pipelines
that integrate Motor, Vision, and Brain systems.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Stages in the art generation pipeline."""
    INITIALIZATION = "initialization"
    ANALYSIS = "analysis"
    GESTURE = "gesture"
    STRUCTURE = "structure"
    REFINEMENT = "refinement"
    DETAIL = "detail"
    STYLIZATION = "stylization"
    COMPLETION = "completion"


@dataclass
class StageResult:
    """Result from a pipeline stage."""
    stage: PipelineStage
    success: bool
    duration: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    canvas_state: Optional[np.ndarray] = None


@dataclass
class PipelineResult:
    """Complete result from a pipeline execution."""
    success: bool
    total_duration: float
    stages: List[StageResult]
    final_canvas: Optional[np.ndarray] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def get_stage_result(self, stage: PipelineStage) -> Optional[StageResult]:
        """Get result for a specific stage."""
        for result in self.stages:
            if result.stage == stage:
                return result
        return None
    
    def get_metric(self, key: str, default: Any = None) -> Any:
        """Get a specific metric value."""
        return self.metrics.get(key, default)


class BasePipeline(ABC):
    """
    Base class for art generation pipelines.
    
    A pipeline orchestrates the complete workflow from input to final output,
    coordinating Motor, Vision, and Brain systems through multiple stages.
    
    Example:
        >>> pipeline = PhotoReferencePipeline(
        ...     motor_backend="simulation",
        ...     canvas_width=800,
        ...     canvas_height=600
        ... )
        >>> result = pipeline.execute(reference_image="photo.jpg")
        >>> print(f"Success: {result.success}, Duration: {result.total_duration:.1f}s")
    """
    
    def __init__(
        self,
        motor_backend: str = "simulation",
        canvas_width: int = 800,
        canvas_height: int = 600,
        max_iterations: int = 5,
        quality_threshold: float = 0.7
    ):
        """
        Initialize pipeline.
        
        Args:
            motor_backend: Motor backend to use ("simulation" or "krita")
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            max_iterations: Maximum refinement iterations
            quality_threshold: Quality score threshold for completion
        """
        self.motor_backend = motor_backend
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        
        self.motor = None
        self.vision = None
        self.brain = None
        
        self._initialized = False
        self._stage_results: List[StageResult] = []
        self._start_time = 0.0
    
    def execute(
        self,
        reference_image: Optional[Union[str, Path, np.ndarray]] = None,
        goal: Optional[str] = None,
        **kwargs
    ) -> PipelineResult:
        """
        Execute the complete pipeline.
        
        Args:
            reference_image: Optional reference image (path or array)
            goal: Artistic goal description
            **kwargs: Additional pipeline-specific parameters
            
        Returns:
            PipelineResult with execution details and final output
        """
        self._start_time = time.time()
        self._stage_results = []
        errors = []
        
        try:
            # Stage 1: Initialization
            logger.info("Starting pipeline execution")
            init_result = self._run_stage(
                PipelineStage.INITIALIZATION,
                lambda: self._stage_initialization(reference_image, goal, **kwargs)
            )
            
            if not init_result.success:
                return self._create_result(False, errors=["Initialization failed"])
            
            # Stage 2: Analysis
            analysis_result = self._run_stage(
                PipelineStage.ANALYSIS,
                lambda: self._stage_analysis(reference_image, **kwargs)
            )
            
            # Stage 3: Gesture
            gesture_result = self._run_stage(
                PipelineStage.GESTURE,
                lambda: self._stage_gesture(**kwargs)
            )
            
            # Stage 4: Structure
            structure_result = self._run_stage(
                PipelineStage.STRUCTURE,
                lambda: self._stage_structure(**kwargs)
            )
            
            # Stage 5: Refinement (iterative)
            refinement_result = self._run_stage(
                PipelineStage.REFINEMENT,
                lambda: self._stage_refinement(**kwargs)
            )
            
            # Stage 6: Detail
            detail_result = self._run_stage(
                PipelineStage.DETAIL,
                lambda: self._stage_detail(**kwargs)
            )
            
            # Stage 7: Stylization
            stylization_result = self._run_stage(
                PipelineStage.STYLIZATION,
                lambda: self._stage_stylization(**kwargs)
            )
            
            # Stage 8: Completion
            completion_result = self._run_stage(
                PipelineStage.COMPLETION,
                lambda: self._stage_completion(**kwargs)
            )
            
            # Determine overall success
            success = all(r.success for r in self._stage_results if r.stage != PipelineStage.STYLIZATION)
            
            return self._create_result(success, errors=errors)
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            errors.append(str(e))
            return self._create_result(False, errors=errors)
        
        finally:
            self._cleanup()
    
    def _run_stage(self, stage: PipelineStage, func) -> StageResult:
        """Run a pipeline stage with timing and error handling."""
        logger.info(f"Running stage: {stage.value}")
        start_time = time.time()
        
        try:
            result = func()
            duration = time.time() - start_time
            
            if result is None:
                result = StageResult(
                    stage=stage,
                    success=True,
                    duration=duration
                )
            elif not isinstance(result, StageResult):
                result = StageResult(
                    stage=stage,
                    success=bool(result),
                    duration=duration
                )
            
            self._stage_results.append(result)
            logger.info(f"Stage {stage.value} completed in {duration:.2f}s")
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Stage {stage.value} failed: {e}", exc_info=True)
            result = StageResult(
                stage=stage,
                success=False,
                duration=duration,
                notes=str(e)
            )
            self._stage_results.append(result)
            return result
    
    def _create_result(
        self,
        success: bool,
        errors: Optional[List[str]] = None
    ) -> PipelineResult:
        """Create final pipeline result."""
        total_duration = time.time() - self._start_time
        
        # Get final canvas
        final_canvas = None
        if self.motor:
            try:
                # Save to temp and read back
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    temp_path = f.name
                self.motor.save(temp_path)
                from PIL import Image
                final_canvas = np.array(Image.open(temp_path))
                Path(temp_path).unlink()
            except Exception as e:
                logger.warning(f"Could not capture final canvas: {e}")
        
        # Aggregate metrics
        metrics = {
            "total_stages": len(self._stage_results),
            "successful_stages": sum(1 for r in self._stage_results if r.success),
            "failed_stages": sum(1 for r in self._stage_results if not r.success),
        }
        
        return PipelineResult(
            success=success,
            total_duration=total_duration,
            stages=self._stage_results,
            final_canvas=final_canvas,
            metrics=metrics,
            errors=errors or []
        )
    
    def _cleanup(self):
        """Clean up resources."""
        if self.motor:
            try:
                self.motor.close()
            except Exception as e:
                logger.warning(f"Error closing motor: {e}")
        
        if self.vision:
            try:
                self.vision.close()
            except Exception as e:
                logger.warning(f"Error closing vision: {e}")
        
        if self.brain:
            try:
                self.brain.close()
            except Exception as e:
                logger.warning(f"Error closing brain: {e}")
    
    # Abstract methods - must be implemented by subclasses
    
    @abstractmethod
    def _stage_initialization(
        self,
        reference_image: Optional[Union[str, Path, np.ndarray]],
        goal: Optional[str],
        **kwargs
    ) -> StageResult:
        """Initialize pipeline systems and canvas."""
        pass
    
    @abstractmethod
    def _stage_analysis(
        self,
        reference_image: Optional[Union[str, Path, np.ndarray]],
        **kwargs
    ) -> StageResult:
        """Analyze reference image and plan approach."""
        pass
    
    @abstractmethod
    def _stage_gesture(self, **kwargs) -> StageResult:
        """Create initial gesture sketch."""
        pass
    
    @abstractmethod
    def _stage_structure(self, **kwargs) -> StageResult:
        """Refine structure and proportions."""
        pass
    
    @abstractmethod
    def _stage_refinement(self, **kwargs) -> StageResult:
        """Iteratively refine based on vision feedback."""
        pass
    
    @abstractmethod
    def _stage_detail(self, **kwargs) -> StageResult:
        """Add details and features."""
        pass
    
    @abstractmethod
    def _stage_stylization(self, **kwargs) -> StageResult:
        """Apply stylistic choices."""
        pass
    
    @abstractmethod
    def _stage_completion(self, **kwargs) -> StageResult:
        """Final checks and cleanup."""
        pass
