# Interface System Documentation

## Overview

The Interface System provides a user-friendly command-line interface (CLI) for interacting with the Cerebrum AI-driven art platform. It allows users to guide the creative process, provide feedback, review system decisions, and control the iterative refinement workflow.

## Purpose

The Interface System serves as the human-in-the-loop component, enabling:

- **User Guidance**: Submit reference images, sketches, or AI-generated images
- **Goal Setting**: Define artistic objectives and project requirements
- **Review & Feedback**: Inspect Vision analysis results and Brain task plans
- **Decision Control**: Approve or reject system suggestions
- **Iteration Management**: Control refinement loops manually or in batch mode
- **Progress Tracking**: Monitor actions, evaluations, and canvas states

## Architecture

The Interface System integrates with all other Cerebrum components:

```
┌─────────────────────────────────────────┐
│         User (CLI Interface)            │
└─────────────┬───────────────────────────┘
              │
    ┌─────────▼─────────┐
    │  Interface System │
    │  - Session Mgmt   │
    │  - Logging        │
    │  - Display        │
    └──┬─────┬─────┬────┘
       │     │     │
   ┌───▼─┐ ┌▼───┐ ┌▼────┐
   │Brain│ │Vision│Motor│
   └─────┘ └─────┘ └─────┘
```

## Components

### 1. CLI Interface (`CLIInterface`)

Main interface class providing user interaction capabilities.

**Key Methods:**
- `start_session()` - Initialize a new working session
- `end_session()` - Complete and save session data
- `set_goal(goal)` - Set artistic goal
- `submit_reference(path)` - Submit reference image
- `submit_sketch(path)` - Submit initial sketch
- `create_blank_canvas()` - Create blank canvas
- `analyze_canvas()` - Analyze current canvas with Vision
- `compare_to_reference()` - Compare canvas to reference
- `plan_next_action()` - Use Brain to plan next steps
- `execute_task(task)` - Execute a Brain task
- `run_iteration()` - Run single refinement iteration
- `run_batch_iterations(count)` - Run multiple iterations
- `display_session_summary()` - Show session statistics

### 2. Session Management

**Session** - Tracks all activities during a working session:
- User inputs (goals, references, sketches)
- System actions (analyze, plan, execute)
- Evaluation results and scores
- Canvas state history
- Iteration count

**SessionConfig** - Configuration for interface behavior:
- Canvas dimensions
- Maximum iterations
- Auto-save settings
- Output directory
- Module enable/disable flags
- Interactive mode toggle

### 3. User Input Models

**UserInput** - Represents a single user input action:
- Input type (goal, reference, sketch, decision)
- Value and timestamp
- Metadata and context

**UserDecision** - Decision types:
- APPROVE - Accept suggestion
- REJECT - Decline suggestion
- SKIP - Skip for now
- MODIFY - Request modification

### 4. Logging System

**InterfaceLogger** - Comprehensive logging of all events:
- User inputs
- System actions
- Evaluations and scores
- Decisions and iterations
- Event log export to JSON

### 5. Display Formatting

**DisplayFormatter** - Format information for user display:
- Headers and sections
- Vision analysis results
- Brain tasks and action plans
- Comparison metrics
- Evaluation results
- User prompts

## Usage Examples

### Basic Usage

```python
from interface import CLIInterface, SessionConfig

# Create configuration
config = SessionConfig(
    canvas_width=800,
    canvas_height=600,
    max_iterations=10,
    output_dir=Path("output"),
    interactive=True
)

# Initialize interface
interface = CLIInterface(config)

# Start session
session_id = interface.start_session()

# Set goal
interface.set_goal("Draw a stylized female portrait with strong hands")

# Create canvas
interface.create_blank_canvas()

# Run an iteration
interface.run_iteration()

# End session
interface.end_session()
```

### With Reference Image

```python
# Start session
interface = CLIInterface(config)
interface.start_session()

# Set goal and submit reference
interface.set_goal("Match reference pose and proportions")
interface.submit_reference("reference.png")

# Analyze and compare
interface.analyze_canvas()
interface.compare_to_reference()

# Plan and execute
tasks = interface.plan_next_action()
if tasks:
    interface.execute_task(tasks[0])

interface.end_session()
```

### Batch Iteration Mode

```python
# Start session with sketch
interface = CLIInterface(config)
interface.start_session()
interface.set_goal("Refine figure drawing")
interface.submit_sketch("initial_sketch.png")

# Run multiple iterations automatically
completed = interface.run_batch_iterations(5, auto_approve=True)

print(f"Completed {completed} iterations")
interface.end_session()
```

### Manual Review Workflow

```python
# Interactive mode
config = SessionConfig(interactive=True)
interface = CLIInterface(config)
interface.start_session()

interface.set_goal("Create accurate portrait")
interface.submit_reference("reference.png")

# Run iteration with manual approval
interface.run_iteration(auto_approve=False)
# User will be prompted to approve each action

interface.end_session()
```

## Session Data

Each session creates several files in the output directory:

1. **Session JSON** (`session-{id}.json`):
   - Session metadata
   - User inputs
   - System actions
   - Evaluations
   - Canvas state history

2. **Event Log** (`session-{id}_events.json`):
   - Chronological event stream
   - Detailed timestamps
   - Complete action history

3. **Canvas States** (`session-{id}_canvas_iter{n}.png`):
   - Canvas after each iteration
   - Allows review of progression

4. **Log File** (`session-{id}.log`):
   - Human-readable log
   - Console output capture

## Interactive Mode

When `interactive=True`, the interface prompts for user decisions:

```
Execute this plan? [approve/reject/skip]: 
```

User responses:
- `approve`, `a`, `y`, `yes` - Approve and execute
- `reject`, `r`, `n`, `no` - Reject and skip
- `skip`, `s` - Skip this task

## Configuration Options

### Canvas Settings
- `canvas_width` - Canvas width in pixels (default: 800)
- `canvas_height` - Canvas height in pixels (default: 600)

### Iteration Control
- `max_iterations` - Maximum iterations allowed (default: 10)
- `auto_save` - Save canvas after each iteration (default: True)

### Module Control
- `enable_vision` - Enable Vision module (default: True)
- `enable_brain` - Enable Brain module (default: True)

### Output Settings
- `output_dir` - Output directory path (default: "output")
- `log_file` - Custom log file path (optional)

### Interaction
- `interactive` - Prompt for user decisions (default: True)

## Logged Information

### User Inputs
- Goal setting
- Reference/sketch submission
- Decisions (approve/reject)
- Commands

### System Actions
- Canvas creation
- Vision analysis
- Brain planning
- Task execution

### Evaluations
- Task results (success/partial/failure)
- Score changes
- Confidence levels
- Before/after metrics

## Best Practices

1. **Set Clear Goals**: Define specific, actionable artistic goals
2. **Use References**: Provide reference images when available
3. **Review Regularly**: Check Vision analysis and Brain plans
4. **Iterative Refinement**: Run multiple small iterations rather than one large batch
5. **Save Sessions**: Session data enables reviewing and learning from past work
6. **Monitor Progress**: Check evaluation scores to track improvement

## Real Artist Parallel

The Interface System mirrors the feedback loop between:
- **Artist and Client**: User provides goals and approves/rejects suggestions
- **Artist and Editor**: System presents options, user guides direction
- **Self-Critique**: Artist reviews their work and decides next steps

The interface enables curated interaction without micromanagement, allowing the AI to work autonomously while keeping the human in control.

## Integration with Other Systems

### With Brain System
- Reviews Brain task plans
- Approves/rejects suggested actions
- Triggers execution via Motor

### With Vision System
- Displays Vision analysis results
- Shows comparison metrics
- Highlights areas needing refinement

### With Motor System
- Creates and manages canvas
- Executes drawing actions
- Saves canvas states

## Future Enhancements

Potential improvements for future milestones:

- **GUI Interface**: Visual interface with image previews
- **Real-time Preview**: Live canvas updates during execution
- **Undo/Redo**: Revert iterations or specific actions
- **Style Library**: Save and load style presets
- **Collaboration**: Multi-user sessions and feedback
- **Advanced Visualization**: Overlay Vision analysis on canvas
- **Voice Commands**: Voice-based interaction

## API Reference

See [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation.

## Examples

See the [examples/interface_usage.py](../examples/interface_usage.py) file for complete usage examples.
