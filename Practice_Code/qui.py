import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# Import our custom classes (Integration)
from Practice_Code.processor import ImageProcessor
from Practice_Code.history import HistoryManager

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 Group 3 - Image Editor")
        self.root.geometry("1200x800")
        
        # --- Initialize Logic ---
        self.processor = ImageProcessor()
        self.history = HistoryManager()
        
        self.tk_image = None # Helper to prevent garbage collection
        
        # --- Build UI ---
        self.setup_menu()
        self.setup_layout()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Save As", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu (Undo/Redo)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo (Ctrl+Z)", command=self.undo_action)
        edit_menu.add_command(label="Redo (Ctrl+Y)", command=self.redo_action)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        self.root.config(menu=menubar)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-z>", lambda event: self.undo_action())
        self.root.bind("<Control-y>", lambda event: self.redo_action())

    def setup_layout(self):
        # 1. Left Sidebar (Controls)
        self.sidebar = tk.Frame(self.root, width=250, bg="#f0f0f0", padx=10, pady=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False) # Fixed width
        
        # Tools Header
        tk.Label(self.sidebar, text="Tools Panel", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(0, 20))
        
        # Section: Geometry
        self.add_section_header("Geometry")
        btn_frame = tk.Frame(self.sidebar, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Rotate 90°", command=lambda: self.apply_transform("rotate", 90)).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Flip Horizontal", command=lambda: self.apply_transform("flip", 1)).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Flip Vertical", command=lambda: self.apply_transform("flip", 0)).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Resize...", command=self.ask_resize).pack(fill=tk.X, pady=2)
        
        # Section: Filters
        self.add_section_header("Filters")
        tk.Button(self.sidebar, text="Grayscale", command=lambda: self.apply_transform("gray")).pack(fill=tk.X, pady=2)
        tk.Button(self.sidebar, text="Edge Detection", command=lambda: self.apply_transform("edge")).pack(fill=tk.X, pady=2)
        
        # Section: Adjustments (Sliders)
        self.add_section_header("Adjustments")
        
        tk.Label(self.sidebar, text="Blur Intensity", bg="#f0f0f0").pack(anchor="w")
        self.blur_slider = tk.Scale(self.sidebar, from_=0, to=20, orient=tk.HORIZONTAL, bg="#f0f0f0")
        self.blur_slider.pack(fill=tk.X)
        tk.Button(self.sidebar, text="Apply Blur", command=self.apply_blur_from_slider).pack(fill=tk.X, pady=2)
        
        tk.Label(self.sidebar, text="Contrast / Brightness", bg="#f0f0f0").pack(anchor="w", pady=(10,0))
        # We use a button for this to prevent lag while dragging
        self.contrast_slider = tk.Scale(self.sidebar, from_=0.5, to=3.0, resolution=0.1, label="Contrast", orient=tk.HORIZONTAL)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X)
        
        self.brightness_slider = tk.Scale(self.sidebar, from_=-100, to=100, label="Brightness", orient=tk.HORIZONTAL)
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill=tk.X)
        
        tk.Button(self.sidebar, text="Apply Adjustments", command=self.apply_brightness_contrast).pack(fill=tk.X, pady=5)

        # 2. Main Canvas (Image Display)
        self.canvas_area = tk.Frame(self.root, bg="#333333")
        self.canvas_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_area, bg="#333333", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 3. Status Bar
        self.status_var = tk.StringVar(value="Welcome! Open an image to start.")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_section_header(self, text):
        lbl = tk.Label(self.sidebar, text=text, font=("Arial", 10, "bold"), fg="#555", bg="#f0f0f0")
        lbl.pack(anchor="w", pady=(15, 5))
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=2)

    # --- LOGIC HANDLERS ---
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp")])
        if path:
            try:
                self.processor.load_image(path)
                self.history.clear() # Clear undo stack for new image
                self.refresh_display()
                self.status_var.set(f"Loaded: {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_image(self):
        if self.processor.image is None: return
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if path:
            self.processor.save_image(path)
            messagebox.showinfo("Success", "Image saved successfully!")

    def refresh_display(self):
        """Updates the canvas and status bar."""
        self.tk_image = self.processor.get_tk_image(
            max_size=(self.canvas_area.winfo_width(), self.canvas_area.winfo_height())
        )
        self.canvas.delete("all")
        # Center the image
        cx = self.canvas.winfo_width() // 2
        cy = self.canvas.winfo_height() // 2
        self.canvas.create_image(cx, cy, anchor=tk.CENTER, image=self.tk_image)
        
        # Update Dimensions in status bar
        dims = self.processor.get_dimensions()
        self.status_var.set(f"Dimensions: {dims} px")

    def apply_transform(self, type, value=None):
        if self.processor.image is None: return
        
        # 1. Save History
        self.history.push_state(self.processor.image)
        
        # 2. Apply Change
        if type == "rotate":
            self.processor.rotate(value)
        elif type == "flip":
            self.processor.flip(value)
        elif type == "gray":
            self.processor.to_grayscale()
        elif type == "edge":
            self.processor.apply_canny_edge()
            
        # 3. Show Result
        self.refresh_display()

    def ask_resize(self):
        if self.processor.image is None: return
        
        # Custom Dialog for Resize
        w = simpledialog.askinteger("Resize", "Enter new Width:", minvalue=50, maxvalue=4000)
        h = simpledialog.askinteger("Resize", "Enter new Height:", minvalue=50, maxvalue=4000)
        
        if w and h:
            self.history.push_state(self.processor.image)
            self.processor.resize_image(w, h)
            self.refresh_display()

    def apply_blur_from_slider(self):
        if self.processor.image is None: return
        val = self.blur_slider.get()
        if val > 0:
            self.history.push_state(self.processor.image)
            self.processor.apply_blur(val)
            self.refresh_display()

    def apply_brightness_contrast(self):
        if self.processor.image is None: return
        alpha = self.contrast_slider.get()
        beta = self.brightness_slider.get()
        
        self.history.push_state(self.processor.image)
        self.processor.adjust_brightness_contrast(alpha, beta)
        self.refresh_display()

    def undo_action(self):
        prev = self.history.undo(self.processor.image)
        if prev is not None:
            self.processor.image = prev
            self.refresh_display()
            self.status_var.set("Undo successful")
        else:
            self.status_var.set("Nothing to Undo")

    def redo_action(self):
        next_img = self.history.redo(self.processor.image)
        if next_img is not None:
            self.processor.image = next_img
            self.refresh_display()
            self.status_var.set("Redo successful")
        else:
            self.status_var.set("Nothing to Redo")