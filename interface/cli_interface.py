"""
Command-Line Interface for Cerebrum AI-Driven Art Platform.

This module provides a CLI for interacting with the Cerebrum system,
allowing users to guide the art creation process, provide feedback,
and control iterations.
"""

import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from interface.models.session import Session, SessionConfig
from interface.models.user_input import UserInput, InputType, UserDecision
from interface.utils.logger import InterfaceLogger
from interface.utils.display import DisplayFormatter

# Import Cerebrum modules
from brain import BrainModule
from vision import VisionModule
from motor import MotorInterface, ToolPresets, Stroke, StrokePoint


class CLIInterface:
    """
    Command-Line Interface for Cerebrum.
    
    Provides a text-based interface for:
    - Submitting reference images, sketches, or AI-generated images
    - Setting artistic goals
    - Reviewing Vision analysis and Brain tasks
    - Approving or rejecting suggestions
    - Controlling iteration loops
    
    Example:
        >>> config = SessionConfig(canvas_width=800, canvas_height=600)
        >>> interface = CLIInterface(config)
        >>> interface.start_session()
        >>> interface.set_goal("Draw a stylized female portrait")
        >>> interface.submit_reference("reference.png")
        >>> interface.run_iteration()
        >>> interface.end_session()
    """
    
    def __init__(self, config: Optional[SessionConfig] = None):
        """
        Initialize CLI interface.
        
        Args:
            config: Session configuration (uses defaults if None)
        """
        self.config = config or SessionConfig()
        self.session: Optional[Session] = None
        self.logger: Optional[InterfaceLogger] = None
        self.formatter = DisplayFormatter()
        
        # Initialize Cerebrum modules
        self.brain: Optional[BrainModule] = None
        self.vision: Optional[VisionModule] = None
        self.motor: Optional[MotorInterface] = None
        
        # State
        self.current_canvas_path: Optional[Path] = None
        self.current_reference_path: Optional[Path] = None
        self.current_tasks: List[Any] = []
        self.pending_decisions: List[Dict[str, Any]] = []
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new interface session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if self.session:
            raise RuntimeError("Session already started")
        
        # Generate session ID
        if not session_id:
            session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        # Create session
        self.session = Session(session_id=session_id, config=self.config)
        
        # Setup logging
        if self.config.log_file:
            log_file = self.config.log_file
        else:
            log_file = self.config.output_dir / f"{session_id}.log"
        
        self.logger = InterfaceLogger(log_file=log_file)
        self.logger.info(f"Session started: {session_id}")
        
        # Initialize modules
        if self.config.enable_brain:
            self.brain = BrainModule()
            self.logger.info("Brain module initialized")
        
        if self.config.enable_vision:
            self.vision = VisionModule()
            self.logger.info("Vision module initialized")
        
        # Initialize motor with simulation backend
        self.motor = MotorInterface(backend="simulation")
        self.logger.info("Motor module initialized")
        
        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(self.formatter.format_header("Cerebrum Interface"))
        print(f"Session ID: {session_id}")
        print(f"Output directory: {self.config.output_dir}")
        
        return session_id
    
    def end_session(self):
        """End the current session and save logs."""
        if not self.session:
            return
        
        self.session.complete()
        
        # Save session data
        session_file = self.config.output_dir / f"{self.session.session_id}.json"
        self.session.save(session_file)
        self.logger.info(f"Session saved to {session_file}")
        
        # Save event log
        log_file = self.config.output_dir / f"{self.session.session_id}_events.json"
        self.logger.save_event_log(log_file)
        self.logger.info(f"Event log saved to {log_file}")
        
        # Cleanup
        if self.motor:
            self.motor.close()
        if self.vision:
            self.vision.close()
        
        print(f"\nSession ended: {self.session.session_id}")
        print(f"Total inputs: {len(self.session.inputs)}")
        print(f"Total actions: {len(self.session.actions)}")
        print(f"Total iterations: {self.session.current_iteration}")
        
        self.session = None
    
    def set_goal(self, goal: str):
        """
        Set the artistic goal for the session.
        
        Args:
            goal: High-level artistic goal description
        """
        self._check_session()
        
        self.session.goal = goal
        user_input = UserInput(
            input_type=InputType.GOAL,
            value=goal,
            context="session_goal"
        )
        self.session.add_input(user_input)
        
        if self.brain:
            self.brain.set_goal(goal)
        
        self.logger.log_user_input("goal", goal, "session_goal")
        print(f"\nGoal set: {goal}")
    
    def submit_reference(self, image_path: Union[str, Path]) -> bool:
        """
        Submit a reference image.
        
        Args:
            image_path: Path to reference image
            
        Returns:
            True if successful
        """
        self._check_session()
        
        image_path = Path(image_path)
        if not image_path.exists():
            self.logger.error(f"Reference image not found: {image_path}")
            return False
        
        self.current_reference_path = image_path
        user_input = UserInput(
            input_type=InputType.REFERENCE,
            value=str(image_path),
            context="reference_submission"
        )
        self.session.add_input(user_input)
        
        self.logger.log_user_input("reference", str(image_path))
        print(f"\nReference submitted: {image_path.name}")
        
        return True
    
    def submit_sketch(self, image_path: Union[str, Path]) -> bool:
        """
        Submit a sketch image.
        
        Args:
            image_path: Path to sketch image
            
        Returns:
            True if successful
        """
        self._check_session()
        
        image_path = Path(image_path)
        if not image_path.exists():
            self.logger.error(f"Sketch image not found: {image_path}")
            return False
        
        # Load sketch as initial canvas
        self.motor.create_canvas(
            width=self.config.canvas_width,
            height=self.config.canvas_height
        )
        
        # Save as initial state
        canvas_path = self.config.output_dir / f"{self.session.session_id}_canvas_init.png"
        self.motor.save(str(canvas_path))
        self.current_canvas_path = canvas_path
        self.session.add_canvas_state(str(canvas_path))
        
        user_input = UserInput(
            input_type=InputType.SKETCH,
            value=str(image_path),
            context="sketch_submission"
        )
        self.session.add_input(user_input)
        
        self.logger.log_user_input("sketch", str(image_path))
        print(f"\nSketch submitted: {image_path.name}")
        
        return True
    
    def create_blank_canvas(self) -> bool:
        """
        Create a blank canvas.
        
        Returns:
            True if successful
        """
        self._check_session()
        
        self.motor.create_canvas(
            width=self.config.canvas_width,
            height=self.config.canvas_height
        )
        
        # Save initial state
        canvas_path = self.config.output_dir / f"{self.session.session_id}_canvas_init.png"
        self.motor.save(str(canvas_path))
        self.current_canvas_path = canvas_path
        self.session.add_canvas_state(str(canvas_path))
        
        self.logger.log_action("create_canvas", {
            "width": self.config.canvas_width,
            "height": self.config.canvas_height
        })
        print(f"\nBlank canvas created: {self.config.canvas_width}x{self.config.canvas_height}")
        
        return True
    
    def analyze_canvas(self) -> Optional[Any]:
        """
        Analyze current canvas with Vision module.
        
        Returns:
            AnalysisResult from Vision module, or None if failed
        """
        self._check_session()
        
        if not self.vision:
            self.logger.error("Vision module not enabled")
            return None
        
        if not self.current_canvas_path:
            self.logger.error("No canvas to analyze")
            return None
        
        self.logger.log_action("analyze_canvas", {"path": str(self.current_canvas_path)})
        
        # Analyze canvas
        result = self.vision.analyze(str(self.current_canvas_path))
        
        # Display results
        print(self.formatter.format_vision_result(result))
        
        return result
    
    def compare_to_reference(self) -> Optional[Any]:
        """
        Compare current canvas to reference image.
        
        Returns:
            ComparisonResult from Vision module, or None if failed
        """
        self._check_session()
        
        if not self.vision:
            self.logger.error("Vision module not enabled")
            return None
        
        if not self.current_canvas_path:
            self.logger.error("No canvas to compare")
            return None
        
        if not self.current_reference_path:
            self.logger.error("No reference image")
            return None
        
        self.logger.log_action("compare_to_reference", {
            "canvas": str(self.current_canvas_path),
            "reference": str(self.current_reference_path)
        })
        
        # Compare
        comparison = self.vision.compare_to(
            str(self.current_canvas_path),
            str(self.current_reference_path)
        )
        
        # Display results
        print(self.formatter.format_comparison_result(comparison))
        
        return comparison
    
    def plan_next_action(self) -> List[Any]:
        """
        Use Brain module to plan next actions based on Vision analysis.
        
        Returns:
            List of tasks created by Brain module
        """
        self._check_session()
        
        if not self.brain:
            self.logger.error("Brain module not enabled")
            return []
        
        if not self.vision:
            self.logger.error("Vision module not enabled")
            return []
        
        # Analyze canvas
        vision_result = self.analyze_canvas()
        if not vision_result:
            return []
        
        # Compare to reference if available
        comparison = None
        if self.current_reference_path:
            comparison = self.compare_to_reference()
        
        # Build vision data for Brain
        vision_data = self._build_vision_data(vision_result, comparison)
        
        # Plan actions
        self.logger.log_action("plan_next_action")
        tasks = self.brain.plan_next_action(vision_data)
        self.current_tasks = tasks
        
        # Display tasks
        print(self.formatter.format_tasks(tasks))
        
        return tasks
    
    def execute_task(self, task: Any, auto_approve: bool = False) -> bool:
        """
        Execute a task using Brain and Motor modules.
        
        Args:
            task: Task to execute
            auto_approve: Auto-approve without user confirmation
            
        Returns:
            True if executed
        """
        self._check_session()
        
        if not self.brain:
            self.logger.error("Brain module not enabled")
            return False
        
        # Get action plan
        plan = self.brain.get_action_plan(task)
        print(self.formatter.format_action_plan(plan))
        
        # Ask for approval if interactive
        if self.config.interactive and not auto_approve:
            decision = self._prompt_decision("Execute this plan?")
            if decision != UserDecision.APPROVE:
                self.logger.log_decision("reject", f"task_{task.task_id}", "user_rejected")
                return False
        
        # Execute actions
        self.logger.log_action("execute_task", {"task_id": task.task_id})
        print("\nExecuting actions...")
        
        for i, action in enumerate(plan.actions, 1):
            print(f"  [{i}/{len(plan.actions)}] {action.description}...")
            success = self.brain.delegate_to_motor(action, self.motor)
            if not success:
                self.logger.warning(f"Action {i} failed")
        
        # Save canvas state
        canvas_path = self.config.output_dir / f"{self.session.session_id}_canvas_iter{self.session.current_iteration}.png"
        self.motor.save(str(canvas_path))
        self.current_canvas_path = canvas_path
        self.session.add_canvas_state(str(canvas_path))
        
        print(f"✓ Task executed, canvas saved to {canvas_path.name}")
        
        return True
    
    def evaluate_result(self, task: Any, vision_before: Dict[str, Any], vision_after: Dict[str, Any]) -> Any:
        """
        Evaluate task execution result.
        
        Args:
            task: Executed task
            vision_before: Vision data before execution
            vision_after: Vision data after execution
            
        Returns:
            ExecutionResult from Brain module
        """
        self._check_session()
        
        if not self.brain:
            self.logger.error("Brain module not enabled")
            return None
        
        result = self.brain.evaluate_result(task, vision_before, vision_after)
        
        # Extract scores
        scores = {
            'before_proportion': vision_before.get('proportion_score', 0),
            'after_proportion': vision_after.get('proportion_score', 0),
            'before_symmetry': vision_before.get('symmetry_score', 0),
            'after_symmetry': vision_after.get('symmetry_score', 0)
        }
        
        # Display evaluation
        print(self.formatter.format_evaluation(result, scores))
        
        # Log evaluation
        self.logger.log_evaluation(task.description, scores, result.value)
        self.session.add_evaluation({
            'task_id': task.task_id,
            'result': result.value,
            'score_change': result.score_change,
            'confidence': result.confidence,
            'scores': scores
        })
        
        return result
    
    def run_iteration(self, auto_approve: bool = False) -> bool:
        """
        Run a single iteration of analysis, planning, and execution.
        
        Args:
            auto_approve: Auto-approve all decisions
            
        Returns:
            True if iteration completed
        """
        self._check_session()
        
        self.session.increment_iteration()
        iteration = self.session.current_iteration
        
        print(self.formatter.format_header(f"Iteration {iteration}"))
        self.logger.log_iteration(iteration, "Starting iteration")
        
        # Ensure we have a canvas
        if not self.current_canvas_path:
            print("No canvas found, creating blank canvas...")
            self.create_blank_canvas()
        
        # Analyze and plan
        tasks = self.plan_next_action()
        
        if not tasks:
            print("\nNo tasks created - iteration complete!")
            self.logger.log_iteration(iteration, "No tasks created")
            return True
        
        # Execute first task (or all if not interactive)
        task = tasks[0]
        
        # Get vision data before
        vision_before = self._get_vision_data()
        
        # Execute task
        success = self.execute_task(task, auto_approve=auto_approve)
        
        if success:
            # Get vision data after
            vision_after = self._get_vision_data()
            
            # Evaluate
            self.evaluate_result(task, vision_before, vision_after)
        
        self.logger.log_iteration(iteration, "Iteration complete")
        return True
    
    def run_batch_iterations(self, count: int, auto_approve: bool = True) -> int:
        """
        Run multiple iterations in batch mode.
        
        Args:
            count: Number of iterations to run
            auto_approve: Auto-approve all decisions
            
        Returns:
            Number of iterations completed
        """
        self._check_session()
        
        print(f"\nRunning {count} iterations in batch mode...")
        
        completed = 0
        for i in range(count):
            if self.session.current_iteration >= self.config.max_iterations:
                print(f"\nReached maximum iterations ({self.config.max_iterations})")
                break
            
            success = self.run_iteration(auto_approve=auto_approve)
            if success:
                completed += 1
            else:
                print(f"\nIteration {i+1} failed, stopping batch")
                break
        
        print(f"\nBatch complete: {completed}/{count} iterations")
        return completed
    
    def display_session_summary(self):
        """Display a summary of the current session."""
        self._check_session()
        
        print(self.formatter.format_header("Session Summary"))
        print(f"Session ID: {self.session.session_id}")
        print(f"Goal: {self.session.goal or 'Not set'}")
        print(f"Iterations: {self.session.current_iteration}")
        print(f"User inputs: {len(self.session.inputs)}")
        print(f"System actions: {len(self.session.actions)}")
        print(f"Evaluations: {len(self.session.evaluations)}")
        print(f"Canvas states: {len(self.session.canvas_states)}")
        
        if self.session.evaluations:
            print("\nRecent evaluations:")
            for eval_data in self.session.evaluations[-3:]:
                print(f"  - {eval_data.get('task_id', 'unknown')}: {eval_data.get('result', 'unknown')}")
    
    def _check_session(self):
        """Check if session is active."""
        if not self.session:
            raise RuntimeError("No active session. Call start_session() first.")
    
    def _build_vision_data(self, vision_result: Any, comparison: Optional[Any] = None) -> Dict[str, Any]:
        """Build vision data dictionary for Brain module."""
        data = {
            'has_pose': vision_result.has_pose(),
            'pose_errors': [],
            'refinement_areas': [],
            'proportion_issues': False,
            'symmetry_issues': False,
            'proportion_score': 0.7,
            'symmetry_score': 0.7,
            'detection_confidence': vision_result.detection_confidence
        }
        
        if vision_result.proportion_metrics:
            data['proportion_score'] = vision_result.proportion_metrics.overall_score
            data['proportion_issues'] = vision_result.proportion_metrics.overall_score < 0.7
        
        if vision_result.symmetry_metrics:
            data['symmetry_score'] = vision_result.symmetry_metrics.overall_score
            data['symmetry_issues'] = vision_result.symmetry_metrics.overall_score < 0.7
        
        if comparison:
            data['overall_similarity'] = comparison.overall_similarity
        
        return data
    
    def _get_vision_data(self) -> Dict[str, Any]:
        """Get current vision data."""
        if not self.vision or not self.current_canvas_path:
            return {}
        
        result = self.vision.analyze(str(self.current_canvas_path))
        return self._build_vision_data(result)
    
    def _prompt_decision(self, message: str) -> UserDecision:
        """
        Prompt user for a decision.
        
        Args:
            message: Prompt message
            
        Returns:
            UserDecision
        """
        prompt = self.formatter.format_prompt(message, ["approve", "reject", "skip"])
        
        while True:
            response = input(prompt).strip().lower()
            
            if response in ['approve', 'a', 'y', 'yes']:
                return UserDecision.APPROVE
            elif response in ['reject', 'r', 'n', 'no']:
                return UserDecision.REJECT
            elif response in ['skip', 's']:
                return UserDecision.SKIP
            else:
                print("Invalid response. Please enter 'approve', 'reject', or 'skip'.")
