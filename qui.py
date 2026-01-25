# gui.py
# Commit Message: UI: Added control frame and canvas layout
# This file builds the window: toolbar (holds controls), canvas (shows image), status bar (shows messages).

import tkinter as tk

class ImageEditorApp:
    def __init__(self, root):
        # Create the main window and set its size and minimum size.
        self.root = root
        self.root.title("HIT137 - Image Editor Group 3")
        self.root.geometry("1100x700")   # This sets the starting window size.
        self.root.minsize(800, 600)     # This prevents the window from getting too small.

        # Build the UI layout (toolbar, canvas, status bar).
        self.setup_layout()

    def setup_layout(self):
        # This creates the top control bar where buttons and sliders will live.
        self.control_frame = tk.Frame(
            self.root,
            height=100,          # This suggests how tall the toolbar should be.
            bg="#d9d9d9",        # This gives the toolbar a light grey background.
            bd=2,                # This adds a small border around the toolbar.
            relief=tk.RAISED     # This makes the toolbar look raised like a real toolbar.
        )
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        self.control_frame.pack_propagate(False)  # This keeps the toolbar at the height we set.

        # This placeholder shows where you'll add buttons and sliders.
        tk.Label(self.control_frame, text="[Buttons and Sliders will go here]", bg="#d9d9d9").pack(pady=10)

        # This creates the main container for the canvas (image area).
        self.canvas_frame = tk.Frame(self.root, bg="#404040")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # This creates the canvas where images will be drawn or displayed.
        self.canvas = tk.Canvas(self.canvas_frame, bg="#404040", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # This gives the canvas breathing room.

        # This creates a slim status bar at the bottom for short messages.
        self.status_frame = tk.Frame(self.root, height=22, bg="#e9e9e9", bd=1, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_frame.pack_propagate(False)  # This keeps the status bar height fixed.

        # This label displays status text like "Ready" or "Image loaded".
        self.status_label = tk.Label(self.status_frame, text="Ready", anchor="w", bg="#e9e9e9")
        self.status_label.pack(fill=tk.BOTH, padx=8)

        # This is a quick note for later: split the control_frame into subframes when adding many controls.
        # This is a quick note for later: bind <Configure> on canvas_frame if you need to react to resizing.

if __name__ == "__main__":
    # This launches the application window.
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
