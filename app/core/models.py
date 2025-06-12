"""
Data models for the GUI Automation Tool.
"""
import os
import tempfile
import shutil
from typing import Dict, Any, List, Optional, TypedDict, Literal
from pathlib import Path

# Type aliases
ButtonType = Literal['left', 'middle', 'right']
PositionType = Literal[
    'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right',
    'top_center', 'bottom_center', 'left_center', 'right_center'
]

# Common modifier keys for keyboard shortcuts
ModifierKey = Literal['ctrl', 'alt', 'shift', 'win', 'cmd']
# Common special keys for keyboard shortcuts
SpecialKey = Literal[
    'enter', 'tab', 'esc', 'space', 'backspace', 'delete', 'insert', 'home', 'end',
    'pageup', 'pagedown', 'up', 'down', 'left', 'right', 'f1', 'f2', 'f3', 'f4',
    'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
]

class AutomationStep(TypedDict, total=False):
    """Represents a single automation step."""
    id: str
    type: str
    params: Dict[str, Any]
    
    # Type-specific parameters
    x_position: Optional[int]
    y_position: Optional[int]
    button: Optional[ButtonType]
    text: Optional[str]
    seconds: Optional[float]
    image_path: Optional[str]
    # Keyboard action parameters
    keys: Optional[List[str]]
    modifiers: Optional[List[ModifierKey]]
    key_sequence: Optional[List[Dict[str, Any]]]
    position: Optional[PositionType]
    confidence: Optional[float]
    max_attempts: Optional[int]
    retry_interval: Optional[float]

class AutomationState:
    """Manages the state of the automation."""
    def __init__(self):
        self.steps: List[AutomationStep] = []
        self.step_counter: int = 0
        self.uploaded_images: Dict[str, str] = {}  # filename: temp_path
        self.temp_dir = Path(tempfile.mkdtemp(prefix='gui-automation-'))
        
    def __del__(self):
        """Clean up temporary files when the object is destroyed."""
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def get_temp_file(self, filename: str) -> Path:
        """Get a path in the temp directory for the given filename."""
        return self.temp_dir / filename
        
    def cleanup_old_files(self) -> None:
        """Clean up old temporary files."""
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            for file in self.temp_dir.glob('*'):
                try:
                    if file.is_file():
                        file.unlink()
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
        
    def add_step(self, step: AutomationStep) -> None:
        """Add a new step to the automation."""
        try:
            # Create a copy of the step to avoid modifying the original
            step_copy = step.copy()
            step_copy['id'] = f"step_{self.step_counter}"
            self.steps.append(step_copy)
            self.step_counter += 1
            return step_copy
        except Exception as e:
            print(f"Error adding step: {e}")
            raise
    
    def remove_step(self, index: int) -> Optional[AutomationStep]:
        """Remove a step by index."""
        if 0 <= index < len(self.steps):
            return self.steps.pop(index)
        return None
    
    def reorder_step(self, old_index: int, new_index: int) -> bool:
        """Reorder a step from old_index to new_index."""
        if not (0 <= old_index < len(self.steps) and 0 <= new_index < len(self.steps)):
            print(f"Error: Invalid indices for reordering. old_index: {old_index}, new_index: {new_index}, steps_count: {len(self.steps)}")
            return False
        
        try:
            step_to_move = self.steps.pop(old_index)
            self.steps.insert(new_index, step_to_move)
            return True
        except IndexError as e:
            print(f"Error reordering step: {e}")
            return False
            
    def clear_steps(self) -> None:
        """Remove all steps."""
        self.steps.clear()
    
    def get_step(self, index: int) -> Optional[AutomationStep]:
        """Get a step by index."""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None
