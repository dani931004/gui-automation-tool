"""
Image-based automation utilities for the GUI Automation Tool.
Uses OpenCV for template matching and PyAutoGUI for mouse control.
"""
import os
import time
import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple, Dict, Any
import tempfile

class ImageAutomation:
    def __init__(self, confidence_threshold: float = 0.72):
        """
        Initialize the ImageAutomation class.
        
        Args:
            confidence_threshold: Minimum confidence score for template matching (0.0 to 1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.temp_dir = tempfile.mkdtemp(prefix='gui_automation_')
        
    def find_image(self, template_path: str, retry_interval: float = 0.5, max_attempts: int = 10) -> Optional[Dict[str, Any]]:
        """
        Find an image on the screen using template matching.
        
        Args:
            template_path: Path to the template image to find
            retry_interval: Seconds to wait between retry attempts
            max_attempts: Maximum number of attempts to find the image
            
        Returns:
            Dict containing match information or None if not found
        """
        if not os.path.exists(template_path):
            print(f"Error: Template image not found at {template_path}")
            return None
            
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Error: Could not read template image at {template_path}")
            return None
            
        for attempt in range(max_attempts):
            try:
                # Take screenshot
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= self.confidence_threshold:
                    # Calculate positions relative to the found image
                    h, w = template.shape
                    top_left = max_loc
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    center = (top_left[0] + w // 2, top_left[1] + h // 2)
                    
                    return {
                        'found': True,
                        'confidence': float(max_val),
                        'top_left': top_left,
                        'bottom_right': bottom_right,
                        'center': center,
                        'width': w,
                        'height': h,
                        'top_right': (bottom_right[0], top_left[1]),
                        'bottom_left': (top_left[0], bottom_right[1]),
                        'top_center': (center[0], top_left[1]),
                        'bottom_center': (center[0], bottom_right[1]),
                        'left_center': (top_left[0], center[1]),
                        'right_center': (bottom_right[0], center[1])
                    }
                
                if attempt < max_attempts - 1:
                    time.sleep(retry_interval)
                    
            except Exception as e:
                print(f"Error during image search (attempt {attempt + 1}): {str(e)}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(retry_interval)
                
        return None
    
    def move_to_image(self, template_path: str, position: str = 'center', 
                      click: bool = False, button: str = 'left', 
                      retry_interval: float = 0.5, max_attempts: int = 10) -> Optional[Tuple[int, int]]:
        """
        Move the mouse to a position relative to a found image.
        
        Args:
            template_path: Path to the template image to find
            position: Where to move relative to the found image. Can be:
                     'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right',
                     'top_center', 'bottom_center', 'left_center', 'right_center'
            click: Whether to click after moving
            button: Mouse button to click ('left', 'middle', 'right')
            retry_interval: Seconds to wait between retry attempts
            max_attempts: Maximum number of attempts to find the image
            
        Returns:
            (x, y) coordinates where the mouse was moved, or None if image not found
        """
        result = self.find_image(template_path, retry_interval, max_attempts)
        if not result or not result['found']:
            print(f"Could not find image: {template_path}")
            return None
            
        # Get the requested position
        if position not in result:
            print(f"Invalid position: {position}. Defaulting to center.")
            position = 'center'
            
        target_x, target_y = result[position]
        
        # Move the mouse
        pyautogui.moveTo(target_x, target_y, duration=0.3)
        
        # Click if requested
        if click:
            pyautogui.click(button=button)
            
        return (target_x, target_y)
    
    def click_image(self, template_path: str, position: str = 'center', 
                   button: str = 'left', **kwargs) -> Optional[Tuple[int, int]]:
        """
        Click on a position relative to a found image.
        
        Args:
            template_path: Path to the template image to find
            position: Where to click relative to the found image
            button: Mouse button to click ('left', 'middle', 'right')
            **kwargs: Additional arguments passed to move_to_image()
            
        Returns:
            (x, y) coordinates where clicked, or None if image not found
        """
        return self.move_to_image(template_path, position, click=True, button=button, **kwargs)

# Helper function for backward compatibility
def move_mouse(template_path: str = "", position: str = 'center', 
              click: bool = False, button: str = 'left', 
              confidence: float = 0.72, **kwargs):
    """
    Simplified interface for moving/clicking relative to an image.
    
    Args:
        template_path: Path to the template image to find
        position: Position relative to the found image
        click: Whether to click after moving
        button: Mouse button to click
        confidence: Minimum confidence threshold (0.0 to 1.0)
        **kwargs: Additional arguments for move_to_image
        
    Returns:
        (x, y) coordinates where moved/clicked, or None if image not found
    """
    automator = ImageAutomation(confidence_threshold=confidence)
    if click:
        return automator.click_image(template_path, position, button, **kwargs)
    else:
        return automator.move_to_image(template_path, position, False, button, **kwargs)
