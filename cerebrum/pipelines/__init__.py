"""
Pipeline module for end-to-end art generation workflows.
"""

from cerebrum.pipelines.base_pipeline import BasePipeline, PipelineStage, PipelineResult
from cerebrum.pipelines.photo_pipeline import PhotoReferencePipeline
from cerebrum.pipelines.sketch_pipeline import SketchCorrectionPipeline
from cerebrum.pipelines.ai_pipeline import AIImagePipeline

__all__ = [
    "BasePipeline",
    "PipelineStage",
    "PipelineResult",
    "PhotoReferencePipeline",
    "SketchCorrectionPipeline",
    "AIImagePipeline",
]
