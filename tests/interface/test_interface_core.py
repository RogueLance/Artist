"""
Tests for Interface core functionality.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from interface import CLIInterface, SessionConfig
from interface.models.session import Session
from interface.models.user_input import UserInput, InputType, UserDecision
from interface.utils.logger import InterfaceLogger
from interface.utils.display import DisplayFormatter


class TestUserInput:
    """Tests for UserInput model."""
    
    def test_create_user_input(self):
        """Test creating a user input."""
        user_input = UserInput(
            input_type=InputType.GOAL,
            value="Test goal",
            context="test"
        )
        
        assert user_input.input_type == InputType.GOAL
        assert user_input.value == "Test goal"
        assert user_input.context == "test"
        assert isinstance(user_input.timestamp, datetime)
    
    def test_user_input_to_dict(self):
        """Test converting user input to dictionary."""
        user_input = UserInput(
            input_type=InputType.REFERENCE,
            value="image.png",
            metadata={"size": "800x600"}
        )
        
        data = user_input.to_dict()
        
        assert data['input_type'] == 'reference'
        assert data['value'] == 'image.png'
        assert data['metadata']['size'] == "800x600"
        assert 'timestamp' in data
    
    def test_user_input_from_dict(self):
        """Test creating user input from dictionary."""
        data = {
            'input_type': 'sketch',
            'value': 'sketch.png',
            'timestamp': datetime.now().isoformat(),
            'metadata': {},
            'context': 'test'
        }
        
        user_input = UserInput.from_dict(data)
        
        assert user_input.input_type == InputType.SKETCH
        assert user_input.value == 'sketch.png'
        assert user_input.context == 'test'


class TestSessionConfig:
    """Tests for SessionConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SessionConfig()
        
        assert config.canvas_width == 800
        assert config.canvas_height == 600
        assert config.max_iterations == 10
        assert config.auto_save is True
        assert config.enable_vision is True
        assert config.enable_brain is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SessionConfig(
            canvas_width=400,
            canvas_height=300,
            max_iterations=5,
            interactive=False
        )
        
        assert config.canvas_width == 400
        assert config.canvas_height == 300
        assert config.max_iterations == 5
        assert config.interactive is False
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = SessionConfig(canvas_width=400, canvas_height=300)
        data = config.to_dict()
        
        assert data['canvas_width'] == 400
        assert data['canvas_height'] == 300
        assert isinstance(data, dict)


class TestSession:
    """Tests for Session."""
    
    def test_create_session(self):
        """Test creating a session."""
        config = SessionConfig()
        session = Session(session_id="test-session", config=config)
        
        assert session.session_id == "test-session"
        assert session.config == config
        assert isinstance(session.start_time, datetime)
        assert session.end_time is None
        assert session.current_iteration == 0
    
    def test_add_input(self):
        """Test adding user input to session."""
        session = Session(session_id="test", config=SessionConfig())
        user_input = UserInput(input_type=InputType.GOAL, value="Test")
        
        session.add_input(user_input)
        
        assert len(session.inputs) == 1
        assert session.inputs[0] == user_input
    
    def test_add_action(self):
        """Test adding action to session."""
        session = Session(session_id="test", config=SessionConfig())
        action = {"type": "analyze", "details": "test"}
        
        session.add_action(action)
        
        assert len(session.actions) == 1
        assert 'timestamp' in session.actions[0]
        assert session.actions[0]['type'] == "analyze"
    
    def test_add_evaluation(self):
        """Test adding evaluation to session."""
        session = Session(session_id="test", config=SessionConfig())
        evaluation = {"result": "success", "score": 0.8}
        
        session.add_evaluation(evaluation)
        
        assert len(session.evaluations) == 1
        assert session.evaluations[0]['result'] == "success"
        assert session.evaluations[0]['iteration'] == 0
    
    def test_increment_iteration(self):
        """Test incrementing iteration counter."""
        session = Session(session_id="test", config=SessionConfig())
        
        assert session.current_iteration == 0
        session.increment_iteration()
        assert session.current_iteration == 1
        session.increment_iteration()
        assert session.current_iteration == 2
    
    def test_complete_session(self):
        """Test completing a session."""
        session = Session(session_id="test", config=SessionConfig())
        
        assert session.end_time is None
        session.complete()
        assert session.end_time is not None
        assert isinstance(session.end_time, datetime)
    
    def test_session_to_dict(self):
        """Test converting session to dictionary."""
        config = SessionConfig()
        session = Session(session_id="test", config=config)
        session.goal = "Test goal"
        session.add_input(UserInput(input_type=InputType.GOAL, value="Test"))
        
        data = session.to_dict()
        
        assert data['session_id'] == "test"
        assert data['goal'] == "Test goal"
        assert len(data['inputs']) == 1
        assert 'start_time' in data
    
    def test_save_and_load_session(self):
        """Test saving and loading session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = SessionConfig()
            session = Session(session_id="test", config=config)
            session.goal = "Test goal"
            session.add_canvas_state("/tmp/canvas.png")
            
            # Save
            path = Path(tmpdir) / "session.json"
            session.save(path)
            assert path.exists()
            
            # Load
            loaded = Session.load(path)
            assert loaded.session_id == "test"
            assert loaded.goal == "Test goal"
            assert len(loaded.canvas_states) == 1


class TestInterfaceLogger:
    """Tests for InterfaceLogger."""
    
    def test_create_logger(self):
        """Test creating logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = InterfaceLogger(log_file=log_file)
            
            assert logger.log_file == log_file
            assert len(logger.event_log) == 0
    
    def test_log_user_input(self):
        """Test logging user input."""
        logger = InterfaceLogger()
        
        logger.log_user_input("goal", "Test goal", "context")
        
        assert len(logger.event_log) == 1
        assert logger.event_log[0]['type'] == 'user_input'
        assert logger.event_log[0]['input_type'] == 'goal'
    
    def test_log_action(self):
        """Test logging action."""
        logger = InterfaceLogger()
        
        logger.log_action("test_action", {"detail": "value"})
        
        assert len(logger.event_log) == 1
        assert logger.event_log[0]['type'] == 'system_action'
        assert logger.event_log[0]['action'] == 'test_action'
    
    def test_log_evaluation(self):
        """Test logging evaluation."""
        logger = InterfaceLogger()
        
        logger.log_evaluation("task1", {"score": 0.8}, "success")
        
        assert len(logger.event_log) == 1
        assert logger.event_log[0]['type'] == 'evaluation'
        assert logger.event_log[0]['result'] == 'success'
    
    def test_save_event_log(self):
        """Test saving event log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = InterfaceLogger()
            logger.log_action("test")
            
            path = Path(tmpdir) / "events.json"
            logger.save_event_log(path)
            
            assert path.exists()


class TestDisplayFormatter:
    """Tests for DisplayFormatter."""
    
    def test_format_header(self):
        """Test formatting header."""
        header = DisplayFormatter.format_header("Test", width=20)
        
        assert "Test" in header
        assert "=" in header
    
    def test_format_section(self):
        """Test formatting section."""
        section = DisplayFormatter.format_section("Section Title")
        
        assert "Section Title" in section
        assert "-" in section
    
    def test_format_list(self):
        """Test formatting list."""
        items = ["item1", "item2", "item3"]
        formatted = DisplayFormatter.format_list(items)
        
        assert "item1" in formatted
        assert "item2" in formatted
        assert "•" in formatted
    
    def test_format_dict(self):
        """Test formatting dictionary."""
        data = {"key1": "value1", "key2": 123}
        formatted = DisplayFormatter.format_dict(data)
        
        assert "key1" in formatted
        assert "value1" in formatted
        assert "key2" in formatted
    
    def test_format_prompt(self):
        """Test formatting prompt."""
        prompt = DisplayFormatter.format_prompt("Test?", ["yes", "no"])
        
        assert "Test?" in prompt
        assert "yes/no" in prompt


class TestCLIInterface:
    """Tests for CLIInterface."""
    
    def test_create_interface(self):
        """Test creating interface."""
        config = SessionConfig()
        interface = CLIInterface(config)
        
        assert interface.config == config
        assert interface.session is None
        assert interface.formatter is not None
    
    def test_start_end_session(self):
        """Test starting and ending session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = SessionConfig(
                output_dir=Path(tmpdir),
                enable_vision=False,
                enable_brain=False
            )
            interface = CLIInterface(config)
            
            # Start session
            session_id = interface.start_session()
            assert interface.session is not None
            assert interface.session.session_id == session_id
            assert interface.logger is not None
            assert interface.motor is not None
            
            # End session
            interface.end_session()
            assert interface.session is None
    
    def test_set_goal(self):
        """Test setting goal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = SessionConfig(
                output_dir=Path(tmpdir),
                enable_vision=False,
                enable_brain=False
            )
            interface = CLIInterface(config)
            interface.start_session()
            
            interface.set_goal("Test goal")
            
            assert interface.session.goal == "Test goal"
            assert len(interface.session.inputs) == 1
            
            interface.end_session()
    
    def test_create_blank_canvas(self):
        """Test creating blank canvas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = SessionConfig(
                canvas_width=400,
                canvas_height=300,
                output_dir=Path(tmpdir),
                enable_vision=False,
                enable_brain=False
            )
            interface = CLIInterface(config)
            interface.start_session()
            
            success = interface.create_blank_canvas()
            
            assert success is True
            assert interface.current_canvas_path is not None
            assert interface.current_canvas_path.exists()
            assert len(interface.session.canvas_states) == 1
            
            interface.end_session()
    
    def test_display_session_summary(self):
        """Test displaying session summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = SessionConfig(
                output_dir=Path(tmpdir),
                enable_vision=False,
                enable_brain=False
            )
            interface = CLIInterface(config)
            interface.start_session()
            interface.set_goal("Test")
            
            # Should not raise exception
            interface.display_session_summary()
            
            interface.end_session()
    
    def test_no_session_error(self):
        """Test error when no session is active."""
        config = SessionConfig()
        interface = CLIInterface(config)
        
        with pytest.raises(RuntimeError, match="No active session"):
            interface.set_goal("Test")
