# HIT137 Group Assignment 3 – Desktop Image Editor (Tkinter + OpenCV)

## How to run
1. Install Python 3.10+ (recommended).
2. Install dependencies:
   ```bash
   pip install opencv-python pillow numpy
   ```
3. Run:
   ```bash
   python main.py
   ```

## What this app includes (matches the brief)
- **OOP (3+ classes):**
  - `ImageEditorApp` (GUI + app logic)
  - `ImageProcessor` (OpenCV image processing features)
  - `HistoryManager` (Undo/Redo)

- **GUI elements:**
  - Main window with title and sizing
  - Menu bar: File (Open, Save, Save As, Exit), Edit (Undo, Redo)
  - Image display area (Tkinter Canvas)
  - Control panel with buttons + sliders (blur/brightness/contrast)
  - Status bar (filename, full path, dimensions)

- **Functionality:**
  - File dialogs for opening/saving
  - JPG/PNG/BMP supported
  - Message boxes for errors/confirmations
  - Undo/Redo

## Files
- `main.py` – run this
- `processor.py` – image processing operations
- `history.py` – undo/redo manager
- `github_link.txt` – paste your repository link here before submitting
