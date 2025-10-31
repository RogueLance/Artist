"""
Tests for Brain System core functionality.

Tests task management, planning, state tracking, and the main BrainModule API.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime

from brain import (
    BrainModule,
    TaskManager,
    Planner,
    StateTracker,
    Task,
    TaskType,
    TaskStatus,
    TaskPriority,
    ActionPlan,
    DrawingAction,
    ActionType,
    BrainState,
    ExecutionHistory,
)
from brain.models.brain_state import ExecutionResult


class TestTask:
    """Test Task model."""
    
    def test_create_task(self):
        """Test task creation."""
        task = Task(
            task_id="test-1",
            task_type=TaskType.FIX_HAND,
            description="Fix hand pose"
        )
        assert task.task_id == "test-1"
        assert task.task_type == TaskType.FIX_HAND
        assert task.description == "Fix hand pose"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
    
    def test_task_status_transitions(self):
        """Test task status transitions."""
        task = Task(
            task_id="test-1",
            task_type=TaskType.FIX_HAND,
            description="Fix hand"
        )
        
        # Start as pending
        assert task.status == TaskStatus.PENDING
        
        # Mark in progress
        task.mark_in_progress()
        assert task.status == TaskStatus.IN_PROGRESS
        
        # Mark completed
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
    
    def test_task_retry(self):
        """Test task retry logic."""
        task = Task(
            task_id="test-1",
            task_type=TaskType.FIX_HAND,
            description="Fix hand",
            max_retries=3
        )
        
        # Fail task
        task.mark_failed("Error message")
        assert task.status == TaskStatus.FAILED
        assert task.retry_count == 1
        assert task.can_retry()
        
        # Retry
        task.retry()
        assert task.status == TaskStatus.PENDING
        assert task.error_message is None
        
        # Fail and retry until max retries
        task.mark_failed("Error")
        task.retry()
        assert task.retry_count == 2
        assert task.can_retry()
        
        task.mark_failed("Error")
        assert task.retry_count == 3
        assert not task.can_retry()
        
        # Cannot retry anymore
        with pytest.raises(ValueError):
            task.retry()
    
    def test_task_serialization(self):
        """Test task to_dict."""
        task = Task(
            task_id="test-1",
            task_type=TaskType.FIX_HAND,
            description="Fix hand",
            target_area={"x": 100, "y": 100, "width": 50, "height": 50}
        )
        
        data = task.to_dict()
        assert data["task_id"] == "test-1"
        assert data["task_type"] == "fix_hand"
        assert data["description"] == "Fix hand"
        assert data["target_area"] == {"x": 100, "y": 100, "width": 50, "height": 50}


class TestActionPlan:
    """Test ActionPlan model."""
    
    def test_create_action_plan(self):
        """Test action plan creation."""
        plan = ActionPlan(
            plan_id="plan-1",
            task_id="task-1"
        )
        assert plan.plan_id == "plan-1"
        assert plan.task_id == "task-1"
        assert len(plan.actions) == 0
        assert plan.estimated_total_duration == 0.0
    
    def test_add_actions(self):
        """Test adding actions to plan."""
        plan = ActionPlan(plan_id="plan-1", task_id="task-1")
        
        action1 = DrawingAction(
            action_id="action-1",
            action_type=ActionType.DRAW_STROKE,
            description="Draw",
            estimated_duration=2.0
        )
        action2 = DrawingAction(
            action_id="action-2",
            action_type=ActionType.ERASE_STROKE,
            description="Erase",
            estimated_duration=1.0
        )
        
        plan.add_action(action1)
        plan.add_action(action2)
        
        assert len(plan.actions) == 2
        assert plan.estimated_total_duration == 3.0
    
    def test_get_next_action(self):
        """Test getting next action."""
        plan = ActionPlan(plan_id="plan-1", task_id="task-1")
        
        assert plan.get_next_action() is None
        
        action = DrawingAction(
            action_id="action-1",
            action_type=ActionType.DRAW_STROKE,
            description="Draw"
        )
        plan.add_action(action)
        
        next_action = plan.get_next_action()
        assert next_action is not None
        assert next_action.action_id == "action-1"
    
    def test_remove_action(self):
        """Test removing action."""
        plan = ActionPlan(plan_id="plan-1", task_id="task-1")
        
        action = DrawingAction(
            action_id="action-1",
            action_type=ActionType.DRAW_STROKE,
            description="Draw",
            estimated_duration=2.0
        )
        plan.add_action(action)
        
        assert plan.remove_action("action-1")
        assert len(plan.actions) == 0
        assert plan.estimated_total_duration == 0.0
        
        assert not plan.remove_action("nonexistent")


class TestBrainState:
    """Test BrainState model."""
    
    def test_create_brain_state(self):
        """Test brain state creation."""
        state = BrainState()
        assert state.current_goal is None
        assert len(state.active_tasks) == 0
        assert len(state.pending_tasks) == 0
        assert state.iteration_count == 0
    
    def test_add_task(self):
        """Test adding tasks."""
        state = BrainState()
        
        task1 = Task(task_id="t1", task_type=TaskType.FIX_HAND, description="Fix hand", priority=TaskPriority.HIGH)
        task2 = Task(task_id="t2", task_type=TaskType.FIX_FACE, description="Fix face", priority=TaskPriority.CRITICAL)
        
        state.add_task(task1)
        state.add_task(task2)
        
        # Should be sorted by priority
        assert len(state.pending_tasks) == 2
        assert state.pending_tasks[0].task_id == "t2"  # CRITICAL first
        assert state.pending_tasks[1].task_id == "t1"  # HIGH second
    
    def test_task_lifecycle(self):
        """Test task lifecycle management."""
        state = BrainState()
        task = Task(task_id="t1", task_type=TaskType.FIX_HAND, description="Fix hand")
        
        # Add to pending
        state.add_task(task)
        assert len(state.pending_tasks) == 1
        
        # Activate
        state.activate_task(task)
        assert len(state.pending_tasks) == 0
        assert len(state.active_tasks) == 1
        assert task.status == TaskStatus.IN_PROGRESS
        
        # Complete
        state.complete_task(task)
        assert len(state.active_tasks) == 0
        assert len(state.completed_tasks) == 1
        assert task.status == TaskStatus.COMPLETED
    
    def test_task_retry(self):
        """Test task retry logic."""
        state = BrainState()
        task = Task(task_id="t1", task_type=TaskType.FIX_HAND, description="Fix hand", max_retries=2)
        
        state.add_task(task)
        state.activate_task(task)
        
        # Fail task (should retry, retry_count=1)
        state.fail_task(task, "Error")
        assert len(state.active_tasks) == 0
        assert len(state.pending_tasks) == 1
        assert task.retry_count == 1
        
        # Fail again (max retries exceeded after this failure, cannot retry)
        state.activate_task(task)
        state.fail_task(task, "Error")
        assert len(state.pending_tasks) == 0
        assert len(state.failed_tasks) == 1
        assert task.retry_count == 2
    
    def test_execution_history(self):
        """Test execution history."""
        state = BrainState()
        
        history = ExecutionHistory(
            execution_id="e1",
            task_id="t1",
            result=ExecutionResult.SUCCESS
        )
        
        state.record_execution(history)
        assert len(state.execution_history) == 1
        
        recent = state.get_recent_executions(limit=5)
        assert len(recent) == 1


class TestTaskManager:
    """Test TaskManager."""
    
    def test_create_task_manager(self):
        """Test task manager creation."""
        manager = TaskManager()
        assert len(manager.tasks) == 0
    
    def test_create_task(self):
        """Test task creation."""
        manager = TaskManager()
        
        task = manager.create_task(
            task_type=TaskType.FIX_HAND,
            description="Fix hand",
            priority=TaskPriority.HIGH
        )
        
        assert task.task_id is not None
        assert task.task_type == TaskType.FIX_HAND
        assert task.priority == TaskPriority.HIGH
        assert len(manager.tasks) == 1
    
    def test_get_tasks_by_status(self):
        """Test getting tasks by status."""
        manager = TaskManager()
        
        task1 = manager.create_task(TaskType.FIX_HAND, "Task 1")
        task2 = manager.create_task(TaskType.FIX_FACE, "Task 2")
        
        manager.update_task_status(task1.task_id, TaskStatus.IN_PROGRESS)
        
        pending = manager.get_tasks_by_status(TaskStatus.PENDING)
        in_progress = manager.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        
        assert len(pending) == 1
        assert len(in_progress) == 1
    
    def test_get_statistics(self):
        """Test getting statistics."""
        manager = TaskManager()
        
        task1 = manager.create_task(TaskType.FIX_HAND, "Task 1")
        task2 = manager.create_task(TaskType.FIX_FACE, "Task 2")
        
        manager.update_task_status(task1.task_id, TaskStatus.COMPLETED)
        
        stats = manager.get_statistics()
        assert stats["total"] == 2
        assert stats["pending"] == 1
        assert stats["completed"] == 1


class TestPlanner:
    """Test Planner."""
    
    def test_create_planner(self):
        """Test planner creation."""
        planner = Planner()
        assert planner is not None
    
    def test_analyze_vision_feedback(self):
        """Test analyzing vision feedback."""
        planner = Planner()
        
        vision_result = {
            "has_pose": True,
            "pose_errors": ["Hand proportions incorrect"],
            "refinement_areas": [
                {"type": "hand", "region": {"x": 100, "y": 100, "width": 50, "height": 50}}
            ],
            "proportion_issues": True,
            "symmetry_issues": False
        }
        
        tasks = planner.analyze_vision_feedback(vision_result)
        
        assert len(tasks) > 0
        # Should create tasks for pose errors, refinement areas, and proportion issues
        assert any(t.task_type == TaskType.FIX_PROPORTIONS for t in tasks)
    
    def test_create_action_plan(self):
        """Test creating action plan."""
        planner = Planner()
        
        task = Task(
            task_id="t1",
            task_type=TaskType.FIX_HAND,
            description="Fix hand",
            target_area={"x": 100, "y": 100, "width": 50, "height": 50}
        )
        
        plan = planner.create_action_plan(task)
        
        assert plan.task_id == task.task_id
        assert len(plan.actions) > 0
    
    def test_evaluate_result(self):
        """Test evaluating execution result."""
        planner = Planner()
        
        task = Task(task_id="t1", task_type=TaskType.FIX_HAND, description="Fix hand")
        
        vision_before = {"proportion_score": 0.5, "symmetry_score": 0.5}
        vision_after = {"proportion_score": 0.8, "symmetry_score": 0.8}
        
        result = planner.evaluate_execution_result(task, vision_before, vision_after)
        
        assert result == ExecutionResult.SUCCESS


class TestStateTracker:
    """Test StateTracker."""
    
    def test_create_state_tracker(self):
        """Test state tracker creation."""
        tracker = StateTracker()
        assert tracker.state is not None
    
    def test_set_goal(self):
        """Test setting goal."""
        tracker = StateTracker()
        tracker.set_goal("Draw accurate figure")
        assert tracker.get_goal() == "Draw accurate figure"
    
    def test_task_management(self):
        """Test task management."""
        tracker = StateTracker()
        
        task = Task(task_id="t1", task_type=TaskType.FIX_HAND, description="Fix hand")
        
        tracker.add_task(task)
        assert tracker.get_next_task() is not None
        
        tracker.activate_task(task)
        tracker.complete_task(task)
        
        assert tracker.get_next_task() is None
    
    def test_execution_tracking(self):
        """Test execution tracking."""
        tracker = StateTracker()
        
        tracker.record_execution(
            execution_id="e1",
            task_id="t1",
            result=ExecutionResult.SUCCESS
        )
        
        recent = tracker.get_recent_executions(limit=5)
        assert len(recent) == 1
    
    def test_iteration_count(self):
        """Test iteration counting."""
        tracker = StateTracker()
        
        assert tracker.get_iteration_count() == 0
        
        tracker.increment_iteration()
        assert tracker.get_iteration_count() == 1


class TestBrainModule:
    """Test BrainModule main API."""
    
    def test_create_brain_module(self):
        """Test brain module creation."""
        brain = BrainModule()
        assert brain is not None
        assert brain.task_manager is not None
        assert brain.planner is not None
        assert brain.state_tracker is not None
    
    def test_set_goal(self):
        """Test setting goal."""
        brain = BrainModule()
        brain.set_goal("Draw accurate figure")
        assert brain.get_goal() == "Draw accurate figure"
    
    def test_plan_next_action(self):
        """Test planning next action."""
        brain = BrainModule()
        
        vision_data = {
            "has_pose": True,
            "pose_errors": ["Hand incorrect"],
            "refinement_areas": [],
            "proportion_issues": False,
            "symmetry_issues": False
        }
        
        tasks = brain.plan_next_action(vision_data)
        
        assert len(tasks) > 0
        assert all(isinstance(t, Task) for t in tasks)
    
    def test_get_action_plan(self):
        """Test getting action plan."""
        brain = BrainModule()
        
        task = Task(
            task_id="t1",
            task_type=TaskType.FIX_HAND,
            description="Fix hand"
        )
        
        plan = brain.get_action_plan(task)
        
        assert plan is not None
        assert plan.task_id == task.task_id
        assert len(plan.actions) > 0
    
    def test_evaluate_result(self):
        """Test evaluating result."""
        brain = BrainModule()
        
        task = Task(task_id="t1", task_type=TaskType.FIX_HAND, description="Fix hand")
        
        vision_before = {"proportion_score": 0.5}
        vision_after = {"proportion_score": 0.8}
        
        result = brain.evaluate_result(task, vision_before, vision_after)
        
        assert result in [ExecutionResult.SUCCESS, ExecutionResult.PARTIAL, ExecutionResult.FAILURE]
    
    def test_get_statistics(self):
        """Test getting statistics."""
        brain = BrainModule()
        
        stats = brain.get_statistics()
        
        assert "task_stats" in stats
        assert "state_summary" in stats
        assert "iteration_count" in stats
    
    def test_reset(self):
        """Test resetting brain module."""
        brain = BrainModule()
        
        brain.set_goal("Test goal")
        brain.reset()
        
        assert brain.get_goal() is None
        assert len(brain.task_manager.tasks) == 0
