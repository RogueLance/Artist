# Brain System - Planning and Decision Making Engine

## Overview

The Brain System is the central decision-making component of the Cerebrum AI art platform. It interprets visual feedback from the Vision System and decides what corrective actions or stylistic progressions should occur, mimicking the cognitive planning process of a human artist.

## Purpose

The Brain System acts as the executive logic controller that:
- Receives vision analysis input
- Decides what needs to be done next
- Translates high-level goals into concrete drawing plans
- Manages task prioritization and scheduling
- Evaluates results and schedules refinements
- Interfaces cleanly with Motor and Vision systems

## Architecture

### Components

The Brain System consists of four main components:

```
┌─────────────────────────────────────────────┐
│           BrainModule (Main API)            │
│  - plan_next_action(vision_data)            │
│  - evaluate_result()                        │
│  - schedule_refinement_task()               │
│  - delegate_to_motor()                      │
└──────────┬──────────────────────────────────┘
           │
    ┌──────┴────────┐
    │               │
┌───▼────┐  ┌──────▼────┐  ┌──────────────┐
│ Task   │  │  Planner  │  │    State     │
│Manager │  │           │  │   Tracker    │
└────────┘  └───────────┘  └──────────────┘
```

#### 1. BrainModule

The main API that provides high-level methods for planning and decision-making.

**Key Methods:**
- `plan_next_action(vision_data)` - Analyze vision feedback and create tasks
- `get_action_plan(task)` - Generate concrete drawing actions for a task
- `evaluate_result(task, before, after)` - Evaluate if task was successful
- `schedule_refinement_task(task)` - Schedule task for retry
- `delegate_to_motor(action, motor)` - Execute action via Motor System

#### 2. TaskManager

Manages task lifecycle, prioritization, and scheduling.

**Features:**
- Task creation with type, priority, and target area
- Status tracking (pending, in_progress, completed, failed)
- Retry logic with configurable max retries
- Task statistics and reporting

#### 3. Planner

Translates vision feedback into actionable drawing plans.

**Features:**
- Vision analysis interpretation
- Task generation from detected issues
- Action plan creation with concrete drawing operations
- Execution result evaluation
- Retry decision logic

#### 4. StateTracker

Tracks the current state of the Brain System.

**Features:**
- Goal management
- Task state tracking (active, pending, completed, failed)
- Execution history recording
- Context management
- Iteration counting

## Data Models

### Task

Represents a high-level task to accomplish.

```python
class TaskType(Enum):
    FIX_POSE = "fix_pose"
    REFINE_ANATOMY = "refine_anatomy"
    ENHANCE_SILHOUETTE = "enhance_silhouette"
    FIX_PROPORTIONS = "fix_proportions"
    IMPROVE_SYMMETRY = "improve_symmetry"
    ALIGN_EDGES = "align_edges"
    FIX_HAND = "fix_hand"
    FIX_FACE = "fix_face"
    ADD_DETAIL = "add_detail"
    CORRECT_STRUCTURE = "correct_structure"

class TaskPriority(Enum):
    CRITICAL = 1  # Structural issues that must be fixed
    HIGH = 2      # Important issues affecting overall quality
    MEDIUM = 3    # Noticeable issues that should be addressed
    LOW = 4       # Minor refinements

@dataclass
class Task:
    task_id: str
    task_type: TaskType
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    target_area: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
```

### ActionPlan

A concrete plan of drawing actions to accomplish a task.

```python
class ActionType(Enum):
    DRAW_STROKE = "draw_stroke"
    ERASE_STROKE = "erase_stroke"
    SWITCH_TOOL = "switch_tool"
    CHANGE_LAYER = "change_layer"
    ADJUST_COLOR = "adjust_color"
    REFINE_AREA = "refine_area"

@dataclass
class DrawingAction:
    action_id: str
    action_type: ActionType
    description: str
    tool_config: Optional[Dict[str, Any]] = None
    stroke_points: Optional[List[Dict[str, float]]] = None
    target_region: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: float = 1.0

@dataclass
class ActionPlan:
    plan_id: str
    task_id: str
    actions: List[DrawingAction] = field(default_factory=list)
    estimated_total_duration: float = 0.0
    success_criteria: Dict[str, Any] = field(default_factory=dict)
```

### BrainState

Current state of the Brain System.

```python
@dataclass
class BrainState:
    current_goal: Optional[str] = None
    active_tasks: List[Task] = field(default_factory=list)
    pending_tasks: List[Task] = field(default_factory=list)
    completed_tasks: List[Task] = field(default_factory=list)
    failed_tasks: List[Task] = field(default_factory=list)
    current_action_plan: Optional[ActionPlan] = None
    execution_history: List[ExecutionHistory] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    iteration_count: int = 0
```

## Usage Examples

### Basic Usage

```python
from brain import BrainModule
from vision import VisionModule
from motor import MotorInterface

# Initialize systems
brain = BrainModule()
vision = VisionModule()
motor = MotorInterface(backend="simulation")

# Set artistic goal
brain.set_goal("Draw an accurate human figure")

# Create canvas and initial drawing
motor.create_canvas(800, 600)
# ... draw initial sketch ...
motor.save("canvas.png")

# Analyze and plan
vision_data = vision.analyze("canvas.png")
tasks = brain.plan_next_action(vision_data)

print(f"Created {len(tasks)} tasks")
for task in tasks:
    print(f"  - {task.description} (priority: {task.priority.value})")
```

### Executing Tasks

```python
# Get next task
task = brain.get_next_task()
if task:
    # Get action plan
    plan = brain.get_action_plan(task)
    
    print(f"Executing task: {task.description}")
    print(f"  Actions: {len(plan.actions)}")
    
    # Capture before state
    motor.save("before.png")
    vision_before = vision.analyze("before.png")
    
    # Execute actions
    for action in plan.actions:
        success = brain.delegate_to_motor(action, motor)
        if not success:
            print(f"  Action failed: {action.description}")
    
    # Capture after state
    motor.save("after.png")
    vision_after = vision.analyze("after.png")
    
    # Evaluate result
    result = brain.evaluate_result(task, vision_before, vision_after)
    print(f"  Result: {result.value}")
```

### Iterative Refinement

```python
# Iterative refinement loop
max_iterations = 5
for iteration in range(max_iterations):
    brain.increment_iteration()
    
    # Analyze current state
    motor.save(f"iteration_{iteration}.png")
    vision_data = vision.analyze(f"iteration_{iteration}.png")
    
    # Plan next actions
    tasks = brain.plan_next_action(vision_data, auto_schedule=True)
    
    if not tasks:
        print("No more tasks - drawing complete!")
        break
    
    # Execute pending tasks
    while True:
        task = brain.get_next_task()
        if not task:
            break
        
        # Execute task workflow
        plan = brain.get_action_plan(task)
        
        # Capture before
        vision_before = vision.analyze(f"iteration_{iteration}.png")
        
        # Execute actions
        for action in plan.actions:
            brain.delegate_to_motor(action, motor)
        
        # Capture after and evaluate
        motor.save(f"iteration_{iteration}_result.png")
        vision_after = vision.analyze(f"iteration_{iteration}_result.png")
        result = brain.evaluate_result(task, vision_before, vision_after)
        
        print(f"Task {task.description}: {result.value}")

# Get statistics
stats = brain.get_statistics()
print(f"\nCompleted {stats['task_stats']['completed']} tasks")
print(f"Failed {stats['task_stats']['failed']} tasks")
print(f"Total iterations: {stats['iteration_count']}")
```

### Integration with Vision System

```python
# Use vision comparison for refinement
reference_img = "reference_pose.png"
canvas_img = "canvas.png"

# Compare to reference
comparison = vision.compare_to(canvas_img, reference_img)
errors = vision.detect_pose_errors(canvas_img, reference_img)
areas = vision.highlight_areas_needing_refinement(canvas_img, reference_img)

# Create vision data for Brain
vision_data = {
    "has_pose": comparison.canvas_pose is not None,
    "pose_errors": errors,
    "refinement_areas": areas,
    "proportion_issues": comparison.proportion_metrics.overall_score < 0.7,
    "symmetry_issues": comparison.symmetry_metrics.overall_score < 0.7,
    "proportion_score": comparison.proportion_metrics.overall_score,
    "symmetry_score": comparison.symmetry_metrics.overall_score,
    "overall_similarity": comparison.overall_similarity,
}

# Plan based on vision feedback
tasks = brain.plan_next_action(vision_data)
```

## Decision-Making Process

The Brain System follows this decision-making process:

1. **Analysis**: Receive vision feedback about canvas state
2. **Interpretation**: Identify issues and areas needing work
3. **Planning**: Create tasks with priorities
4. **Scheduling**: Order tasks by priority
5. **Execution**: Generate action plans and delegate to Motor
6. **Evaluation**: Compare before/after states
7. **Iteration**: Retry failed tasks or move to next task

### Task Prioritization

Tasks are prioritized as follows:

1. **CRITICAL** - Structural issues (e.g., missing pose, broken anatomy)
2. **HIGH** - Important quality issues (e.g., wrong proportions, asymmetry)
3. **MEDIUM** - Noticeable refinements (e.g., hand details, face features)
4. **LOW** - Minor polish (e.g., edge alignment, small details)

### Retry Logic

The Brain System implements intelligent retry logic:

- Tasks can be retried up to `max_retries` times (default: 3)
- Failed tasks are automatically scheduled for retry if possible
- CRITICAL tasks may retry on PARTIAL success
- After max retries, tasks are marked as permanently failed

## Real Artist Parallels

The Brain System mimics human artistic cognition:

| Human Artist | Brain System |
|--------------|--------------|
| "This hand needs work" | Creates FIX_HAND task |
| "That leg is too short" | Creates FIX_PROPORTIONS task |
| Decides to refine an area | Generates refinement action plan |
| Erases and redraws | Creates erase + draw actions |
| Checks progress against reference | Uses vision comparison |
| Iterates until satisfied | Loops through refinement cycles |

## API Reference

### BrainModule

#### `__init__()`
Initialize the Brain Module.

#### `set_goal(goal: str)`
Set the current artistic goal.

#### `plan_next_action(vision_data: Dict[str, Any], auto_schedule: bool = True) -> List[Task]`
Analyze vision feedback and create tasks.

**Parameters:**
- `vision_data`: Vision analysis result
- `auto_schedule`: Automatically schedule tasks

**Returns:** List of created tasks

#### `get_action_plan(task: Task) -> ActionPlan`
Get concrete action plan for a task.

**Parameters:**
- `task`: Task to plan for

**Returns:** ActionPlan with drawing actions

#### `evaluate_result(task: Task, vision_before: Dict, vision_after: Dict) -> ExecutionResult`
Evaluate task execution result.

**Parameters:**
- `task`: Executed task
- `vision_before`: Vision analysis before execution
- `vision_after`: Vision analysis after execution

**Returns:** ExecutionResult (SUCCESS/PARTIAL/FAILURE)

#### `schedule_refinement_task(task: Task)`
Schedule a task for refinement/retry.

#### `delegate_to_motor(action: DrawingAction, motor_interface: MotorInterface) -> bool`
Execute action via Motor System.

**Parameters:**
- `action`: Drawing action to execute
- `motor_interface`: MotorInterface instance

**Returns:** True if successful

#### `get_statistics() -> Dict[str, Any]`
Get brain system statistics.

**Returns:** Dictionary with task stats, state summary, iteration count

#### `reset()`
Reset the brain module to initial state.

## Integration Points

### With Motor System

The Brain System delegates drawing actions to the Motor System:

```python
# Brain creates action
action = DrawingAction(
    action_id="action-1",
    action_type=ActionType.DRAW_STROKE,
    description="Draw correction",
    tool_config={"tool_type": "pencil", "size": 2.0},
    stroke_points=[...]
)

# Delegate to Motor
brain.delegate_to_motor(action, motor)
```

### With Vision System

The Brain System uses Vision feedback for decision-making:

```python
# Vision analyzes canvas
result = vision.analyze("canvas.png")

# Brain plans based on analysis
tasks = brain.plan_next_action({
    "has_pose": result.has_pose(),
    "pose_errors": vision.detect_pose_errors(...),
    "refinement_areas": vision.highlight_areas_needing_refinement(...)
})
```

## Technical Implementation

### Task Management

Tasks flow through these states:
- `PENDING` → `IN_PROGRESS` → `COMPLETED`
- `PENDING` → `IN_PROGRESS` → `FAILED` → `PENDING` (retry)
- `FAILED` (max retries exceeded)

### Planning Algorithm

The Planner uses rule-based logic to translate vision feedback:

1. **Issue Detection**: Identify problems from vision analysis
2. **Task Generation**: Create tasks for each issue
3. **Action Planning**: Generate concrete actions for tasks
4. **Success Criteria**: Define metrics for evaluation

### State Tracking

The StateTracker maintains:
- Current goal and context
- Task queues (pending, active, completed, failed)
- Execution history with metrics
- Iteration count for refinement cycles

## Performance

- **Task Creation**: < 1ms per task
- **Action Planning**: < 5ms per plan
- **State Updates**: < 1ms
- **Memory Usage**: ~10MB (with 100 tasks in history)

## Future Enhancements

Potential improvements for future versions:

1. **LLM Integration**: Use LLM (OpenAI, Ollama) for intelligent planning
2. **Learning**: Learn from successful/failed executions
3. **Style Guidance**: Integrate with Style AI for artistic decisions
4. **Advanced Planning**: Multi-step planning with dependencies
5. **Parallel Execution**: Execute independent tasks in parallel
6. **Visual Feedback**: Real-time visualization of plans

## Testing

The Brain System includes comprehensive tests:

- **33 unit tests** covering all components
- Task lifecycle management tests
- Planning logic tests
- State tracking tests
- Integration tests with Motor System

Run tests:
```bash
pytest tests/brain/ -v
```

## Examples

See `examples/brain_usage.py` for complete working examples.

## License

MIT License - See LICENSE file for details.
