"""
Image processing and template matching utilities for the GUI Automation Tool.
"""
import os
import cv2
import numpy as np
import pyautogui
from typing import Dict, Any, Optional, Tuple

def find_image_on_screen(image_path: str, confidence: float = 0.7, max_attempts: int = 1, 
                       retry_interval: float = 0.5) -> Optional[Dict[str, Any]]:
    """
    Find an image on the screen using template matching.
    
    Args:
        image_path: Path to the template image
        confidence: Minimum confidence threshold (0-1)
        max_attempts: Maximum number of attempts to find the image
        retry_interval: Time to wait between attempts in seconds
        
    Returns:
        Dict containing match information or None if not found
    """
    try:
        # Load the template image
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if template is None:
            return None
            
        for attempt in range(max_attempts):
            try:
                # Take a screenshot
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= confidence:
                    # Calculate positions
                    h, w = template.shape[:2]
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
                    import time
                    time.sleep(retry_interval)
                    
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(retry_interval)
                
        return None
        
    except Exception as e:
        raise Exception(f"Error finding image: {str(e)}")
