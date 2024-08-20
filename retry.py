import pytesseract
import cv2
import numpy as np
import pyautogui
import time

# Define the bounding box of the game region
bounding_box = (2037, 344, 465, 494)

# Path to the Tesseract executable (update this path if necessary)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def detect_text_in_bounding_box(bounding_box):
    # Capture the screenshot of the bounding box
    screen = np.array(pyautogui.screenshot(region=bounding_box))
    gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray_screen, lang='eng')

    return "Jogar" in text


def main():
    if detect_text_in_bounding_box(bounding_box):
        print("Retry button detected. Clicking on the screen...")
        pyautogui.click(2280,770)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)
