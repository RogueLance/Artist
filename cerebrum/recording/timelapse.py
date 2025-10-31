"""
Time-lapse generation module.

Creates time-lapse visualizations from recorded drawing sessions,
showing the progression of the AI's drawing process.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from cerebrum.recording.session_recorder import SessionRecorder, CanvasSnapshot

logger = logging.getLogger(__name__)


class TimelapseGenerator:
    """
    Generates time-lapse visualizations from drawing sessions.
    
    Creates videos, GIFs, or image sequences showing the progressive
    development of artwork, with optional overlays for metrics and stage info.
    
    Example:
        >>> recorder = SessionRecorder.load("session_dir/")
        >>> generator = TimelapseGenerator(recorder)
        >>> generator.generate_gif("timelapse.gif", fps=2)
        >>> generator.generate_image_grid("progress_grid.png", cols=4)
    """
    
    def __init__(self, recorder: SessionRecorder):
        """
        Initialize timelapse generator.
        
        Args:
            recorder: SessionRecorder instance with recorded snapshots
        """
        self.recorder = recorder
    
    def generate_gif(
        self,
        output_path: Path,
        fps: int = 2,
        add_overlay: bool = True,
        loop: int = 0
    ):
        """
        Generate animated GIF from snapshots.
        
        Args:
            output_path: Path to save GIF
            fps: Frames per second
            add_overlay: Whether to add stage/metric overlay
            loop: Number of loops (0 = infinite)
        """
        output_path = Path(output_path)
        
        if not self.recorder.snapshots:
            logger.warning("No snapshots to generate GIF")
            return
        
        # Prepare frames
        frames = []
        for snapshot in self.recorder.snapshots:
            frame = Image.fromarray(snapshot.canvas_data)
            
            if add_overlay:
                frame = self._add_overlay(frame, snapshot)
            
            frames.append(frame)
        
        # Save as GIF
        duration = int(1000 / fps)  # milliseconds per frame
        
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=loop
        )
        
        logger.info(f"GIF saved to {output_path} ({len(frames)} frames, {fps} fps)")
    
    def generate_image_grid(
        self,
        output_path: Path,
        cols: int = 4,
        add_overlay: bool = True,
        target_size: Optional[Tuple[int, int]] = None
    ):
        """
        Generate grid of key snapshots.
        
        Args:
            output_path: Path to save grid image
            cols: Number of columns in grid
            add_overlay: Whether to add stage/metric overlay
            target_size: Optional target size for each snapshot (width, height)
        """
        output_path = Path(output_path)
        
        if not self.recorder.snapshots:
            logger.warning("No snapshots to generate grid")
            return
        
        # Select evenly distributed snapshots
        total = len(self.recorder.snapshots)
        step = max(1, total // (cols * 3))  # Aim for ~3 rows
        selected = self.recorder.snapshots[::step]
        
        # Prepare images
        images = []
        for snapshot in selected:
            img = Image.fromarray(snapshot.canvas_data)
            
            if target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            if add_overlay:
                img = self._add_overlay(img, snapshot)
            
            images.append(img)
        
        # Calculate grid dimensions
        rows = (len(images) + cols - 1) // cols
        
        # Get image size
        img_width, img_height = images[0].size
        
        # Create grid
        grid_width = cols * img_width
        grid_height = rows * img_height
        grid = Image.new('RGB', (grid_width, grid_height), 'white')
        
        # Place images
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            x = col * img_width
            y = row * img_height
            grid.paste(img, (x, y))
        
        grid.save(output_path)
        logger.info(f"Grid saved to {output_path} ({len(images)} images, {cols}x{rows})")
    
    def generate_comparison(
        self,
        output_path: Path,
        stages: Optional[List[str]] = None
    ):
        """
        Generate side-by-side comparison of specific stages.
        
        Args:
            output_path: Path to save comparison image
            stages: List of stage names to compare (None = first/last)
        """
        output_path = Path(output_path)
        
        if not self.recorder.snapshots:
            logger.warning("No snapshots for comparison")
            return
        
        if stages is None:
            # Compare first and last
            snapshots = [self.recorder.snapshots[0], self.recorder.snapshots[-1]]
        else:
            # Get first snapshot of each stage
            snapshots = []
            for stage in stages:
                stage_snapshots = self.recorder.get_snapshots_by_stage(stage)
                if stage_snapshots:
                    snapshots.append(stage_snapshots[0])
        
        if not snapshots:
            logger.warning("No snapshots found for comparison")
            return
        
        # Create side-by-side comparison
        images = [Image.fromarray(s.canvas_data) for s in snapshots]
        
        # Add labels
        labeled_images = []
        for img, snapshot in zip(images, snapshots):
            img_with_label = self._add_overlay(img, snapshot)
            labeled_images.append(img_with_label)
        
        # Combine horizontally
        widths, heights = zip(*(i.size for i in labeled_images))
        
        total_width = sum(widths)
        max_height = max(heights)
        
        comparison = Image.new('RGB', (total_width, max_height), 'white')
        
        x_offset = 0
        for img in labeled_images:
            comparison.paste(img, (x_offset, 0))
            x_offset += img.width
        
        comparison.save(output_path)
        logger.info(f"Comparison saved to {output_path}")
    
    def generate_video(
        self,
        output_path: Path,
        fps: int = 2,
        add_overlay: bool = True,
        codec: str = 'mp4v'
    ):
        """
        Generate video from snapshots (requires opencv).
        
        Args:
            output_path: Path to save video
            fps: Frames per second
            add_overlay: Whether to add stage/metric overlay
            codec: Video codec (e.g., 'mp4v', 'avc1')
        """
        try:
            import cv2
        except ImportError:
            logger.warning("OpenCV not available - cannot generate video")
            return
        
        output_path = Path(output_path)
        
        if not self.recorder.snapshots:
            logger.warning("No snapshots to generate video")
            return
        
        # Get frame size
        first_frame = self.recorder.snapshots[0].canvas_data
        height, width = first_frame.shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Write frames
        for snapshot in self.recorder.snapshots:
            frame = snapshot.canvas_data.copy()
            
            if add_overlay:
                frame_img = self._add_overlay(Image.fromarray(frame), snapshot)
                frame = np.array(frame_img)
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        logger.info(f"Video saved to {output_path} ({len(self.recorder.snapshots)} frames, {fps} fps)")
    
    def _add_overlay(
        self,
        image: Image.Image,
        snapshot: CanvasSnapshot
    ) -> Image.Image:
        """Add overlay with stage and metric information."""
        # Create a copy to draw on
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            font_small = font
        
        # Prepare text
        text_lines = [
            f"Stage: {snapshot.stage}",
            f"Time: {snapshot.timestamp:.1f}s",
            f"Iteration: {snapshot.iteration}"
        ]
        
        # Add key metrics
        if snapshot.metrics:
            for key, value in list(snapshot.metrics.items())[:2]:  # Max 2 metrics
                if isinstance(value, float):
                    text_lines.append(f"{key}: {value:.2f}")
                else:
                    text_lines.append(f"{key}: {value}")
        
        # Draw background rectangle
        padding = 10
        line_height = 20
        bg_height = len(text_lines) * line_height + 2 * padding
        bg_width = 250
        
        draw.rectangle(
            [(0, 0), (bg_width, bg_height)],
            fill=(0, 0, 0, 180)
        )
        
        # Draw text
        y = padding
        for line in text_lines:
            draw.text((padding, y), line, fill='white', font=font_small)
            y += line_height
        
        return img
