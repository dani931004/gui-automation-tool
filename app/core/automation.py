"""
Core automation logic for the GUI Automation Tool.
"""
import asyncio
import os
import pyautogui
from typing import Dict, Any, Optional, Callable, List

from .models import AutomationStep, AutomationState, ButtonType, PositionType
from ..utils.image_utils import find_image_on_screen

class AutomationEngine:
    """Handles execution of automation steps."""
    
    def __init__(self, state: AutomationState, log_callback: Callable[[str, str], None]):
        """Initialize with state and logging callback.
        
        Args:
            state: The automation state
            log_callback: Function to call with log messages (message: str, level: str)
        """
        self.state = state
        self.log = log_callback
        self._setup_pyautogui()
    
    def _setup_pyautogui(self) -> None:
        """Configure PyAutoGUI settings."""
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True
    
    async def execute_step(self, step: AutomationStep) -> bool:
        """Execute a single automation step.
        
        Args:
            step: The step to execute
            
        Returns:
            bool: True if step executed successfully, False otherwise
        """
        step_type = step.get('type', '').lower()
        params = step.get('params', {})
        
        try:
            if step_type == 'move mouse':
                await self._execute_move_mouse(params)
            elif step_type == 'click':
                await self._execute_click(params)
            elif step_type == 'type text':
                await self._execute_type_text(params)
            elif step_type == 'delay':
                await self._execute_delay(params)
            elif step_type == 'screenshot':
                await self._execute_screenshot(params)
            elif step_type == 'find and click image':
                return await self._execute_find_and_click_image(params)
            elif step_type == 'press hotkey':
                await self._execute_press_hotkey(params)
            else:
                self.log(f"Unknown step type: {step_type}", 'error')
                return False
                
            return True
            
        except Exception as e:
            self.log(f"Error executing {step_type} step: {str(e)}", 'error')
            return False
    
    async def _execute_move_mouse(self, params: Dict[str, Any]) -> None:
        """Execute a move mouse step."""
        x = int(params.get('x', 0))
        y = int(params.get('y', 0))
        self.log(f"Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y)
    
    async def _execute_click(self, params: Dict[str, Any]) -> None:
        """Execute a click step."""
        x = int(params.get('x', 0))
        y = int(params.get('y', 0))
        button = params.get('button', 'left')
        self.log(f"Clicking at ({x}, {y}) with {button} button")
        pyautogui.click(x, y, button=button)
    
    async def _execute_type_text(self, params: Dict[str, Any]) -> None:
        """Execute a type text step."""
        text = params.get('text', '')
        self.log(f"Typing: {text[:20]}{'...' if len(text) > 20 else ''}")
        pyautogui.write(text)
    
    async def _execute_delay(self, params: Dict[str, Any]) -> None:
        """Execute a delay step."""
        delay = float(params.get('seconds', 0))
        self.log(f"Waiting for {delay} seconds")
        await asyncio.sleep(delay)
    
    async def _execute_screenshot(self, params: Dict[str, Any]) -> None:
        """Execute a screenshot step.
        
        Args:
            params: Dictionary containing screenshot parameters
        """
        try:
            self.log("[DEBUG] Starting screenshot capture...", 'debug')
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'gui-automation-tool', 'gui_automation_screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate timestamp for filename
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(screenshots_dir, f'screenshot_{timestamp}.png')
            
            # Take the screenshot
            try:
                self.log(f"[INFO] Capturing screenshot to {filename}", 'info')
                screenshot = pyautogui.screenshot()
                
                # Save the screenshot
                screenshot.save(filename)
                self.log(f"[SUCCESS] Screenshot saved to {filename}", 'success')
                
            except Exception as e:
                self.log(f"[ERROR] Failed to take screenshot: {str(e)}", 'error')
                self.log("[INFO] Make sure you have a display server running (X11 or Wayland)", 'info')
                import traceback
                self.log(f"[DEBUG] {traceback.format_exc()}", 'debug')
                
        except Exception as e:
            self.log(f"[ERROR] Unexpected error in screenshot: {str(e)}", 'error')
            import traceback
            self.log(f"[DEBUG] {traceback.format_exc()}", 'debug')
    
    async def _execute_find_and_click_image(self, params: Dict[str, Any]) -> bool:
        """Execute a find and click image step."""
        image_path = params.get('image_path')
        if not image_path or not os.path.exists(image_path):
            self.log("Image not found", 'error')
            return False
            
        position = params.get('position', 'center')
        button = params.get('button', 'left')
        confidence = float(params.get('confidence', 0.7))
        max_attempts = int(params.get('max_attempts', 1))
        retry_interval = float(params.get('retry_interval', 0.5))
        
        self.log(f"Searching for image: {os.path.basename(image_path)}")
        
        try:
            result = find_image_on_screen(
                image_path=image_path,
                confidence=confidence,
                max_attempts=max_attempts,
                retry_interval=retry_interval
            )
            
            if result and result.get('found'):
                target_pos = result.get(position, result['center'])
                self.log(f"Found image at {target_pos}, clicking with {button} button")
                pyautogui.click(target_pos[0], target_pos[1], button=button)
                return True
            else:
                self.log("Image not found on screen", 'warning')
                return False
                
        except Exception as e:
            self.log(f"Error finding/clicking image: {str(e)}", 'error')
            return False

    async def _execute_press_hotkey(self, params: Dict[str, Any]) -> None:
        """Execute a press hotkey step."""
        keys = params.get('keys', [])
        modifiers = params.get('modifiers', [])

        if not keys and not modifiers:
            self.log("No keys or modifiers specified for hotkey.", 'warning')
            return

        all_keys_to_press = modifiers + keys
        self.log(f"Pressing hotkey: {', '.join(all_keys_to_press)}")
        pyautogui.hotkey(*all_keys_to_press)
