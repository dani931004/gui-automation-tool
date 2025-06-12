"""
Main application entry point for the GUI Automation Tool.
"""
import os
import asyncio
from typing import Dict, Any, List, Optional

from nicegui import ui

from app.core.models import AutomationStep, AutomationState
from app.core.automation import AutomationEngine
from app.ui.pages.main_window import MainWindow

# Try to import PyAutoGUI, but don't fail if not available
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: PyAutoGUI not installed. Running in simulation mode.")

class GUIAutomationApp:
    """Main application class for the GUI Automation Tool."""
    
    def __init__(self):
        """Initialize the application."""
        self.state = AutomationState()
        self.engine = AutomationEngine(self.state, self._log)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the main UI components."""
        # Create main window
        self.window = MainWindow(
            on_add_step=self._add_step,
            on_run_steps=self._run_all_steps,
            on_clear_steps=self._clear_steps,
            on_remove_step=self._remove_step,
            on_upload_image=self._handle_upload,
            log=self._log
        )
        
        # Show warning if running in simulation mode
        if not PYAUTOGUI_AVAILABLE:
            ui.notify("Running in simulation mode. Install PyAutoGUI for full functionality.", type='warning')
    
    def _log(self, message: str, level: str = 'info') -> None:
        """Add a message to the log.
        
        Args:
            message: The message to log
            level: The log level (info, warning, error)
        """
        try:
            # Map level to color
            colors = {
                'info': 'text-grey',
                'warning': 'text-orange',
                'error': 'text-red'
            }
            color = colors.get(level.lower(), 'text-grey')
            
            # Print to console for debugging
            print(f"[{level.upper()}] {message}")
            
            # Add to log area if available
            if hasattr(self, 'window') and hasattr(self.window, 'log_area'):
                self.window.log_area.push(f'<span class="{color}">{message}</span>')
                
        except Exception as e:
            # If logging fails, at least print the error
            print(f"Error in _log: {e}")
            print(f"Original message: [{level}] {message}")
    
    def _add_step(self, step_type: str, params: Dict[str, Any]) -> None:
        """Add a new step to the automation.
        
        Args:
            step_type: The type of step to add
            params: The step parameters
        """
        try:
            step = {
                'type': step_type,
                'params': params
            }
            
            # Add to state
            self.state.add_step(step)
            
            # Update UI
            self.window.add_step_to_ui(step)
            self._log(f"Added step: {step_type}")
            
        except Exception as e:
            self._log(f"Error adding step: {str(e)}", 'error')
    
    def _remove_step(self, index: int) -> None:
        """Remove a step from the automation.
        
        Args:
            index: The index of the step to remove
        """
        try:
            step = self.state.remove_step(index)
            if step:
                self.window.clear_steps_ui()
                for s in self.state.steps:
                    self.window.add_step_to_ui(s)
                self._log(f"Removed step: {step['type']}")
        except Exception as e:
            self._log(f"Error removing step: {str(e)}", 'error')
    
    async def _run_all_steps(self) -> None:
        """Run all automation steps."""
        if not self.state.steps:
            self._log("No steps to run", 'warning')
            return
            
        self._log("Starting automation...")
        
        try:
            for step in self.state.steps:
                success = await self.engine.execute_step(step)
                if not success:
                    self._log(f"Step failed: {step['type']}", 'error')
                    break
                await asyncio.sleep(0.1)  # Small delay between steps
                
            self._log("Automation completed!")
            
        except Exception as e:
            self._log(f"Error during automation: {str(e)}", 'error')
    
    def _clear_steps(self) -> None:
        """Clear all automation steps."""
        self.state.clear_steps()
        self.window.clear_steps_ui()
        self._log("Cleared all steps")
    
    def _handle_upload(self, e) -> None:
        """Handle file upload.
        
        Args:
            e: The upload event
        """
        if not e or not hasattr(e, 'files') or not e.files:
            self._log("No files were uploaded", 'warning')
            return
            
        try:
            # Clean up old files before uploading new ones
            self.state.cleanup_old_files()
            
            # Process each uploaded file
            for file in e.files:
                try:
                    # Get a safe path in the temp directory
                    file_path = self.state.get_temp_file(file.name)
                    
                    # Save the file
                    with open(file_path, 'wb') as f:
                        f.write(file.content)
                    
                    # Add to uploaded files
                    self.state.uploaded_images[file.name] = str(file_path)
                    
                    # Update the UI
                    if hasattr(self, 'window') and hasattr(self.window, 'add_uploaded_image'):
                        self.window.add_uploaded_image(file.name, str(file_path))
                    
                    self._log(f"Uploaded: {file.name}")
                    
                except Exception as file_error:
                    error_msg = f"Error processing {file.name}: {str(file_error)}"
                    print(error_msg)  # Debug
                    self._log(error_msg, 'error')
                    
            # Update the image selector if it exists
            if hasattr(self, 'window') and hasattr(self.window, 'update_image_list'):
                self.window.update_image_list()
                
        except Exception as e:
            error_msg = f"Error handling upload: {str(e)}"
            print(error_msg)  # Debug
            self._log(error_msg, 'error')
            import traceback
            traceback.print_exc()  # Print full traceback for debugging

def main():
    """Run the application."""
    # Configure UI
    ui.add_head_html('''
        <style>
            body {
                font-family: 'Inter', sans-serif;
            }
            .log-entry {
                padding: 2px 4px;
                border-bottom: 1px solid #eee;
                font-family: monospace;
            }
        </style>
    ''')
    
    # Create the app
    app = GUIAutomationApp()
    
    # Run the app and open in browser
    ui.run(title='GUI Automation Tool', port=8080, reload=False, show=True
    )

if __name__ == '__main__':
    main()
