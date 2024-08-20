import time
import cv2
import numpy as np
import pyautogui
import threading
from collections import deque

# Define the bounding box of the game region
bounding_box = (2037, 344, 465, 494)
grid_size = (14, 13)  # Number of grid cells in the game

# Load template images (example paths)
food_templates = [
    cv2.imread(f'assets/food{i}.png', cv2.IMREAD_GRAYSCALE) for i in range(1, 13)
]
snake_head_templates = {
    'up': cv2.imread('assets/head_up.png', cv2.IMREAD_GRAYSCALE),
    'down': cv2.imread('assets/head_down.png', cv2.IMREAD_GRAYSCALE),
    'left': cv2.imread('assets/head_left.png', cv2.IMREAD_GRAYSCALE),
    'right': cv2.imread('assets/head_right.png', cv2.IMREAD_GRAYSCALE),
}
snake_body_template = cv2.imread('assets/body.png', cv2.IMREAD_GRAYSCALE)
snake_tail_template = cv2.imread('assets/tail.png', cv2.IMREAD_GRAYSCALE)

# Template matching threshold
template_thresh = 0.83  # Lower threshold to capture lighter images

# Frame skip to reduce processing load
frame_skip = 5

# Initialize global variables
current_path = None
previous_food_position = None
snake_head_grid = None
food_grid = None
snake_body_positions = []
frame_count = 0


def detect_with_template(frame, template):
    """Detect objects in the frame using template matching."""
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= template_thresh)
    if len(loc[0]) > 0:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2
    return None


def preprocess_frame(frame):
    """Preprocess the frame to improve template matching."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray_frame, (5, 5), 0)


def detect_food(frame):
    """Detect food in the frame using multiple templates."""
    gray_frame = preprocess_frame(frame)
    for food_template in food_templates:
        food_position = detect_with_template(gray_frame, food_template)
        if food_position:
            return food_position
    return None


def detect_snake_head(frame):
    """Detect the snake's head and direction."""
    gray_frame = preprocess_frame(frame)
    for direction, template in snake_head_templates.items():
        head_position = detect_with_template(gray_frame, template)
        if head_position:
            return head_position, direction
    return None, None


def detect_snake_body(frame):
    """Detect the snake's body and tail."""
    gray_frame = preprocess_frame(frame)
    body_positions = []
    tail_position = detect_with_template(gray_frame, snake_tail_template)
    body_position = detect_with_template(gray_frame, snake_body_template)
    if body_position:
        # Convert the body position to grid coordinates
        grid_position = (body_position[1] // (bounding_box[3] // grid_size[0]),
                         body_position[0] // (bounding_box[2] // grid_size[1]))
        # Exclude the tail position from body positions
        if tail_position:
            tail_grid_position = (tail_position[1] // (bounding_box[3] // grid_size[0]),
                                  tail_position[0] // (bounding_box[2] // grid_size[1]))
            if grid_position != tail_grid_position:
                body_positions.append(grid_position)
    return body_positions, tail_position


def process_frame(frame):
    """Process the current frame to extract game state."""
    snake_head, snake_direction = detect_snake_head(frame)
    snake_body_positions, snake_tail = detect_snake_body(frame)
    food_position = detect_food(frame)
    return snake_head, snake_direction, food_position, snake_tail, snake_body_positions


def wrap_position(pos, max_x, max_y):
    """Handle wrapping behavior across the screen edges."""
    return pos[0] % max_x, pos[1] % max_y


def bfs(start, goal, grid):
    """Breadth-First Search (BFS) algorithm for pathfinding."""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for direction in directions:
            neighbor = wrap_position((current[0] + direction[0], current[1] + direction[1]), grid_size[0], grid_size[1])

            if neighbor not in came_from and grid[neighbor[0]][neighbor[1]] == 0:
                queue.append(neighbor)
                came_from[neighbor] = current

    return None


def get_direction(from_pos, to_pos):
    """Get the direction from one position to another."""
    if to_pos[0] < from_pos[0]:
        return 'up'
    if to_pos[0] > from_pos[0]:
        return 'down'
    if to_pos[1] < from_pos[1]:
        return 'left'
    if to_pos[1] > from_pos[1]:
        return 'right'


def create_debug_grid(snake_pos, food_pos, snake_body_positions, path):
    """Create a debug grid visualization."""
    grid_image = np.zeros((grid_size[0] * 20, grid_size[1] * 20, 3), dtype=np.uint8)

    # Colors
    snake_body_color = (0, 255, 0)  # Green for snake body
    path_color = (255, 255, 0)  # Yellow for path
    food_color = (0, 0, 255)  # Red for food

    for y in range(grid_size[0]):
        for x in range(grid_size[1]):
            # Draw grid cell border
            cv2.rectangle(grid_image, (x * 20, y * 20),
                          ((x + 1) * 20 - 1, (y + 1) * 20 - 1), (255, 255, 255), 1)  # White grid lines

    for pos in snake_body_positions:
        if 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]:
            cv2.rectangle(grid_image, (pos[1] * 20, pos[0] * 20),
                          ((pos[1] + 1) * 20 - 1, (pos[0] + 1) * 20 - 1), snake_body_color, -1)

    if path:
        for pos in path:
            if 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]:
                cv2.rectangle(grid_image, (pos[1] * 20, pos[0] * 20),
                              ((pos[1] + 1) * 20 - 1, (pos[0] + 1) * 20 - 1), path_color, -1)

    if snake_pos:
        snake_y, snake_x = snake_pos
        cv2.rectangle(grid_image, (snake_x * 20, snake_y * 20),
                      ((snake_x + 1) * 20 - 1, (snake_y + 1) * 20 - 1), snake_body_color, -1)

    if food_pos:
        food_y, food_x = food_pos
        cv2.rectangle(grid_image, (food_x * 20, food_y * 20),
                      ((food_x + 1) * 20 - 1, (food_y + 1) * 20 - 1), food_color, -1)

    return grid_image


def analyze_game():
    global snake_head_grid, food_grid, previous_food_position, current_path, frame_count, snake_body_positions

    while True:
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        screen = np.array(pyautogui.screenshot(region=bounding_box))
        frame = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        snake_head, snake_direction, food_position, snake_tail, snake_body_positions = process_frame(frame)

        if snake_head and food_position:
            snake_head_grid = (snake_head[1] // (bounding_box[3] // grid_size[0]),
                               snake_head[0] // (bounding_box[2] // grid_size[1]))
            food_grid = (food_position[1] // (bounding_box[3] // grid_size[0]),
                         food_position[0] // (bounding_box[2] // grid_size[1]))

            if previous_food_position != food_position or not current_path:
                grid = np.zeros(grid_size)
                grid[snake_head_grid] = 1

                for body_pos in snake_body_positions:
                    if 0 <= body_pos[0] < grid_size[0] and 0 <= body_pos[1] < grid_size[1]:
                        grid[body_pos[0], body_pos[1]] = 1

                current_path = bfs(snake_head_grid, food_grid, grid)

            previous_food_position = food_position

            debug_grid = create_debug_grid(snake_head_grid, food_grid, snake_body_positions, current_path or [])
            cv2.imshow('Debug Grid', debug_grid)
            cv2.waitKey(1)


def control_snake():
    global current_path, snake_head_grid

    last_key_time = 0
    key_delay = 0.1

    while True:
        if current_path:
            next_move = current_path[1] if len(current_path) > 1 else current_path[0]
            direction = get_direction(snake_head_grid, next_move)
            current_path.pop(0)

            current_time = time.time()
            if current_time - last_key_time > key_delay:
                if direction == 'up':
                    pyautogui.press('up')
                elif direction == 'down':
                    pyautogui.press('down')
                elif direction == 'left':
                    pyautogui.press('left')
                elif direction == 'right':
                    pyautogui.press('right')
                last_key_time = current_time


# Start threads for analysis and control
analyze_thread = threading.Thread(target=analyze_game)
control_thread = threading.Thread(target=control_snake)

analyze_thread.start()
control_thread.start()

# Ensure the OpenCV windows stay open and handle updates
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
