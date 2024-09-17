import pyautogui
import clipboard
import time
import numpy as np
from common import *


intellij_click_coordinates = (200, 200)


class ContainsFaultError(Exception):
    pass


def print_red(text, pause=True):
    # ANSI escape code for red text
    red_start = "\033[91m"
    reset = "\033[0m"  # Resets the color to default
    print(red_start + text + reset)
    if pause:
        input('Press any key to continue...')
        click_on_intelij()


def click_on_intelij():
    # Move the mouse to specific coordinates
    pyautogui.moveTo(intellij_click_coordinates)  # Moves the mouse to the screen position x=100, y=150
    # Click the mouse at the current position
    pyautogui.click()


def open_file(file_path):
    # Copy file path to clipboard
    message = f'{file_path}'
    clipboard.copy(message)
    # Keyboard shift command O
    pyautogui.hotkey('shift', 'command', 'o')
    # Paste the new file path
    pyautogui.hotkey('command', 'v')
    # Wait for the file path to be pasted
    time.sleep(0.3)
    # Hit enter
    pyautogui.press('enter')
    # Wait for the file to open
    time.sleep(0.2)


def seek_position(line: int, index: int):
    # Formulate the string
    message = f'{line}:{index}'
    # Keyboard command L
    pyautogui.hotkey('command', 'l')
    time.sleep(0.1)
    # Paste the new file path
    pyautogui.write(message)
    # Wait for the file path to be pasted
    time.sleep(0.1)
    # Hit enter
    pyautogui.press('enter')


def is_color_near(color1, color2, tolerance=10):
    """Check if color1 is within the tolerance range of color2."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    distance = ((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) ** 0.5
    return distance <= tolerance


def find_near_color(target_color, colors, tolerance=10):
    """Search for any color in the set that is close to the target color within the specified tolerance."""
    for color in colors:
        if is_color_near(color, target_color, tolerance):
            return True
    return False


def contains_choice():
    # Take a screenshot of a region
    screenshot = pyautogui.screenshot(region=(27, 108, 350, 350))
    screenshot = screenshot.convert('RGB')
    # Extract colors from the screenshot
    colors = set(screenshot.getdata())
    # Define the target color
    target_color = color_4
    # Check for near color match
    return find_near_color(target_color, colors, tolerance=30)


def contains_button():
    # Take a screenshot of a region
    screenshot = pyautogui.screenshot(region=(27, 108, 350, 350))
    screenshot = screenshot.convert('RGB')
    # Extract colors from the screenshot
    colors = set(screenshot.getdata())
    # Define the target color
    target_color = color_5
    # Check for near color match
    return find_near_color(target_color, colors, tolerance=30)


def contains_fault():
    # Take a screenshot of a region
    screenshot = pyautogui.screenshot(region=(27, 108, 350, 350))
    screenshot = screenshot.convert('RGB')
    # Extract colors from the screenshot
    colors = set(screenshot.getdata())
    # Define the target color
    target_color = color_2
    # Check for near color match
    return find_near_color(target_color, colors, tolerance=30)


def unable_to_refactor():
    # Take a screenshot of a region
    screenshot = pyautogui.screenshot(region=(27, 108, 350, 350))
    screenshot = screenshot.convert('RGB')
    # Extract colors from the screenshot
    colors = set(screenshot.getdata())
    # Define the target color
    target_color = color_3
    # Check for near color match
    return find_near_color(target_color, colors, tolerance=0)


def able_to_refactor():
    # Take a screenshot of a region
    screenshot = pyautogui.screenshot(region=(27, 108, 350, 350))
    screenshot = screenshot.convert('RGB')
    # Extract colors from the screenshot
    colors = set(screenshot.getdata())
    # Define the target color
    target_color = color_1
    # Check for near color match
    return find_near_color(target_color, colors, tolerance=0)


def compare_images(image1, image2):
    # Convert images to numpy arrays
    img_array1 = np.array(image1)
    img_array2 = np.array(image2)

    # Check if the images have the same size and channel numbers
    if img_array1.shape != img_array2.shape:
        raise ValueError("Images do not have the same dimensions.")

    # Calculate the percentage of similar pixels
    identical_pixels = np.sum(img_array1 == img_array2)
    total_pixels = img_array1.size
    similarity = (identical_pixels / total_pixels) * 100
    return similarity


def refactor(new_name: str) -> bool:
    """

    :param new_name:
    :return:
    """
    # Keyboard shift F6
    pyautogui.hotkey('shift', 'f6')
    # Check for anomaly
    if contains_choice():
        pyautogui.press('esc')
        return False
        # # Hit enter
        # pyautogui.press('enter')

    # Test if unable to refactor
    if unable_to_refactor():
        print_red('Unable to refactor due to "unable to refactor popup".', pause=False)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('enter')
        return False

    # See if the blue backlight shows up
    if not able_to_refactor():
        print_red('Unable to refactor due to not finding blue bracket.', pause=False)
        return False

    # Take a pre-refactor screenshot
    pre_refactor_screenshot = pyautogui.screenshot(region=(27, 108, 340, 300))

    # Copy new name to clipboard
    clipboard.copy(new_name)
    # Paste the new file path
    pyautogui.hotkey('command', 'v')
    # Wait for the file path to be pasted
    time.sleep(0.2)
    # Hit enter
    pyautogui.press('enter')
    # Hit esc
    time.sleep(0.3)

    # Check for anomaly
    if contains_choice():
        pyautogui.press('esc')
        time.sleep(0.2)
        # Continue to check for anomalies
        while contains_choice():
            pyautogui.press('esc')
            time.sleep(0.2)
        # Revert change
        pyautogui.hotkey('command', 'z')
        time.sleep(0.5)
        if contains_button():
            pyautogui.press('enter')
        return False

    # Take a post-refactor screenshot
    time.sleep(0.2)
    post_refactor_screenshot = pyautogui.screenshot(region=(27, 108, 340, 300))

    # Compare the two screenshots, to check for conflict issues
    similarity = compare_images(pre_refactor_screenshot, post_refactor_screenshot)
    if similarity < 40:
        pyautogui.press('esc')
        return False

    return True

def close_file():

    # Keyboard command W
    pyautogui.hotkey('command', 'w')

def reload_from_file():
    # Keyboard command option command y
    pyautogui.hotkey('option', 'command', 'y')

def save_file():
    # Keyboard command S
    pyautogui.hotkey('command', 's')
    # Delay
    time.sleep(0.1)
