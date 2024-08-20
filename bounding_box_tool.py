import cv2
import numpy as np
import pyautogui

# Global variables for the bounding box selection
bounding_box = None
start_point = None
end_point = None
selection_in_progress = False
screenshot = None
scale_factor = 0.7


def select_bounding_box(event, x, y, flags, param):
    """Mouse callback function to select the bounding box."""
    global start_point, end_point, selection_in_progress, bounding_box, screenshot, scale_factor

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (int(x / scale_factor), int(y / scale_factor))
        selection_in_progress = True

    elif event == cv2.EVENT_MOUSEMOVE and selection_in_progress:
        end_point = (int(x / scale_factor), int(y / scale_factor))
        temp_image = screenshot.copy()
        cv2.rectangle(temp_image, start_point, end_point, (0, 255, 0), 2)
        temp_image = cv2.resize(temp_image, None, fx=scale_factor, fy=scale_factor)
        cv2.imshow('Select Bounding Box', temp_image)

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (int(x / scale_factor), int(y / scale_factor))
        selection_in_progress = False
        bounding_box = (start_point[0], start_point[1], end_point[0] - start_point[0], end_point[1] - start_point[1])
        cv2.destroyAllWindows()


def capture_and_select_bounding_box():
    """Capture the full screen and allow the user to select the bounding box."""
    global screenshot, scale_factor
    screenshot = np.array(pyautogui.screenshot())
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    scaled_screenshot = cv2.resize(screenshot, None, fx=scale_factor, fy=scale_factor)
    cv2.imshow('Select Bounding Box', scaled_screenshot)
    cv2.setMouseCallback('Select Bounding Box', select_bounding_box)
    cv2.waitKey(0)


if __name__ == "__main__":
    capture_and_select_bounding_box()

    if bounding_box:
        print(f"Selected bounding box: {bounding_box}")
    else:
        print("Bounding box selection was not successful.")
