import time
import pydirectinput as pdi
import pyautogui as pag

def press_key(key, times, thelddown, tinbetween):
    for _ in range(times):
        pdi.keyDown(key)
        time.sleep(thelddown)
        pdi.keyUp(key)
        time.sleep(tinbetween)


def hold_key(key, dur):
    pdi.keyDown(key)
    time.sleep(dur)
    pdi.keyUp(key)

def hold_key_with_rmb(key, dur):
    """For WASD movement - requires right mouse button."""
    pdi.mouseDown(button='right')
    pdi.keyDown(key)
    time.sleep(dur)
    pdi.keyUp(key)
    pdi.mouseUp(button='right')


def move_forward(duration):
    hold_key_with_rmb("w", duration)

def move_backward(duration):
    hold_key_with_rmb("s", duration)


def move_left(duration):
    hold_key_with_rmb("a", duration)


def move_right(duration):
    hold_key_with_rmb("d", duration)


def in_place_rotate_to_left(duration):
    hold_key("left", duration)


def in_place_rotate_to_right(duration):
    hold_key("right", duration)


def look_up(duration):
    hold_key("up", duration)


def look_down(duration):
    hold_key("down", duration)


def press_button(duration):
    hold_key("u", duration)


def screenshot(counter, region, orbit=False):
    # Define the bounding box (left, top, width, height)
    # Captures a 500x400 area starting from (100,100)

    # Take a screenshot of the specified region
    screenshot = pag.screenshot(region=region)

    # Save the screenshot
    # screenshot.save(f"screenshot{counter}.png")
    # screenshot.save(f"screenshots/screenshot{counter}.png")
    # screenshot.save(f"temp/screenshot_original/screenshot{counter}.png")
    if(orbit):
        screenshot.save(f"temp/orbit_screenshots/screenshot{counter}.png")
    else:
        screenshot.save(f"temp/screenshot_original/screenshot{counter}.png")
    
    return screenshot
    # image.save("screenshot.png")
