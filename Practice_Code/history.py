import copy

class HistoryManager:
    """
    Utility Class: Manages the Undo/Redo stacks.
    Demonstrates: Data Structures (Stacks) and State Management.
    """
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 15 # Limit memory usage

    def push_state(self, image):
        """Saves a copy of the current image state."""
        if image is not None:
            # Deep copy is essential here to store the actual data, not a reference
            self.undo_stack.append(image.copy())
            self.redo_stack.clear() # New action clears the redo path
            
            # Keep memory usage in check
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)

    def undo(self, current_image):
        """Returns the previous state."""
        if not self.undo_stack:
            return None
        
        # Save current state to redo stack before undoing
        self.redo_stack.append(current_image.copy())
        return self.undo_stack.pop()

    def redo(self, current_image):
        """Returns the forward state."""
        if not self.redo_stack:
            return None
            
        # Save current state to undo stack before redoing
        self.undo_stack.append(current_image.copy())
        return self.redo_stack.pop()
        
    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()