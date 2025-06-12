"""
Main application window for the GUI Automation Tool.
"""
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
import os

from nicegui import ui

from app.core.models import AutomationStep
from app.ui.components.step_parameters import create_parameters, EmptyParameters

class MainWindow:
    """Main application window."""
    
    def __init__(self, 
                 on_add_step: Callable[[str, Dict[str, Any]], None],
                 on_run_steps: Callable[[], None],
                 on_clear_steps: Callable[[], None],
                 on_remove_step: Callable[[int], None],
                 on_upload_image: Callable[[Any], None],
                 log: Callable[[str, str], None]):
        """Initialize the main window.
        
        Args:
            on_add_step: Callback when a step is added
            on_run_steps: Callback when run all steps is clicked
            on_clear_steps: Callback when clear all steps is clicked
            on_remove_step: Callback when a step is removed
            on_upload_image: Callback when an image is uploaded
            log: Function to add log messages
        """
        self.on_add_step = on_add_step
        self.on_run_steps = on_run_steps
        self.on_clear_steps = on_clear_steps
        self.on_remove_step = on_remove_step
        self.on_upload_image = on_upload_image
        self.log = log
        
        self.step_type = None
        self.parameters_ui = None
        self.uploaded_images: Dict[str, str] = {}
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the main UI components."""
        # Header
        with ui.header().classes('bg-blue-500 text-white'):
            ui.label('GUI Automation Tool').classes('text-2xl font-bold')
        
        # Main content
        with ui.column().classes('w-full p-4'):
            # Add Step Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Add New Step').classes('text-xl font-bold')
                
                # Create a card for the step configuration
                with ui.card().classes('w-full p-4 bg-gray-100') as self.params_card:
                    # Add step type selection
                    with ui.row().classes('w-full items-center'):
                        # Define the step types as simple strings
                        self.step_types = [
                            'Move Mouse',
                            'Click',
                            'Type Text',
                            'Delay',
                            'Screenshot',
                            'Find and Click Image',
                            'Press Hotkey'
                        ]
                        
                        # Initialize the select component with simple string options
                        self.step_type_select = ui.select(
                            label='Action Type',
                            options=self.step_types,
                            value=self.step_types[0],  # Use the first option as default
                            on_change=lambda e: self._on_step_type_changed(e)
                        ).classes('w-full')
                        
                        # Set the initial step type
                        self.step_type = self.step_types[0]
                        
                        # Debug log
                        print(f"Initialized step type select with value: {self.step_type}")
                    
                    # Create a container for the parameters UI
                    self.parameters_container = ui.column().classes('w-full mt-4')
                    
                    # Initialize parameters UI with the default step type
                    self._update_parameters_ui(self.step_type)
                
                # Image upload section
                self.upload_container = ui.column().classes('w-full')
                with self.upload_container:
                    with ui.card().classes('w-full p-4 bg-blue-50') as self.upload_card:
                        ui.label('Image Upload').classes('text-lg font-bold')
                        
                        # Upload button (always visible when this section is shown)
                        with ui.column().classes('w-full items-center gap-2 mb-4') as self.upload_button_container:
                            ui.label('Upload a reference image:').classes('w-full text-center')
                            self.upload = ui.upload(
                                label='Choose Image',
                                on_upload=self._handle_upload,
                                max_file_size=5_000_000,  # 5MB limit
                                auto_upload=True
                            ).props('accept=.png,.jpg,.jpeg outline')
                        
                        # Image selector (hidden until first upload)
                        with ui.column().classes('w-full') as self.image_selector_container:
                            self.image_selector = ui.select(
                                label='Select Image',
                                options=[],
                                with_input=True
                            ).classes('w-full')
                        
                        # Initially hide the image selector
                        self.image_selector_container.set_visibility(False)
                
                # Initially hide the entire upload section
                self.upload_container.set_visibility(False)
                
                # Parameters section (dynamically updated)
                with ui.card().classes('w-full p-4 bg-gray-100') as self.params_card:
                    self._update_parameters_ui(self.step_type_select.value)
                
                # Update params when step type changes
                self.step_type_select.on('update:model-value', self._on_step_type_changed)
                
                # Add step button
                ui.button('Add Step', on_click=self._on_add_step_clicked)
            
            # Current Steps Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Current Automation Steps').classes('text-xl font-bold')
                self.steps_list = ui.column().classes('w-full')
            
            # Action Buttons
            with ui.row().classes('w-full justify-between'):
                ui.button('Run All Steps', on_click=self.on_run_steps, color='positive')
                ui.button('Clear All Steps', on_click=self.on_clear_steps, color='negative')
            
            # Logs Section
            with ui.card().classes('w-full mt-4'):
                ui.label('Execution Logs').classes('text-xl font-bold')
                self.log_area = ui.log().classes('w-full h-48')
    
    def _on_step_type_changed(self, event) -> None:
        """Handle step type change."""
        try:
            # Extract the step type from the event
            if hasattr(event, 'value'):
                # Handle direct value (string)
                step_type = event.value
            elif hasattr(event, 'args') and isinstance(event.args, dict) and 'label' in event.args:
                # Handle NiceGUI event with args
                step_type = event.args['label']
            elif isinstance(event, str):
                # Handle direct string
                step_type = event
            else:
                # Fallback to default
                step_type = 'Move Mouse'
                
            # Store the current step type
            self.step_type = step_type
            
            # Debug log
            print(f"Step type changed to: {step_type}")
            
            # Update the parameters UI with just the step type string
            self._update_parameters_ui(step_type)
            
            # Show/hide upload section based on step type
            is_image_step = step_type.lower() == 'find and click image'
            if hasattr(self, 'upload_container'):
                self.upload_container.set_visibility(is_image_step)
            
            # Force UI update
            if hasattr(self, 'params_card'):
                ui.update(self.params_card)
            
            # Debug log
            self.log(f'Updated to step type: {step_type}', 'debug')
            
        except Exception as e:
            error_msg = f'Error updating step type: {str(e)}'
            print(error_msg)
            import traceback
            print(f"Error in _on_step_type_changed: {error_msg}")
            print(traceback.format_exc())
    
    def _update_parameters_ui(self, step_type: str) -> None:
        """Update the parameters UI based on the selected step type."""
        try:
            # Ensure step_type is a string
            if not isinstance(step_type, str):
                if hasattr(step_type, 'label'):
                    step_type = step_type.label
                elif hasattr(step_type, 'value'):
                    step_type = step_type.value
                else:
                    step_type = str(step_type)
            
            # Debug log
            print(f"Updating parameters UI for step type: {step_type}")
            
            # Clear the current parameters container
            if hasattr(self, 'parameters_container'):
                # Clear the container by removing all its children
                self.parameters_container.clear()
                
                # Create a new container for the parameters
                with self.parameters_container:
                    # Create parameters with on_change callback
                    self.parameters_ui = create_parameters(
                        step_type=step_type,
                        on_change=lambda: self._on_parameters_changed(
                            self.parameters_ui.get_parameters() if hasattr(self.parameters_ui, 'get_parameters') else {}
                        )
                    )
                    print(f"Created parameters UI: {self.parameters_ui}")
                    
                    # Add the parameters UI to the container
                    if hasattr(self.parameters_ui, 'container'):
                        # Set the container classes if available
                        if hasattr(self.parameters_ui.container, 'classes'):
                            self.parameters_ui.container.classes('w-full')
                        # The container is automatically added by the context manager
                
                # Debug log
                log_msg = f"Updated parameters UI for step type: {step_type}"
                print(log_msg)
                if hasattr(self, 'log'):
                    self.log(log_msg, 'debug')
                
            # Show/hide upload section based on step type
            is_image_step = step_type.lower() == 'find and click image'
            if hasattr(self, 'upload_container'):
                self.upload_container.set_visibility(is_image_step)
            
        except Exception as e:
            error_msg = f'Error updating parameters UI: {str(e)}'
            print(error_msg)
            import traceback
            print(traceback.format_exc())
            if hasattr(self, 'log'):
                self.log(error_msg, 'error')
    
    def _on_parameters_changed(self, params: Dict[str, Any]) -> None:
        """Handle parameter changes."""
        # Update the parameters UI with the new parameters
        if self.parameters_ui:
            self.parameters_ui.set_parameters(params)
    
    def _on_add_step_clicked(self) -> None:
        """Handle add step button click."""
        try:
            # Get the selected step type
            step_type = self.step_type_select.value
            
            # Debug log
            print(f"Adding step: {step_type}")
            
            # Ensure we have a valid step type
            if not step_type or step_type not in self.step_types:
                self.log('Please select a valid step type', 'error')
                return
            
            # Get the parameters from the current UI
            params = {}
            if self.parameters_ui:
                try:
                    params = self.parameters_ui.get_parameters()
                except Exception as e:
                    self.log(f'Error getting parameters: {str(e)}', 'error')
                    raise
            
            # For image steps, add the selected image path
            if step_type == 'Find and Click Image':
                selected_image = self.image_selector.value if hasattr(self, 'image_selector') else None
                if not selected_image:
                    self.log('Please select an image', 'error')
                    return
                    
                if selected_image not in self.uploaded_images:
                    self.log('Selected image not found', 'error')
                    return
                    
                params['image_path'] = self.uploaded_images[selected_image]
            
            # Debug log
            print(f"Calling on_add_step with type: {step_type}, params: {params}")
            
            # Call the add step callback with the step type and parameters
            try:
                self.on_add_step(step_type, params)
                
                # Reset the form
                self.step_type_select.value = self.step_types[0]  # Reset to first option
                if hasattr(self, 'parameters_ui') and self.parameters_ui:
                    self.parameters_ui.set_parameters({})
                
                # Clear the image selector if it exists
                if hasattr(self, 'image_selector'):
                    self.image_selector.value = None
                    
            except Exception as e:
                self.log(f'Error adding step: {str(e)}', 'error')
                raise
            
        except Exception as e:
            error_msg = f'Error adding step: {str(e)}'
            self.log(error_msg, 'error')
            import traceback
            print(f"Error in _on_add_step_clicked: {error_msg}")
            print(traceback.format_exc())
    
    def _handle_upload(self, e) -> None:
        """Handle file upload.
        
        Args:
            e: The upload event containing file data
        """
        try:
            if not e or not hasattr(e, 'files') or not e.files:
                if hasattr(self, 'log'):
                    self.log("No files were uploaded", 'warning')
                return
                
            # Call the parent's upload handler
            self.on_upload_image(e)
            
            # Show success message
            if hasattr(self, 'log'):
                self.log(f"Successfully processed {len(e.files)} file(s)", 'success')
                
        except Exception as e:
            error_msg = f"Error handling upload: {str(e)}"
            print(error_msg)
            if hasattr(self, 'log'):
                self.log(error_msg, 'error')
    
    def add_step_to_ui(self, step: AutomationStep) -> None:
        """Add a step to the UI list.
        
        Args:
            step: The step to add to the UI
        """
        # Create a unique ID for this step
        step_id = id(step)
        
        with self.steps_list:
            with ui.card().classes('w-full mb-2').tight() as card:
                # Store the step ID as a custom attribute
                card._props['data-step-id'] = str(step_id)
                
                with ui.row().classes('w-full items-center gap-2'):
                    # Step type badge
                    ui.badge(step['type'], color='primary').props('rounded')
                    
                    # Show step parameters summary
                    params = step.get('params', {})
                    with ui.row().classes('items-center gap-4'):
                        if step['type'] == 'Move Mouse':
                            ui.icon('mouse').classes('text-gray-500')
                            ui.label(f"Move to ({params.get('x', 0)}, {params.get('y', 0)})")
                            
                        elif step['type'] == 'Click':
                            ui.icon('mouse').classes('text-gray-500')
                            ui.label(f"Click at ({params.get('x', 0)}, {params.get('y', 0)})")
                            ui.badge(params.get('button', 'left'), color='secondary').props('rounded')
                            
                        elif step['type'] == 'Type Text':
                            ui.icon('keyboard').classes('text-gray-500')
                            text = params.get('text', '')
                            ui.label(f"Type: '{text[:20]}{'...' if len(text) > 20 else ''}")
                            
                        elif step['type'] == 'Delay':
                            ui.icon('schedule').classes('text-gray-500')
                            ui.label(f"Wait {params.get('seconds', 0)} seconds")
                            
                        elif step['type'] == 'Find and Click Image':
                            ui.icon('image_search').classes('text-gray-500')
                            img_path = params.get('image_path', '')
                            img_name = os.path.basename(img_path) if img_path else 'No image'
                            ui.label(f"Find and click: {img_name}")
                            ui.badge(params.get('position', 'center'), color='secondary').props('rounded')

                        elif step['type'] == 'Press Hotkey':
                            ui.icon('keyboard_command_key').classes('text-gray-500') # Or 'keyboard'
                            modifiers = params.get('modifiers', [])
                            keys = params.get('keys', [])
                            hotkey_str = "+".join(modifiers + keys)
                            ui.label(f"Press: {hotkey_str if hotkey_str else 'No keys defined'}")
                    
                    # Spacer to push remove button to the right
                    ui.space()
                    
                    # Remove button
                    ui.button(icon='delete', 
                             on_click=lambda _, s=step_id: self._on_remove_step_clicked(s)) \
                        .props('flat dense color=negative round')
    
    def _on_remove_step_clicked(self, step_id: int) -> None:
        """Handle remove step button click."""
        # Find the step with the matching ID and remove it
        for i, step in enumerate(self.steps_list):
            if hasattr(step, '_props') and 'data-step-id' in step._props:
                if int(step._props['data-step-id']) == step_id:
                    # Call the remove step callback with the correct index
                    self.on_remove_step(i)
                    # Remove the UI element
                    step.delete()
                    break
    
    def clear_steps_ui(self) -> None:
        """Clear all steps from the UI."""
        self.steps_list.clear()
    
    def update_image_list(self) -> None:
        """Update the image selector with the current list of uploaded images."""
        if not hasattr(self, 'image_selector'):
            return
            
        try:
            # Get the current selection to preserve it if possible
            current_selection = self.image_selector.value
            
            # Update the options
            options = list(self.uploaded_images.keys())
            self.image_selector.set_options(options)
            
            # Restore selection if it still exists
            if current_selection in options:
                self.image_selector.value = current_selection
            elif options:  # Select the first option if no selection
                self.image_selector.value = options[0]
                
            # Show the selector if we have images, hide otherwise
            if hasattr(self, 'image_selector_container'):
                self.image_selector_container.set_visibility(bool(options))
                
        except Exception as e:
            print(f"Error updating image list: {e}")
            if hasattr(self, 'log'):
                self.log(f"Error updating image list: {e}", 'error')
    
    def add_uploaded_image(self, filename: str, filepath: str) -> None:
        """Add an uploaded image to the list.
        
        Args:
            filename: The name of the uploaded file
            filepath: The path where the file is stored
        """
        try:
            # Add or update the image in the dictionary
            self.uploaded_images[filename] = filepath
            
            # Update the image selector
            self.update_image_list()
            
            # Log the successful upload
            if hasattr(self, 'log'):
                self.log(f"Added image: {filename}", 'info')
                
        except Exception as e:
            error_msg = f"Error adding image {filename}: {str(e)}"
            print(error_msg)
            if hasattr(self, 'log'):
                self.log(error_msg, 'error')
