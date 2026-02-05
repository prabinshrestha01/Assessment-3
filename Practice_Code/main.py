import tkinter as tk
from gui import ImageEditorApp

if __name__ == "__main__":
    # Create the root window
    root = tk.Tk()
    
    # Initialize the application
    app = ImageEditorApp(root)
    
    # Start the event loop
    root.mainloop()