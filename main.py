"""
GUI Automation Tool - A simple web-based GUI automation tool using NiceGUI and PyAutoGUI.
"""
import asyncio
import os
import shutil
import sys
import time
import cv2
import numpy as np
import atexit
import importlib.util
from typing import List, Dict, Any, Optional, Tuple, Union
from nicegui import ui

# Initialize OpenCV
cv2.setUseOptimized(True)
cv2.setNumThreads(4)

# Check if PyAutoGUI is available
PYAUTOGUI_AVAILABLE = importlib.util.find_spec('pyautogui') is not None

# Mock PyAutoGUI if not available
if not PYAUTOGUI_AVAILABLE:
    print("Warning: PyAutoGUI not found. Running in simulation mode.")
    import types
    pyautogui = types.SimpleNamespace()
    pyautogui.moveTo = lambda x, y: print(f"[SIM] Move mouse to ({x}, {y})")
    pyautogui.click = lambda x=None, y=None, button='left': print(f"[SIM] Click at ({x}, {y}) with {button} button")
    pyautogui.write = lambda text: print(f"[SIM] Type: {text}")
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = False
else:
    import pyautogui
    
    # Configure PyAutoGUI
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = True

class GUIAutomationTool:
    def __init__(self):
        self.automation_steps: List[Dict[str, Any]] = []
        self.simulation_mode = not PYAUTOGUI_AVAILABLE
        self.step_counter = 0
        self.uploaded_images: Dict[str, str] = {}  # Store uploaded images: {filename: temp_path}
        
        # Create a directory for temporary image storage
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_images')
        os.makedirs(self.temp_dir, exist_ok=True)
        atexit.register(self._cleanup_temp_dir)

        self.setup_ui()
        
        if self.simulation_mode:
            ui.notify("Running in simulation mode. Install PyAutoGUI for full functionality.", type='warning')

    def setup_ui(self):
        """Set up the main UI components."""
        # Header
        with ui.header().classes('bg-blue-800 text-white'):
            ui.label('GUI Automation Tool').classes('text-2xl font-bold')
            if self.simulation_mode:
                ui.badge('SIMULATION MODE', color='yellow').props('dense').classes('ml-4')
        
        # Main content
        with ui.column().classes('w-full p-4'):
            # Add Step Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Add New Step').classes('text-xl font-bold')
                
                # Step type selection
                step_types = ['Move Mouse', 'Click', 'Type Text', 'Delay', 'Screenshot', 'Find and Click Image']
                self.step_type_select = ui.select(
                    label='Action Type',
                    options=step_types,
                    value=step_types[0]
                ).classes('w-full')
                self.current_step_type = step_types[0]  # Track current step type
                
                # Image upload section (initially hidden, shown only for image steps)
                with ui.card().classes('w-full p-4 bg-blue-50') as self.upload_card:
                    ui.label('Image Upload').classes('text-lg font-bold')
                    self.upload = ui.upload(label='Upload Reference Image', 
                                          on_upload=lambda e: self.handle_upload(e),
                                          max_file_size=5_000_000,  # 5MB limit
                                          auto_upload=True
                                         ).props('accept=.png,.jpg,.jpeg')
                    # Add a container to show the selected image
                    self.image_preview = ui.image('')
                    self.image_preview.set_visibility(False)
                    self.image_selector = ui.select(
                        label='Select Image',
                        options=[],
                        with_input=True
                    ).classes('w-full')
                    self.upload_card.set_visibility(False)  # Hide by default
                
                # Parameters section (will be updated based on step type)
                with ui.card().classes('w-full p-4 bg-gray-100') as self.params_card:
                    self.setup_step_params(step_type.value)
                
                # Update params when step type changes
                def on_step_type_change(e):
                    self.current_step_type = e.value
                    self.setup_step_params(e.value)
                
                self.step_type_select.on('update:model-value', on_step_type_change)
                
                # Add step button
                self.add_step_btn = ui.button('Add Step').on('click', lambda: self.add_step(self.current_step_type))
            
            # Current Steps Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Current Automation Steps').classes('text-xl font-bold')
                self.steps_list = ui.column().classes('w-full')
            
            # Action Buttons
            with ui.row().classes('w-full justify-between'):
                ui.button('Run All Steps', on_click=self.run_all_steps, color='positive')
                ui.button('Clear All Steps', on_click=self.clear_steps, color='negative')
            
            # Logs Section
            with ui.card().classes('w-full mt-4'):
                ui.label('Execution Logs').classes('text-xl font-bold')
                self.log_area = ui.log().classes('w-full h-48')
    
    def setup_step_params(self, step_type: str):
        """Set up the parameters UI for the selected step type."""
        self.params_card.clear()
        
        # Show/hide upload section based on step type
        self.upload_card.set_visibility(step_type == 'Find and Click Image')
        
        if step_type == 'Move Mouse':
            with self.params_card:
                with ui.row().classes('w-full'):
                    self.x_pos = ui.number('X Position', min=0, value=0, format='%.0f').classes('w-1/2')
                    self.y_pos = ui.number('Y Position', min=0, value=0, format='%.0f').classes('w-1/2')
                    
        elif step_type == 'Click':
            with self.params_card:
                with ui.row().classes('w-full'):
                    self.click_x = ui.number('X Position', min=0, value=0, format='%.0f').classes('w-1/3')
                    self.click_y = ui.number('Y Position', min=0, value=0, format='%.0f').classes('w-1/3')
                    self.click_button = ui.select(
                        label='Button',
                        options=['left', 'middle', 'right'],
                        value='left'
                    ).classes('w-1/3')
                    
        elif step_type == 'Type Text':
            with self.params_card:
                self.text_to_type = ui.input('Text to Type').classes('w-full')
                
        elif step_type == 'Find and Click Image':
            with self.params_card:
                with ui.row().classes('w-full items-center'):
                    self.click_position = ui.select(
                        label='Click Position',
                        options=[
                            'center', 'top_left', 'top_right', 
                            'bottom_left', 'bottom_right', 'top_center',
                            'bottom_center', 'left_center', 'right_center'
                        ],
                        value='center'
                    ).classes('w-1/3')
                    
                    self.click_button_img = ui.select(
                        label='Button',
                        options=['left', 'middle', 'right'],
                        value='left'
                    ).classes('w-1/3')
                    
                    self.confidence = ui.number(
                        label='Confidence',
                        value=0.72,
                        min=0.1,
                        max=1.0,
                        step=0.01,
                        format='%.2f'
                    ).classes('w-1/3')
                
                with ui.row().classes('w-full'):
                    self.max_attempts = ui.number(
                        label='Max Attempts',
                        value=10,
                        min=1,
                        step=1
                    ).classes('w-1/2')
                    
                    self.retry_interval = ui.number(
                        label='Retry Interval (s)',
                        value=0.5,
                        min=0.1,
                        step=0.1,
                        format='%.1f'
                    ).classes('w-1/2')
        elif step_type == 'Type Text':
            with self.params_card:
                self.text_to_type = ui.textarea('Text to Type').classes('w-full') # Prefer textarea over input
        elif step_type == 'Delay':
            with self.params_card:
                self.delay_seconds = ui.number(
                    'Seconds', 
                    min=0.1, 
                    max=60, 
                    value=1.0, 
                    step=0.1,
                    format='%.1f'
                ).classes('w-full') # Added classes for consistency
        elif step_type == 'Screenshot':
            with self.params_card:
                self.screenshot_name = ui.input('Screenshot Name (optional)').classes('w-full') # Prefer allowing a name
    
    async def handle_upload(self, e: ui.events.UploadEventArguments):
        """Handle file upload for image steps."""
        try:
            filename = e.name
            content_stream = e.content  # This is a BytesIO stream

            if not filename:
                ui.notify("Upload event is missing filename.", type='warning')
                return None

            content = content_stream.read()  # Read bytes from the stream

            if not content:
                ui.notify(f"Uploaded file '{filename}' is empty or could not be read.", type='warning')
                return None

            # Create temp directory if it doesn't exist
            os.makedirs(self.temp_dir, exist_ok=True)

            # Generate a unique filename to avoid conflicts
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{int(time.time())}{ext}"
            temp_path = os.path.join(self.temp_dir, unique_filename)

            # Save to temp file
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            # Store the path with both original and unique filenames as keys
            self.uploaded_images[unique_filename] = temp_path
            
            # Update the dropdown if it exists
            if hasattr(self, 'image_selector'):
                current_options = list(self.image_selector.options)
                if unique_filename not in current_options:
                    current_options.append(unique_filename)
                self.image_selector.options = sorted(current_options) # Keep sorted for better UX
                self.image_selector.value = unique_filename # Auto-select the new image
                self.image_selector.update() # Ensure UI reflects changes

            # Show preview if the element exists
            if hasattr(self, 'image_preview'):
                self.image_preview.set_source(temp_path)
                self.image_preview.set_visibility(True)
                self.image_preview.update()

            # Make sure the upload card is visible
            if hasattr(self, 'upload_card'):
                self.upload_card.set_visibility(True)
                
            ui.notify(f"Uploaded '{filename}' as '{unique_filename}'. It has been auto-selected.")
            return temp_path
            
        except Exception as ex_upload:
            ui.notify(f"Error handling upload: {str(ex_upload)}", type='negative')
            import traceback
            self.log(f"Upload error: {traceback.format_exc()}", level='error')
            return None
            
    def add_step(self, step_type: str):
        """Add a new step to the automation."""
        step = {'type': step_type, 'params': {}}
        
        if step_type == 'Click':
            step['params'] = {
                'x_position': self.click_x.value,
                'y_position': self.click_y.value,
                'button': self.click_button.value
            }
        elif step_type == 'Type Text':
            step['params'] = {
                'text': self.text_to_type.value
            }
        elif step_type == 'Delay':
            step['params'] = {
                'seconds': self.delay_seconds.value
            }
        elif step_type == 'Screenshot':
            step['params'] = {
                'name': self.screenshot_name.value if hasattr(self, 'screenshot_name') and self.screenshot_name.value else f'screenshot_{int(time.time())}'
            }
        elif step_type == 'Find and Click Image':
            if not hasattr(self, 'image_selector') or not self.image_selector.value:
                ui.notify("Please upload and select an image first", type='warning')
                return
                
            selected_image = self.image_selector.value
            if selected_image not in self.uploaded_images:
                ui.notify("Selected image not found. Please upload it again.", type='warning')
                return
                
            image_path = self.uploaded_images[selected_image]
            if not os.path.exists(image_path):
                ui.notify("Image file not found. Please upload it again.", type='warning')
                return
                
            step['params'] = {
                'image_path': image_path,
                'image_name': selected_image,
                'position': self.click_position.value if hasattr(self, 'click_position') else 'center',
                'button': self.click_button_img.value if hasattr(self, 'click_button_img') else 'left',
                'confidence': float(self.confidence.value) if hasattr(self, 'confidence') else 0.72,
                'max_attempts': int(self.max_attempts.value) if hasattr(self, 'max_attempts') else 10,
                'retry_interval': float(self.retry_interval.value) if hasattr(self, 'retry_interval') else 0.5
            }
        
        self.step_counter += 1
        self.automation_steps.append(step)
        self.update_steps_list()
        ui.notify(f"Added step: {step_type}")

    def update_steps_list(self):
        """Update the UI list of automation steps."""
        self.steps_list.clear()
        with self.steps_list:
            for i, step_data in enumerate(self.automation_steps):
                with ui.row().classes('w-full items-center justify-between p-2 border-b'):
                    details = f"{i+1}. {step_data['type'].replace('_', ' ').title()}"
                    if step_data['params']:
                        param_str = ", ".join(f"{k}: {v}" for k, v in step_data['params'].items())
                        details += f" ({param_str})"
                    ui.label(details)
                    ui.button(icon='delete', on_click=lambda _, idx=i: self.remove_step(idx)).props('flat dense').classes('text-red-500')

    def remove_step(self, index: int):
        """Remove a step from the automation."""
        if 0 <= index < len(self.automation_steps):
            removed = self.automation_steps.pop(index)
            self.update_steps_list()
            ui.notify(f"Removed step: {removed['type'].replace('_', ' ').title()}")
    
    async def find_image_on_screen(self, image_path: str, confidence: float, max_attempts: int, retry_interval: float):
        """Find an image on the screen using template matching."""
        try:
            self.log(f"Searching for image: {os.path.basename(image_path)}")
            
            # Load the template image
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if template is None:
                self.log(f"Error: Could not load image {image_path}", 'error')
                return None
                
            # Convert to grayscale for matching
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            template_h, template_w = template_gray.shape[:2]
            
            self.log(f"Template size: {template_w}x{template_h}, Confidence threshold: {confidence}")
                
            for attempt in range(max_attempts):
                try:
                    self.log(f"Attempt {attempt + 1}/{max_attempts} to find image...")
                    
                    # Take a screenshot and convert to BGR (OpenCV format)
                    screenshot = pyautogui.screenshot()
                    screenshot_np = np.array(screenshot)
                    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
                    
                    # Perform template matching with multiple methods
                    methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF_NORMED]
                    best_match = {'val': -1, 'loc': None, 'method': None}
                    
                    for method in methods:
                        try:
                            result = cv2.matchTemplate(screenshot_gray, template_gray, method)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            
                            # For TM_SQDIFF_NORMED, the best match is the minimum value
                            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                                if min_val > best_match['val']:
                                    best_match = {'val': min_val, 'loc': min_loc, 'method': method}
                            else:
                                if max_val > best_match['val']:
                                    best_match = {'val': max_val, 'loc': max_loc, 'method': method}
                        except Exception as e:
                            self.log(f"Warning: Template matching with method {method} failed: {str(e)}", 'warning')
                    
                    match_confidence = best_match['val']
                    self.log(f"Best match confidence: {match_confidence:.4f} (threshold: {confidence})")
                    
                    if match_confidence >= confidence:
                        # Calculate positions based on the best match
                        top_left = best_match['loc']
                        bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
                        center = (top_left[0] + template_w // 2, top_left[1] + template_h // 2)
                        
                        # For debugging, save the matched region
                        try:
                            debug_img = screenshot_np.copy()
                            cv2.rectangle(debug_img, top_left, bottom_right, (0, 255, 0), 2)
                            debug_path = os.path.join(self.temp_dir, f"match_debug_{int(time.time())}.png")
                            cv2.imwrite(debug_path, cv2.cvtColor(debug_img, cv2.COLOR_RGB2BGR))
                            self.log(f"Match visualization saved to {debug_path}")
                        except Exception as e:
                            self.log(f"Warning: Could not save match visualization: {str(e)}", 'warning')
                        
                        return {
                            'found': True,
                            'confidence': float(match_confidence),
                            'top_left': top_left,
                            'bottom_right': bottom_right,
                            'center': center,
                            'width': template_w,
                            'height': template_h,
                            'top_right': (bottom_right[0], top_left[1]),
                            'bottom_left': (top_left[0], bottom_right[1]),
                            'top_center': (center[0], top_left[1]),
                            'bottom_center': (center[0], bottom_right[1]),
                            'left_center': (top_left[0], center[1]),
                            'right_center': (bottom_right[0], center[1])
                        }
                    
                    if attempt < max_attempts - 1:
                        self.log(f"No match found, retrying in {retry_interval} seconds...")
                        await asyncio.sleep(retry_interval)
                        
                except Exception as e:
                    error_msg = f"Error in attempt {attempt + 1}: {str(e)}"
                    self.log(error_msg, 'error')
                    import traceback
                    self.log(traceback.format_exc(), 'error')
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(retry_interval)
            
            self.log(f"Could not find image after {max_attempts} attempts", 'warning')
            return None
            
        except Exception as e:
            self.log(f"Error finding image: {str(e)}", 'error')
            return None
            
    async def execute_step(self, step: Dict[str, Any]):
        """Execute a single automation step."""
        step_type = step['type']
        params = step['params']
        
        try:
            if step_type == 'Move Mouse':
                self.log(f"Moving mouse to ({params['x_position']}, {params['y_position']})")
                pyautogui.moveTo(params['x_position'], params['y_position'])

            elif step_type == 'Find and Click Image':
                image_path = params.get('image_path')
                if not image_path or not os.path.exists(image_path):
                    self.log(f"Error: Image file not found at {image_path}", 'error')
                    return False
                    
                self.log(f"Looking for image: {params.get('image_name', 'unknown')}")
                
                # Take a screenshot for debugging
                try:
                    screenshot_path = os.path.join(self.temp_dir, f"screenshot_{int(time.time())}.png")
                    pyautogui.screenshot(screenshot_path)
                    self.log(f"Screenshot saved to {screenshot_path}")
                except Exception as e:
                    self.log(f"Warning: Could not save screenshot: {str(e)}", 'warning')
                
                # Find the image on screen
                result = await self.find_image_on_screen(
                    image_path=image_path,
                    confidence=params.get('confidence', 0.72),
                    max_attempts=params.get('max_attempts', 10),
                    retry_interval=params.get('retry_interval', 0.5)
                )
                
                if result and result['found']:
                    # Get the click position based on the selected position
                    click_pos_key = params.get('position', 'center')
                    click_x, click_y = result.get(click_pos_key, result['center']) # Ensure key exists
                    
                    # Move to the position and click
                    self.log(f"Found image at {click_pos_key} position: ({click_x},{click_y}) (confidence: {result['confidence']:.2f})")
                    pyautogui.moveTo(click_x, click_y)
                    pyautogui.click(button=params.get('button', 'left'))
                    self.log(f"Clicked at ({click_x},{click_y}) with {params.get('button', 'left')} button")
                else:
                    self.log(f"Could not find image '{params.get('image_name', 'unknown')}' after {params.get('max_attempts', 10)} attempts", 'error')
                    return False # Return False on failure
                
            elif step_type == 'Click':
                self.log(f"Clicking at ({params['x_position']}, {params['y_position']}) with {params['button']} button")
                pyautogui.click(params['x_position'], params['y_position'], button=params['button'])
                
            elif step_type == 'Type Text':
                text = params['text']
                self.log(f"Typing: {text[:20]}{'...' if len(text) > 20 else ''}")
                pyautogui.write(text)
                
            elif step_type == 'Delay':
                delay = params['seconds']
                self.log(f"Waiting for {delay} seconds")
                await asyncio.sleep(delay)
                
            elif step_type == 'Screenshot':
                self.log("Taking screenshot")
                screenshot = pyautogui.screenshot()
                # In a real app, you might want to save or display the screenshot
                
            return True
            
        except Exception as e:
            self.log(f"Error executing step: {str(e)}", 'error')
            return False
            
    async def run_all_steps(self):
        """Execute all automation steps."""
        self.log('Starting automation...')
        
        for step in self.automation_steps:
            try:
                if not await self.execute_step(step):
                    self.log(f"Step failed: {step['type']}", 'error')
                    break
                await asyncio.sleep(0.1)  # Small delay between steps
            except Exception as e:
                self.log(f"Error executing step: {e}", 'error')
                break
        
        self.log('Automation completed!')
    
    def clear_steps(self):
        """Clear all automation steps."""
        self.automation_steps = []
        self.steps_list.clear()
        self.log('Cleared all steps')
    
    def log(self, message: str, level: str = 'info'):
        """Add a message to the log."""
        if level == 'error':
            self.log_area.push('ERROR: ' + message)
        else:
            self.log_area.push(message)
            
    def _cleanup_temp_dir(self):
        """Remove the temporary image directory."""
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                print(f"Error cleaning up temp directory {self.temp_dir}: {e}", file=sys.stderr)

def main():
    """Start the application."""
    # Set the correct display
    current_display = os.environ.get('DISPLAY', ':0')
    print(f"Using display: {current_display}")
    
    # Create the application
    app = GUIAutomationTool()
    
    # Start the application
    print("\nStarting GUI Automation Tool...")
    if not PYAUTOGUI_AVAILABLE:
        print("Warning: Running in simulation mode. Install PyAutoGUI for full functionality.")
    print("Please open your web browser and navigate to: http://localhost:8080")
    print("Press Ctrl+C to stop the application\n")
    
    try:
        # Run the application
        ui.run(title='GUI Automation Tool', port=8080, reload=False, show=False)
    except Exception as e:
        print(f"Error starting application: {e}")
        print(f"\nCurrent DISPLAY environment variable: {current_display}")
        print("If you're having display issues, try setting the correct display:")
        print("  export DISPLAY=:1  # or :0, depending on your system")
        print("Then run the application again.")
    
    print("\nApplication closed. Press Ctrl+C to exit completely.")

if __name__ == "__main__":
    main()
