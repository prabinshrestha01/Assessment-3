import tkinter as tk
from tkinter import filedialog, messagebox

# Placeholder imports for helper classes
# from processor import ImageProcessor
# from history import HistoryManager

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 - Image Editor Group 3")
        self.root.geometry("1100x700")

        # Placeholder for helper classes
        self.processor = None 
        self.history = None

        print("App started...")

# This block allows us to run this file directly for testing
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()