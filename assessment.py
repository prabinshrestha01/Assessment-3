import tkinter as tk
from tkinter import messagebox
import cv2
import os

class HistoryManager:
    def __init__(self, status_label):
        self.undo_stack = []
        self.redo_stack = []
        self.status_label = status_label

    # Save current image state
    def save_state(self, image):
        if image is not None:
            self.undo_stack.append(image.copy())
            self.redo_stack.clear()

    # Undo operation
    def undo(self, current_image):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return current_image

        self.redo_stack.append(current_image.copy())
        return self.undo_stack.pop()

    # Redo operation
    def redo(self, current_image):
        if not self.redo_stack:
            messagebox.showinfo("Redo", "Nothing to redo.")
            return current_image

        self.undo_stack.append(current_image.copy())
        return self.redo_stack.pop()

    # Update status bar
    def update_status(self, image_path, image):
        if image is None:
            self.status_label.config(text="No image loaded")
            return

        height, width = image.shape[:2]
        filename = os.path.basename(image_path) if image_path else "Unsaved Image"
        self.status_label.config(
            text=f"File: {filename} | Size: {width} x {height}"
        )

    # Confirmation popup
    def confirm_exit(self):
        return messagebox.askyesno(
            "Exit Application",
            "Are you sure you want to exit?"
        )
