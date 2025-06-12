"""
UI components for step parameters.
"""
from typing import Dict, Any, Callable, Optional, List
from nicegui import ui

from app.core.models import PositionType, ButtonType, ModifierKey, SpecialKey


class StepParameters:
    """Base class for step parameter UIs.
    
    This class provides a base implementation for step parameter UIs.
    Subclasses should override get_parameters() and set_parameters()
    to handle their specific parameters.
    """
    
    def __init__(self, on_change: Optional[Callable] = None):
        """Initialize with optional change callback.
        
        Args:
            on_change: Callback function to be called when parameters change
        """
        self.on_change = on_change
        self.container = ui.column().classes('w-full')
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameter values.
        
        Returns:
            Dictionary containing the current parameter values
        """
        # Default implementation returns an empty dict
        return {}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set the parameter values.
        
        Args:
            params: Dictionary containing parameter values to set
        """
        # Default implementation does nothing
        pass
    
    def _notify_change(self) -> None:
        """Notify of parameter changes by calling the on_change callback if set."""
        if self.on_change:
            self.on_change()


class EmptyParameters(StepParameters):
    """Empty parameters UI for steps that don't require parameters."""
    
    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        with self.container:
            ui.label('No parameters required for this step type.').classes('text-italic text-grey')
    
    def get_parameters(self) -> Dict[str, Any]:
        """Return empty parameters."""
        return {}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """No parameters to set."""
        pass


class MoveMouseParameters(StepParameters):
    """Parameters for Move Mouse step."""
    
    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        with self.container:
            with ui.row().classes('w-full'):
                self.x_pos = ui.number('X Position', min=0, value=0, format='%.0f') \
                    .classes('w-1/2').on('update:model-value', lambda _: self._notify_change())
                self.y_pos = ui.number('Y Position', min=0, value=0, format='%.0f') \
                    .classes('w-1/2').on('update:model-value', lambda _: self._notify_change())
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameter values."""
        try:
            return {
                'x': int(self.x_pos.value) if hasattr(self, 'x_pos') and self.x_pos.value is not None else 0,
                'y': int(self.y_pos.value) if hasattr(self, 'y_pos') and self.y_pos.value is not None else 0
            }
        except (ValueError, AttributeError) as e:
            print(f"Error getting move mouse parameters: {e}")
            return {'x': 0, 'y': 0}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set the parameter values.
        
        Args:
            params: Dictionary containing 'x' and 'y' coordinates
        """
        self.x_pos.value = params.get('x', 0)
        self.y_pos.value = params.get('y', 0)


class ClickParameters(StepParameters):
    """Parameters for Click step."""
    
    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        with self.container:
            with ui.row().classes('w-full'):
                self.x_pos = ui.number('X Position', min=0, value=0, format='%.0f') \
                    .classes('w-1/3').on('update:model-value', lambda _: self._notify_change())
                self.y_pos = ui.number('Y Position', min=0, value=0, format='%.0f') \
                    .classes('w-1/3').on('update:model-value', lambda _: self._notify_change())
                self.button = ui.select(
                    label='Button',
                    options=['left', 'middle', 'right'],
                    value='left'
                ).classes('w-1/3').on('update:model-value', lambda _: self._notify_change())
    
    def get_parameters(self) -> Dict[str, Any]:
        try:
            return {
                'x': int(self.x_pos.value) if hasattr(self, 'x_pos') and self.x_pos.value is not None else 0,
                'y': int(self.y_pos.value) if hasattr(self, 'y_pos') and self.y_pos.value is not None else 0,
                'button': self.button.value if hasattr(self, 'button') and hasattr(self.button, 'value') else 'left'
            }
        except (ValueError, AttributeError) as e:
            print(f"Error getting click parameters: {e}")
            return {'x': 0, 'y': 0, 'button': 'left'}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        self.x_pos.value = params.get('x', 0)
        self.y_pos.value = params.get('y', 0)
        self.button.value = params.get('button', 'left')


class TypeTextParameters(StepParameters):
    """Parameters for Type Text step."""
    
    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        with self.container:
            self.text = ui.input(label='Text to Type') \
                .classes('w-full').on('update:model-value', lambda _: self._notify_change())
    
    def get_parameters(self) -> Dict[str, Any]:
        try:
            return {'text': self.text.value if hasattr(self, 'text') and hasattr(self.text, 'value') else ''}
        except Exception as e:
            print(f"Error getting text parameters: {e}")
            return {'text': ''}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        self.text.value = params.get('text', '')


class DelayParameters(StepParameters):
    """Parameters for Delay step."""
    
    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        with self.container:
            self.seconds = ui.number(
                'Delay (seconds)', 
                min=0.1, 
                value=1.0, 
                step=0.1,
                format='%.1f'
            ).classes('w-full').on('update:model-value', lambda _: self._notify_change())
    
    def get_parameters(self) -> Dict[str, Any]:
        try:
            return {'seconds': float(self.seconds.value) if hasattr(self, 'seconds') and self.seconds.value is not None else 1.0}
        except (ValueError, AttributeError) as e:
            print(f"Error getting delay parameters: {e}")
            return {'seconds': 1.0}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        self.seconds.value = params.get('seconds', 1.0)


class FindClickImageParameters(StepParameters):
    """Parameters for Find and Click Image step."""
    
    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        with self.container:
            with ui.row().classes('w-full items-center'):
                # Define the position options
                self.position_options = [
                    {'label': 'Center', 'value': 'center'},
                    {'label': 'Top Left', 'value': 'top_left'},
                    {'label': 'Top Right', 'value': 'top_right'},
                    {'label': 'Bottom Left', 'value': 'bottom_left'},
                    {'label': 'Bottom Right', 'value': 'bottom_right'},
                    {'label': 'Top Center', 'value': 'top_center'},
                    {'label': 'Bottom Center', 'value': 'bottom_center'},
                    {'label': 'Left Center', 'value': 'left_center'},
                    {'label': 'Right Center', 'value': 'right_center'}
                ]
                
                # Extract just the values for the select component
                position_values = [opt['value'] for opt in self.position_options]
                
                # Create the select with just the values first
                self.click_position = ui.select(
                    label='Click Position',
                    options=position_values,
                    value=position_values[0] if position_values else 'center'
                ).classes('w-1/2').on('update:model-value', lambda _: self._notify_change())
                
                # Update the display to show labels but use values internally
                self.click_position._props['options'] = self.position_options
                self.click_position._props['option-value'] = 'value'
                self.click_position._props['option-label'] = 'label'
                
                self.click_button = ui.select(
                    label='Mouse Button',
                    options=['left', 'middle', 'right'],
                    value='left'
                ).classes('w-1/2').on('update:model-value', lambda _: self._notify_change())
                
            with ui.row().classes('w-full'):
                self.confidence = ui.number(
                    'Confidence (0.1-1.0)',
                    min=0.1,
                    max=1.0,
                    value=0.9,
                    step=0.05,
                    format='%.2f'
                ).classes('w-1/3').on('update:model-value', lambda _: self._notify_change())
                
                self.max_attempts = ui.number(
                    'Max Attempts',
                    min=1,
                    max=10,
                    value=3,
                    format='%d'
                ).classes('w-1/3').on('update:model-value', lambda _: self._notify_change())
                
                self.retry_interval = ui.number(
                    'Retry Interval (s)',
                    min=0.1,
                    max=5.0,
                    value=0.5,
                    step=0.1,
                    format='%.1f'
                ).classes('w-1/3').on('update:model-value', lambda _: self._notify_change())
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameter values."""
        try:
            # Get the raw value from the select component
            position_value = self.click_position.value if hasattr(self, 'click_position') else 'center'
            
            # If the value is a dictionary (from label/value pair), extract the value
            if isinstance(position_value, dict) and 'value' in position_value:
                position_value = position_value['value']
            
            return {
                'position': position_value,
                'button': self.click_button.value if hasattr(self, 'click_button') and hasattr(self.click_button, 'value') else 'left',
                'confidence': float(self.confidence.value) if hasattr(self, 'confidence') and hasattr(self.confidence, 'value') else 0.9,
                'max_attempts': int(self.max_attempts.value) if hasattr(self, 'max_attempts') and hasattr(self.max_attempts, 'value') else 3,
                'retry_interval': float(self.retry_interval.value) if hasattr(self, 'retry_interval') and hasattr(self.retry_interval, 'value') else 0.5
            }
        except Exception as e:
            print(f"Error in get_parameters: {e}")
            return {
                'position': 'center',
                'button': 'left',
                'confidence': 0.9,
                'max_attempts': 3,
                'retry_interval': 0.5
            }
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set the parameter values."""
        try:
            position = params.get('position', 'center')
            # If we have a list of options, find the matching one
            if hasattr(self, 'position_options') and self.position_options:
                for opt in self.position_options:
                    if opt['value'] == position:
                        self.click_position.value = opt['value']
                        break
                else:
                    self.click_position.value = self.position_options[0]['value']
            else:
                self.click_position.value = position
                
            if hasattr(self, 'click_button') and hasattr(self.click_button, 'value'):
                self.click_button.value = params.get('button', 'left')
            if hasattr(self, 'confidence') and hasattr(self.confidence, 'value'):
                self.confidence.value = params.get('confidence', 0.9)
            if hasattr(self, 'max_attempts') and hasattr(self.max_attempts, 'value'):
                self.max_attempts.value = params.get('max_attempts', 3)
            if hasattr(self, 'retry_interval') and hasattr(self.retry_interval, 'value'):
                self.retry_interval.value = params.get('retry_interval', 0.5)
        except Exception as e:
            print(f"Error in set_parameters: {e}")

class PressHotkeyParameters(StepParameters):
    """Parameters for Press Hotkey step."""

    def __init__(self, on_change: Optional[Callable] = None):
        super().__init__(on_change)
        self.modifier_checkboxes: Dict[str, ui.checkbox] = {}
        self.primary_key_select: Optional[ui.select] = None

        with self.container:
            ui.label("Modifier Keys:").classes('text-sm font-medium mb-1')
            with ui.row().classes('gap-x-4 items-center'): # Added items-center for alignment
                for mod in ModifierKey.__args__: # Iterate over defined ModifierKey literals
                    self.modifier_checkboxes[mod] = ui.checkbox(mod.capitalize(), on_change=self._notify_change)

            ui.label("Primary Key:").classes('text-sm font-medium mt-3 mb-1') # Increased mt for spacing
            self.primary_key_select = ui.select(
                label="Select or type a key (e.g., 'c', 'enter', 'f1')",
                options=list(SpecialKey.__args__), # Populate with SpecialKey literals
                with_input=True, # Allow custom input
                value=None # No default selection initially
            ).classes('w-full').on('update:model-value', self._notify_change) # Use on_change for select

    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameter values."""
        modifiers = [mod for mod, cb in self.modifier_checkboxes.items() if cb.value]
        
        primary_key_value = ""
        if self.primary_key_select and self.primary_key_select.value is not None:
            primary_key_value = str(self.primary_key_select.value).strip()
            
        # Store the primary key in lowercase for consistency, if it's not empty
        keys = [primary_key_value.lower()] if primary_key_value else []
        
        return {'modifiers': modifiers, 'keys': keys}

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set the parameter values."""
        selected_modifiers = params.get('modifiers', [])
        for mod, cb in self.modifier_checkboxes.items():
            cb.value = mod in selected_modifiers

        keys_list = params.get('keys', [])
        if self.primary_key_input:
            if keys_list and isinstance(keys_list, list) and len(keys_list) > 0:
                self.primary_key_input.value = str(keys_list[0])
            else:
                self.primary_key_input.value = ""

def create_parameters(step_type: str, on_change: Optional[Callable] = None) -> StepParameters:
    """Create a parameter UI for the given step type.
    
    Args:
        step_type: The type of step to create parameters for
        on_change: Optional callback when parameters change
        
    Returns:
        StepParameters: The appropriate parameters UI component
    """
    try:
        if not step_type:
            print("No step type provided, using EmptyParameters")
            return EmptyParameters(on_change)
            
        # Normalize the step type string
        normalized_step_type = str(step_type).lower().strip()
        print(f"Creating parameters for step type: {normalized_step_type}")
        
        exact_match_map: Dict[str, Callable[[], StepParameters]] = {
            'move mouse': lambda: MoveMouseParameters(on_change),
            'click': lambda: ClickParameters(on_change),
            'type text': lambda: TypeTextParameters(on_change),
            'delay': lambda: DelayParameters(on_change),
            'press hotkey': lambda: PressHotkeyParameters(on_change),
            'screenshot': lambda: EmptyParameters(on_change), # Screenshots don't have UI configurable params
        }

        if normalized_step_type in exact_match_map:
            print(f"Found exact match for {normalized_step_type}")
            return exact_match_map[normalized_step_type]()
        
        # Pattern match for "Find and Click Image"
        if 'find' in normalized_step_type and 'click' in normalized_step_type and 'image' in normalized_step_type:
            print(f"Found pattern match for 'find and click image'")
            return FindClickImageParameters(on_change)
                
        # Fallback for unknown step types
        print(f"No specific parameters UI found for step type: {normalized_step_type}, using EmptyParameters.")
        return EmptyParameters(on_change)
        
    except Exception as e:
        import traceback
        error_msg = f"Error creating parameters for step type '{step_type}': {e}"
        print(error_msg)
        traceback.print_exc()
        # Fallback to EmptyParameters on error
        return EmptyParameters(on_change)
