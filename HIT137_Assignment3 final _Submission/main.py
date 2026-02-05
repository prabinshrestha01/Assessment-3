"""
main.py
Desktop Image Editor (Tkinter + OpenCV)
This is the main application file for the desktop image editor. It provides a GUI for users to open, edit, and save images using various filters and transformations. The application is built with Tkinter for the interface and OpenCV for image processing. We have also demostated object oriented programming like encapsulation, class interaction and so on.

features:
- open save and save as in jpg, png and bmp formats.
- image preview
-Gaussian blur, bightness and contrast adjustment with slider
-edge detection with canny
-image rotation (90, 180, and 270 degrees)
-image resizing
- horizontal and vertical flipping
- undo and redo functionality
- keyboard shortcuts

How to run:
    python main.py

Dependencies:
   these are the things you need to install torun this code. use pip to install them
    pip install opencv-python 
    pip install pillow
    pip install numpy
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import cv2
import numpy as np
from PIL import Image, ImageTk

from Practice_Code.processor import ImageProcessor, ImageInfo
from Practice_Code.history import HistoryManager

# Define supported image file formats
SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".bmp")


def _read_image_any_path(path: str) -> Optional[np.ndarray]:
    """
    Robust image loading (handles unicode paths on Windows by reading bytes then decoding).
    Returns BGR numpy array or None.
    """
    try:
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def _write_image_any_path(path: str, img_bgr: np.ndarray) -> bool:
    """Robust image saving for unicode paths on Windows."""
    try:
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if ext == "jpg":
            ext = "jpeg"
        ok, buf = cv2.imencode("." + ext, img_bgr)
        if not ok:
            return False
        buf.tofile(path)
        return True
    except Exception:
        return False


class ImageEditorApp:
    """
    main GUI for image editor application.

    The main purpose of this class is:
    - creating and managing tkinter gui components
    - handeling the interactions of the users
    - the dispaly of image
    - connecting the image processing and history management to the GUI actions
    - proprer implementation of redo and undo funcationality
    Main GUI class.
    Demonstrates OOP requirements:
      - Encapsulation: internal state (current image, path, history)
      - Constructor: __init__ builds the full UI
      - Methods: open/save/apply filters, etc.
      - Class Interaction: uses ImageProcessor + HistoryManager
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Set us main application window and al ui components. Initialize state.

        type root: tk.Tk
        purpose
        - window size and title is set up
        - image processor and history manager are initialized
        - menu, layout, controls are built
        - keyboard shortcuts are built
        - display default messages.
        
        """
        self.root = root
        self.root.title("HIT137 Assignment 3 - Image Editor")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        # Core state: image data and undo/redo system
        self.processor = ImageProcessor()
        self.history = HistoryManager(max_states=30)
        self.current_img_bgr: Optional[np.ndarray] = None
        self.current_path: Optional[str] = None
        self._tk_img: Optional[ImageTk.PhotoImage] = None  # keep reference to prevent garbage collection

        # UI
        self._build_menu()
        self._build_layout()
        self._build_controls()
        self._set_status("Ready. Open an image to begin.")

        # Set up keyboard shortcuts for common operations
        self.root.bind_all("<Control-o>", lambda e: self.open_image())
        self.root.bind_all("<Control-s>", lambda e: self.save_image())
        self.root.bind_all("<Control-Shift-S>", lambda e: self.save_as_image())
        self.root.bind_all("<Control-z>", lambda e: self.undo())
        self.root.bind_all("<Control-y>", lambda e: self.redo())

    # ---------- UI construction ----------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_image, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

    def _build_layout(self) -> None:
        self.main = ttk.Frame(self.root, padding=8)
        self.main.pack(fill=tk.BOTH, expand=True)

        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=0)
        self.main.rowconfigure(0, weight=1)

        # Image display area
        self.display_frame = ttk.LabelFrame(self.main, text="Image Preview")
        self.display_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.display_frame.columnconfigure(0, weight=1)
        self.display_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.display_frame, bg="#1f1f1f", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Controls area
        self.controls = ttk.LabelFrame(self.main, text="Controls")
        self.controls.grid(row=0, column=1, sticky="ns")
        self.controls.columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="")
        self.status = ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(8, 4))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_controls(self) -> None:
        pad = {"padx": 8, "pady": 6, "sticky": "ew"}

        # Basic actions
        ttk.Button(self.controls, text="Grayscale", command=self.apply_grayscale).grid(row=0, column=0, **pad)
        ttk.Button(self.controls, text="Edge Detect (Canny)", command=self.apply_edges).grid(row=1, column=0, **pad)

        # Rotation
        rot_frame = ttk.LabelFrame(self.controls, text="Rotate")
        rot_frame.grid(row=2, column=0, **pad)
        rot_frame.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(rot_frame, text="90°", command=lambda: self.apply_rotate(90)).grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        ttk.Button(rot_frame, text="180°", command=lambda: self.apply_rotate(180)).grid(row=0, column=1, padx=4, pady=6, sticky="ew")
        ttk.Button(rot_frame, text="270°", command=lambda: self.apply_rotate(270)).grid(row=0, column=2, padx=4, pady=6, sticky="ew")

        # Flip
        flip_frame = ttk.LabelFrame(self.controls, text="Flip")
        flip_frame.grid(row=3, column=0, **pad)
        flip_frame.columnconfigure((0, 1), weight=1)
        ttk.Button(flip_frame, text="Horizontal", command=lambda: self.apply_flip("horizontal")).grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        ttk.Button(flip_frame, text="Vertical", command=lambda: self.apply_flip("vertical")).grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        # Resize
        ttk.Button(self.controls, text="Resize / Scale…", command=self.apply_resize).grid(row=4, column=0, **pad)

        # Sliders (required: at least one slider)
        slider_frame = ttk.LabelFrame(self.controls, text="Adjustments (Sliders)")
        slider_frame.grid(row=5, column=0, **pad)
        slider_frame.columnconfigure(0, weight=1)

        # Blur slider
        ttk.Label(slider_frame, text="Blur intensity").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 0))
        self.blur_var = tk.IntVar(value=0)
        blur = ttk.Scale(slider_frame, from_=0, to=50, variable=self.blur_var, command=lambda v: self._preview_blur())
        blur.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(slider_frame, text="Apply Blur", command=self.apply_blur).grid(row=2, column=0, padx=8, pady=(0, 8), sticky="ew")

        # Brightness slider
        ttk.Label(slider_frame, text="Brightness (-100..100)").grid(row=3, column=0, sticky="w", padx=8)
        self.brightness_var = tk.IntVar(value=0)
        bright = ttk.Scale(slider_frame, from_=-100, to=100, variable=self.brightness_var,
                           command=lambda v: self._preview_brightness_contrast())
        bright.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 8))
        # Contrast slider
        ttk.Label(slider_frame, text="Contrast (0.5..3.0)").grid(row=5, column=0, sticky="w", padx=8)
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast = ttk.Scale(slider_frame, from_=0.5, to=3.0, variable=self.contrast_var,
                             command=lambda v: self._preview_brightness_contrast())
        contrast.grid(row=6, column=0, sticky="ew", padx=8, pady=(0, 8))

        btns = ttk.Frame(slider_frame)
        btns.grid(row=7, column=0, padx=8, pady=(0, 8), sticky="ew")
        btns.columnconfigure((0, 1), weight=1)
        ttk.Button(btns, text="Apply Bright/Contrast", command=self.apply_brightness_contrast).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ttk.Button(btns, text="Reset Sliders", command=self.reset_sliders).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Undo/Redo buttons (in addition to menu)
        ur = ttk.Frame(self.controls)
        ur.grid(row=6, column=0, **pad)
        ur.columnconfigure((0, 1), weight=1)
        ttk.Button(ur, text="Undo", command=self.undo).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ttk.Button(ur, text="Redo", command=self.redo).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Help
        ttk.Button(self.controls, text="About / Help", command=self.show_help).grid(row=7, column=0, **pad)

    # ---------- Status ----------
    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _update_status_from_image(self) -> None:
        if self.current_img_bgr is None:
            self._set_status("No image loaded.")
            return

        h, w = self.current_img_bgr.shape[:2]
        path_text = self.current_path if self.current_path else "(unsaved)"
        self._set_status(f"Image: {os.path.basename(path_text)} | Path: {path_text} | Size: {w}x{h}px")

    # ---------- Display ----------
    def _render_on_canvas(self, img_bgr: np.ndarray) -> None:
        """Render BGR image onto canvas, fitting within the available space."""
        if img_bgr is None:
            self.canvas.delete("all")
            return

        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())

        # Convert BGR -> RGB -> PIL
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(img_rgb)

        # Fit to canvas while keeping aspect ratio
        iw, ih = pil.size
        scale = min(canvas_w / iw, canvas_h / ih)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))
        pil_resized = pil.resize((new_w, new_h), Image.LANCZOS)

        self._tk_img = ImageTk.PhotoImage(pil_resized)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w // 2, canvas_h // 2, image=self._tk_img, anchor="center")

    def _refresh_display(self) -> None:
        if self.current_img_bgr is None:
            self.canvas.delete("all")
            self._set_status("No image loaded.")
            return
        self._render_on_canvas(self.current_img_bgr)
        self._update_status_from_image()

    # ---------- File actions ----------
    def open_image(self) -> None:
        """
        open an image file and load it into the editor. Supported formats: JPG, PNG, BMP.

        steps:
        Open file dialog to select an image
        makes sure the selected file is of supported format
        checks image using opencv
        store the image in the memory     
        shows the image in the canvas
        update the status bar with image info (filename, path, dimensions) 
        """
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if not path:
            return

        if not path.lower().endswith(SUPPORTED_EXTS):
            messagebox.showerror("Unsupported format", "Please open a JPG, PNG, or BMP image.")
            return

        img = _read_image_any_path(path)
        if img is None:
            messagebox.showerror("Open failed", "Could not open the selected image.")
            return

        self.current_img_bgr = img
        self.current_path = path
        self.history.clear()
        self.reset_sliders(silent=True)
        self._refresh_display()

    def save_image(self) -> None:
        """
        saves the current image to disk. If the image was opened from a file, it saves back to that file. If it's a new image or if saving fails, it prompts "Save As" dialog.
        display appropriate messages for success or failure. Supported formats: JPG, PNG, BMP.
        """
        if self.current_img_bgr is None:
            messagebox.showwarning("Nothing to save", "Please open an image first.")
            return

        if not self.current_path:
            self.save_as_image()
            return

        ok = _write_image_any_path(self.current_path, self.current_img_bgr)
        if not ok:
            messagebox.showerror("Save failed", "Could not save the image. Try 'Save As' to a different location.")
            return
        messagebox.showinfo("Saved", "Image saved successfully.")
        self._update_status_from_image()

    def save_as_image(self) -> None:
        """
        if there is an image loaded, open a "Save As" dialog to save the current image to a new file. Supported formats: JPG, PNG, BMP. Update the status bar with the new path and filename after saving.
        """
        if self.current_img_bgr is None:
            messagebox.showwarning("Nothing to save", "Please open an image first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg *.jpeg"), ("BMP", "*.bmp")]
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_EXTS:
            messagebox.showerror("Unsupported format", "Please save as JPG, PNG, or BMP.")
            return

        ok = _write_image_any_path(path, self.current_img_bgr)
        if not ok:
            messagebox.showerror("Save failed", "Could not save the image to the selected location.")
            return

        self.current_path = path
        messagebox.showinfo("Saved", "Image saved successfully.")
        self._update_status_from_image()

    def _on_exit(self) -> None:
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    # ---------- Undo/Redo ----------
    def undo(self) -> None:
        if self.current_img_bgr is None:
            return
        prev = self.history.undo(self.current_img_bgr)
        if prev is None:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        self.current_img_bgr = prev
        self._refresh_display()

    def redo(self) -> None:
        if self.current_img_bgr is None:
            return
        nxt = self.history.redo(self.current_img_bgr)
        if nxt is None:
            messagebox.showinfo("Redo", "Nothing to redo.")
            return
        self.current_img_bgr = nxt
        self._refresh_display()

    # ---------- Apply operations (each pushes to history first) ----------
    def _require_image(self) -> bool:
        if self.current_img_bgr is None:
            messagebox.showwarning("No image", "Please open an image first.")
            return False
        return True

    def apply_grayscale(self) -> None:
        """
        convert the current image into grayscale.
        function:
        - Checks if an image is loaded, if not, shows a warning.
        - save the current image to history which might be used for undo later
        - applies grayscale filter using the image processor
        - refreshes the image

        """
        if not self._require_image():
            return
        self.history.push(self.current_img_bgr)
        self.current_img_bgr = self.processor.to_gray(self.current_img_bgr)
        self._refresh_display()

    def apply_blur(self) -> None:
        """
        - applies a Gaussian blur to the current image.
        - blur intensity is determined by the value of the blur slider (0-50).
        - save the current image to history before applying the blur for undo functionality.
        """
        if not self._require_image():
            return
        intensity = int(self.blur_var.get())
        self.history.push(self.current_img_bgr)
        self.current_img_bgr = self.processor.blur_gaussian(self.current_img_bgr, intensity)
        self._refresh_display()

    def apply_edges(self) -> None:
        """
        applies Canny edge detection to the current image. Prompts the user to input two threshold values for the Canny algorithm. Saves the current image to history before applying the edge detection for undo functionality.
        """
        if not self._require_image():
            return
        t1 = simpledialog.askinteger("Canny Edge Detection", "Threshold 1 (e.g., 50):", minvalue=0, maxvalue=500)
        if t1 is None:
            return
        t2 = simpledialog.askinteger("Canny Edge Detection", "Threshold 2 (e.g., 150):", minvalue=1, maxvalue=500)
        if t2 is None:
            return
        self.history.push(self.current_img_bgr)
        self.current_img_bgr = self.processor.edge_canny(self.current_img_bgr, t1, t2)
        self._refresh_display()

    def apply_brightness_contrast(self) -> None:
        """
        -Adjusts the brightness and contrast of the current image based on the values of the respective sliders. 
        -The brightness slider ranges from -100 to 100, while the contrast slider ranges from 0.5 to 3.0.
        -Before applying the adjustments, it saves the current image to history for undo functionality.
        """
        if not self._require_image():
            return
        beta = int(self.brightness_var.get())
        alpha = float(self.contrast_var.get())
        self.history.push(self.current_img_bgr)
        img = self.processor.adjust_brightness(self.current_img_bgr, beta)
        img = self.processor.adjust_contrast(img, alpha)
        self.current_img_bgr = img
        self._refresh_display()

    def apply_rotate(self, degrees: int) -> None:
        """
        this function rotates the current image by a specified number of degrees (90, 180, or 270). 
        -It first checks if an image is loaded, and if so, it saves the current image to history for undo functionality. 
        -It applies the rotation using the image processor and refreshes the display to show the updated image.
        """
        if not self._require_image():
            return
        self.history.push(self.current_img_bgr)
        self.current_img_bgr = self.processor.rotate(self.current_img_bgr, degrees)
        self._refresh_display()

    def apply_flip(self, mode: str) -> None:
        """
        this function flips the current image either horizontally or vertically based on the specified mode ("horizontal" or "vertical").
        -It checks if an image is loaded, and if so, it saves the current image.
        -It applies the flip using the image processor and refreshes the display to show the updated image.
        """
        if not self._require_image():
            return
        self.history.push(self.current_img_bgr)
        self.current_img_bgr = self.processor.flip(self.current_img_bgr, mode)
        self._refresh_display()

    def apply_resize(self) -> None:
        if not self._require_image():
            return
        h, w = self.current_img_bgr.shape[:2]
        new_w = simpledialog.askinteger("Resize", f"New width (current {w}):", minvalue=1, maxvalue=10000)
        if new_w is None:
            return
        new_h = simpledialog.askinteger("Resize", f"New height (current {h}):", minvalue=1, maxvalue=10000)
        if new_h is None:
            return
        self.history.push(self.current_img_bgr)
        self.current_img_bgr = self.processor.resize(self.current_img_bgr, new_w, new_h)
        self._refresh_display()

    # ---------- Live preview helpers (do NOT push to history) ----------
    def _preview_blur(self) -> None:
        if self.current_img_bgr is None:
            return
        # Preview by applying blur on top of a temporary base.
        # For simplicity and stability, we preview from the current image without changing state.
        intensity = int(self.blur_var.get())
        preview = self.processor.blur_gaussian(self.current_img_bgr, intensity)
        self._render_on_canvas(preview)
        self._update_status_from_image()

    def _preview_brightness_contrast(self) -> None:
        if self.current_img_bgr is None:
            return
        beta = int(self.brightness_var.get())
        alpha = float(self.contrast_var.get())
        preview = self.processor.adjust_brightness(self.current_img_bgr, beta)
        preview = self.processor.adjust_contrast(preview, alpha)
        self._render_on_canvas(preview)
        self._update_status_from_image()

    def reset_sliders(self, silent: bool = False) -> None:
        self.blur_var.set(0)
        self.brightness_var.set(0)
        self.contrast_var.set(1.0)
        if not silent:
            self._refresh_display()

    # ---------- Help ----------
    def show_help(self) -> None:
        msg = (
            "HIT137 Assignment 3 - Image Editor\n\n"
            "Features implemented:\n"
            "• Open/Save/Save As (JPG, PNG, BMP)\n"
            "• Undo/Redo\n"
            "• Grayscale, Gaussian Blur (slider), Edge Detection (Canny)\n"
            "• Brightness & Contrast (sliders)\n"
            "• Rotate 90/180/270, Flip Horizontal/Vertical\n"
            "• Resize/Scale\n"
            "• Status bar shows filename, path, and dimensions\n\n"
            "Shortcuts:\n"
            "Ctrl+O Open, Ctrl+S Save, Ctrl+Shift+S Save As\n"
            "Ctrl+Z Undo, Ctrl+Y Redo"
        )
        messagebox.showinfo("About / Help", msg)


def main() -> None:
    root = tk.Tk()
    app = ImageEditorApp(root)

    # Make sure canvas refreshes correctly after resizing window
    def on_resize(event):
        app._refresh_display()

    root.bind("<Configure>", on_resize)
    root.mainloop()


if __name__ == "__main__":
    main()
