# SnakeSolver - Automated Snake Game Solver

This repository contains a Python program designed to automatically play and solve the classic Snake game using computer vision and pathfinding algorithms. The program captures the game screen, detects the snake's head, body, and food, and then calculates the optimal path for the snake to follow.

## Features

- **Real-Time Game Capture:** The program captures the game area from the screen in real-time.
- **Object Detection:** Detects the snake's head, body, tail, and food using template matching with OpenCV.
- **Pathfinding Algorithm:** Utilizes Breadth-First Search (BFS) to find the optimal path from the snake's head to the food.
- **Automated Controls:** Sends keyboard inputs to control the snake based on the calculated path.
- **Debug Grid:** Displays a visual representation of the game grid, showing the snake's position, the path, and the food.
- **OCR Detection:** Detects the "Tente novamente" text using Tesseract OCR, indicating a failed game state.

## How It Works

### 1. Game Capture

The program captures a specific region of the screen where the game is being played. This region is defined by a bounding box:

```python
bounding_box = (2037, 344, 465, 494)
```

### 2. Object Detection

- **Snake Detection:** The program uses template matching to detect the snake's head, body, and tail. Different templates are provided for detecting the head in different orientations (up, down, left, right).
- **Food Detection:** The program uses multiple food templates to detect the position of the food on the grid.

### 3. Pathfinding

- **BFS Algorithm:** The program uses a Breadth-First Search (BFS) algorithm to calculate the shortest path from the snake's head to the food while avoiding obstacles such as the snake's body.
- **Grid Representation:** The game area is divided into a grid where each cell represents a possible position for the snake. The BFS algorithm traverses this grid to find the optimal path.

### 4. Snake Control

The program translates the calculated path into keyboard inputs (`up`, `down`, `left`, `right`) that control the snake's movement. The controls are sent to the game with minimal delay to account for any input lag.

### 5. Debugging Tools

- **Debug Grid:** The program generates a visual representation of the grid showing the snake's current position, the planned path, and the location of the food.
- **Text Detection:** The program checks for the "Tente novamente" message using Tesseract OCR to detect if the game has ended.

## Installation

### Prerequisites

- Python 3.12+
- Tesseract OCR
- Required Python packages (install via `requirements.txt`):
  ```bash
  pip install -r requirements.txt
  ```

### Required Python Packages

- `opencv-python`
- `numpy`
- `pyautogui`
- `pytesseract`

### Installation Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/SnakeSolver.git
   cd SnakeSolver
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Tesseract:**
   Ensure that Tesseract OCR is installed and accessible via your system's PATH. Update the Tesseract path in the script if necessary:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. **Run the Program:**
   ```bash
   python main.py
   ```

## Usage

Simply run the `main.py` script, and the program will automatically start capturing the game screen, detecting objects, calculating the optimal path, and controlling the snake in real-time.

```bash
python main.py
```

For running a helping tool to define the bounding box where the game is being played, run the `bounding_box_tool.py` script:

```bash
python bounding_box_tool.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you find any bugs or have suggestions for improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```