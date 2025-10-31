"""
Display formatting utilities for the interface.
"""

from typing import List, Dict, Any, Optional
import textwrap


class DisplayFormatter:
    """
    Formatter for displaying information to the user.
    
    Provides methods for formatting vision results, brain tasks, and
    other information in a readable format.
    """
    
    @staticmethod
    def format_header(text: str, width: int = 70, char: str = "=") -> str:
        """Format a header with border."""
        border = char * width
        padding_left = (width - len(text) - 2) // 2
        padding_right = width - len(text) - 2 - padding_left
        return f"{border}\n{' ' * padding_left} {text}{' ' * padding_right}\n{border}"
    
    @staticmethod
    def format_section(title: str, width: int = 70) -> str:
        """Format a section header."""
        return f"\n{title}\n{'-' * len(title)}"
    
    @staticmethod
    def format_list(items: List[str], prefix: str = "  •") -> str:
        """Format a list of items."""
        if not items:
            return f"{prefix} None"
        return "\n".join(f"{prefix} {item}" for item in items)
    
    @staticmethod
    def format_dict(data: Dict[str, Any], indent: int = 2) -> str:
        """Format a dictionary for display."""
        lines = []
        prefix = " " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(DisplayFormatter.format_dict(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        return "\n".join(lines)
    
    @staticmethod
    def format_vision_result(result: Any) -> str:
        """
        Format vision analysis result.
        
        Args:
            result: AnalysisResult from VisionModule
            
        Returns:
            Formatted string for display
        """
        lines = [DisplayFormatter.format_section("Vision Analysis")]
        
        # Image info
        lines.append(f"  Image size: {result.image_width}x{result.image_height}")
        lines.append(f"  Confidence: {result.detection_confidence:.1%}")
        
        # Detected features
        features = result.get_detected_features()
        if features:
            lines.append(f"  Detected: {', '.join(features)}")
        else:
            lines.append("  Detected: No features")
        
        # Pose information
        if result.has_pose():
            lines.append(f"  Pose keypoints: {len(result.pose.keypoints)}")
        
        # Metrics
        if result.proportion_metrics:
            lines.append(f"  Proportion score: {result.proportion_metrics.overall_score:.2f}")
        if result.symmetry_metrics:
            lines.append(f"  Symmetry score: {result.symmetry_metrics.overall_score:.2f}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_comparison_result(comparison: Any) -> str:
        """
        Format vision comparison result.
        
        Args:
            comparison: ComparisonResult from VisionModule
            
        Returns:
            Formatted string for display
        """
        lines = [DisplayFormatter.format_section("Vision Comparison")]
        
        lines.append(f"  Overall similarity: {comparison.overall_similarity:.1%}")
        
        if comparison.pose_metrics:
            lines.append(f"  Pose similarity: {comparison.pose_metrics.pose_similarity:.1%}")
            lines.append(f"  Average distance: {comparison.pose_metrics.average_distance:.2f}")
        
        if comparison.proportion_metrics:
            lines.append(f"  Proportion score: {comparison.proportion_metrics.overall_score:.2f}")
        
        if comparison.symmetry_metrics:
            lines.append(f"  Symmetry score: {comparison.symmetry_metrics.overall_score:.2f}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_tasks(tasks: List[Any]) -> str:
        """
        Format Brain tasks.
        
        Args:
            tasks: List of Task objects from BrainModule
            
        Returns:
            Formatted string for display
        """
        lines = [DisplayFormatter.format_section("Brain Tasks")]
        
        if not tasks:
            lines.append("  No tasks created")
            return "\n".join(lines)
        
        for i, task in enumerate(tasks, 1):
            lines.append(f"\n  Task {i}:")
            lines.append(f"    Type: {task.task_type.value}")
            lines.append(f"    Priority: {task.priority.value}")
            lines.append(f"    Description: {task.description}")
            if task.target_area:
                area = task.target_area
                lines.append(f"    Target: ({area.get('x', 0)}, {area.get('y', 0)}) "
                           f"{area.get('width', 0)}x{area.get('height', 0)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_action_plan(plan: Any) -> str:
        """
        Format Brain action plan.
        
        Args:
            plan: ActionPlan from BrainModule
            
        Returns:
            Formatted string for display
        """
        lines = [DisplayFormatter.format_section("Action Plan")]
        
        lines.append(f"  Plan ID: {plan.plan_id}")
        lines.append(f"  Task: {plan.task_id}")
        lines.append(f"  Actions: {len(plan.actions)}")
        lines.append(f"  Duration: {plan.estimated_total_duration:.1f}s")
        
        if plan.actions:
            lines.append("\n  Actions:")
            for i, action in enumerate(plan.actions, 1):
                lines.append(f"    {i}. {action.description}")
                lines.append(f"       Type: {action.action_type}")
                if action.parameters:
                    lines.append(f"       Parameters: {action.parameters}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_evaluation(result: Any, scores: Dict[str, float]) -> str:
        """
        Format evaluation result.
        
        Args:
            result: ExecutionResult from BrainModule
            scores: Score dictionary
            
        Returns:
            Formatted string for display
        """
        lines = [DisplayFormatter.format_section("Evaluation")]
        
        lines.append(f"  Result: {result.value.upper()}")
        lines.append(f"  Score change: {result.score_change:+.2f}")
        lines.append(f"  Confidence: {result.confidence:.1%}")
        
        if scores:
            lines.append("\n  Scores:")
            for key, value in scores.items():
                lines.append(f"    {key}: {value:.2f}")
        
        if result.notes:
            lines.append(f"\n  Notes: {result.notes}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_prompt(message: str, options: Optional[List[str]] = None) -> str:
        """
        Format a user prompt.
        
        Args:
            message: Prompt message
            options: Optional list of valid options
            
        Returns:
            Formatted prompt string
        """
        prompt = f"\n{message}"
        if options:
            prompt += f" [{'/'.join(options)}]"
        prompt += ": "
        return prompt
    
    @staticmethod
    def wrap_text(text: str, width: int = 70, indent: int = 0) -> str:
        """Wrap text to specified width with optional indent."""
        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=' ' * indent,
            subsequent_indent=' ' * indent
        )
        return wrapper.fill(text)
