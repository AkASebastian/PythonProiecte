import cv2
import pyautogui
import numpy as np
import time

def detect_red_circles_and_click():
    # Take a screenshot
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)

    # Convert screenshot to OpenCV's BGR format
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Convert to HSV color space to detect red color
    hsv_image = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)

    # Define range for red color
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Mask red areas
    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = mask1 + mask2

    # Detect circles using HoughCircles
    gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(
        gray, 
        cv2.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=20, 
        param1=50, 
        param2=30, 
        minRadius=10, 
        maxRadius=50
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            # Check if the circle area contains red color
            if red_mask[y, x] > 0:
                # Move mouse to the circle center and click
                pyautogui.moveTo(x, y, duration=0.1)  # Quick mouse movement
                pyautogui.click()  # Click at the current mouse position
                print(f"Clicked on circle at ({x}, {y})")
                time.sleep(0.05)  # Short delay between clicks for speed

if __name__ == "__main__":
    while True:
        detect_red_circles_and_click()
        time.sleep(0.05)  # Short delay before the next screen capture
