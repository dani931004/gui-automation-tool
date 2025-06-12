def move_mouse(object_path="", tp_left=None, bt_right=None, center=None, tp_right=None, bt_left=None, bt_center=None, tp_center=None, sleep=0):
    import sys
    import site
    # Use environment with selenium
    sys.path.append('/home/dani/Desktop/env/lib/python3.8/site-packages')
    sys.path.append('/home/dani/Desktop/env/bin')
    site.addsitedir('/home/dani/Desktop/env/lib/python3.8/site-packages')
    import cv2
    import numpy as np
    import pyscreenshot as ImageGrab
    import subprocess
    from time import sleep as slp
    if object_path == "":
        with open('/home/dani/Desktop/png/obj.png', 'wb') as f:
            ImageGrab.grab().save(f, 'PNG')
        object_path = "/home/dani/Desktop/png/obj.png"
    slp(sleep)
    # Take a screenshot of the current screen
    screenshot_path = "/home/dani/Desktop/png/scr.png"
    ImageGrab.grab().save(screenshot_path)

    # Find the object coordinates
    with open(screenshot_path, "rb") as f:
        screenshot = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    with open(object_path, "rb") as f:
        object_image = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

    # Ensure both images are loaded correctly
    if screenshot is None:
        print("Error: Screenshot image could not be loaded or is None.")
        return None, None
    if object_image is None:
        print(f"Error: Object image at {object_path} could not be loaded or is None.")
        return None, None
    # Ensure template is not larger than the screenshot
    if (object_image.shape[0] > screenshot.shape[0]) or (object_image.shape[1] > screenshot.shape[1]):
        print(f"Error: Template image (object_image) is larger than the screenshot.\nTemplate size: {object_image.shape}, Screenshot size: {screenshot.shape}")
        return None, None

    result = cv2.matchTemplate(screenshot, object_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Extract the coordinates of the best match
    top_left = max_loc
    top_right = (top_left[0] + object_image.shape[1], top_left[1])
    bot_left = (top_left[0], top_left[1] + object_image.shape[0])
    top_left = (top_left[0], top_left[1])
    bot_right = (top_left[0] + object_image.shape[1], top_left[1] + object_image.shape[0])
    object_center = (top_left[0] + object_image.shape[1] // 2, top_left[1] + object_image.shape[0] // 2)
    bot_center = (top_left[0] + object_image.shape[1] // 2, top_left[1] + object_image.shape[0])
    top_center = (top_left[0] + object_image.shape[1] // 2, top_left[1])

    # Move the mouse to the specified coordinates
    def move_mouse_to(x, y):
        subprocess.run(["xdotool", "mousemove", str(x), str(y)])

    coords = {
        'tp_left': top_left,
        'bt_right': bot_right,
        'tp_right': top_right,
        'bt_left': bot_left,
        'center': object_center,
        'tp_center': top_center,
        'bt_center': bot_center
    }
    if any(arg is not None for arg in [tp_left, bt_right, tp_right, bt_left, center, tp_center, bt_center]):
        coords_to_move = next((arg for arg in coords if vars().get(arg)), None)
        move_mouse_to(*coords[coords_to_move])
        return coords[coords_to_move]






# Testing
def move_mouse(object_path="", tp_left=None, bt_right=None, center=None, tp_right=None, bt_left=None, bt_center=None, tp_center=None, sleep=0.2):
    import sys
    import site
    # Use environment with selenium
    sys.path.append('/home/dani/Desktop/env/lib/python3.8/site-packages')
    sys.path.append('/home/dani/Desktop/env/bin')
    site.addsitedir('/home/dani/Desktop/env/lib/python3.8/site-packages')
    import cv2
    import numpy as np
    import pyscreenshot as ImageGrab
    import subprocess
    from time import sleep as slp
    if object_path == "":
        with open('/home/dani/Desktop/png/obj.png', 'wb') as f:
            ImageGrab.grab().save(f, 'PNG')
        object_path = "/home/dani/Desktop/png/obj.png"


    while True:
        slp(sleep)
        # Take a screenshot of the current screen
        screenshot_path = "/home/dani/Desktop/png/scr.png"
        ImageGrab.grab().save(screenshot_path)

        # Find the object coordinates
        with open(screenshot_path, "rb") as f:
            screenshot = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        with open(object_path, "rb") as f:
            object_image = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

        # Ensure both images are loaded correctly
        if screenshot is None:
            print("Error: Screenshot image could not be loaded or is None.")
            return None, None
        if object_image is None:
            print(f"Error: Object image at {object_path} could not be loaded or is None.")
            return None, None
        # Ensure template is not larger than the screenshot
        if (object_image.shape[0] > screenshot.shape[0]) or (object_image.shape[1] > screenshot.shape[1]):
            print(f"Error: Template image (object_image) is larger than the screenshot.\nTemplate size: {object_image.shape}, Screenshot size: {screenshot.shape}")
            return None, None

        result = cv2.matchTemplate(screenshot, object_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= 0.718:
            break
        else:
            print("Match value: ", max_val)
            screenshot_path = "/home/dani/Desktop/png/scr.png"
            ImageGrab.grab().save(screenshot_path)
            with open(screenshot_path, "rb") as f:
                screenshot = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

    # Extract the coordinates of the best match
    top_left = max_loc
    top_right = (top_left[0] + object_image.shape[1], top_left[1])
    bot_left = (top_left[0], top_left[1] + object_image.shape[0])
    top_left = (top_left[0], top_left[1])
    bot_right = (top_left[0] + object_image.shape[1], top_left[1] + object_image.shape[0])
    object_center = (top_left[0] + object_image.shape[1] // 2, top_left[1] + object_image.shape[0] // 2)
    bot_center = (top_left[0] + object_image.shape[1] // 2, top_left[1] + object_image.shape[0])
    top_center = (top_left[0] + object_image.shape[1] // 2, top_left[1])

    # Move the mouse to the specified coordinates
    def move_mouse_to(x, y):
        subprocess.run(["xdotool", "mousemove", str(x), str(y)])

    if tp_left:
        move_mouse_to(*top_left)
        x = top_left[0]
        y = top_left[1]
        return x,y
    elif bt_right:
        move_mouse_to(*bot_right)
        x = bot_right[0]
        y = bot_right[1]
        return x,y
    elif tp_right:
        move_mouse_to(*top_right)
        x = top_right[0]
        y = top_right[1]
        return x,y
    elif bt_left:
        move_mouse_to(*bot_left)
        x = bot_left[0]
        y = bot_left[1]
        return x,y
    elif center:
        move_mouse_to(*object_center)
        x = object_center[0]
        y = object_center[1]
        return x,y
    elif tp_center:
        move_mouse_to(*top_center)
        x = top_center[0]
        y = top_center[1]
        return x,y
    elif bt_center:
        move_mouse_to(*bot_center)
        x = bot_center[0]
        y = bot_center[1]
        return x,y

# x,y = move_mouse(object_path="/home/dani/Desktop/png/redmine_time.png",tp_right=True)

# print(x,y)