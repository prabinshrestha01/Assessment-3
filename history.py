
"""
History Management Module

This module provides three core classes for the image processing application:
1. History - Manages undo/redo operations with stack-based history
2. StatusBar - Displays real-time application status and image information
3. MessageBoxManager - Centralizes all user dialog interactions

All classes follow OOP principles with proper encapsulation and clear interfaces.

Author: HIT137 Group Assignment 3
Date: January 2026
"""

from collections import deque
from typing import Tuple, Any, Optional, Dict
import tkinter.messagebox as messagebox


# ============================================================================
# CLASS 1: HISTORY
# ============================================================================

class History:
    """
    Manages undo and redo operations for image processing.
    
    This class implements a stack-based history system that stores snapshots
    of image states before and after operations. It supports unlimited undo/redo
    with a configurable maximum history size to prevent excessive memory usage.
    
    Attributes:
        max_history_size (int): Maximum number of operations to store in history
        undo_stack (deque): Stack of completed operations that can be undone
        redo_stack (deque): Stack of undone operations that can be redone
    
    Example:
        >>> history = History(max_history_size=20)
        >>> history.add_operation("Grayscale", image_array)
        >>> history.can_undo()
        True
        >>> operation_name, image_state, metadata = history.undo()
    """
    
    def __init__(self, max_history_size: int = 20):
        """
        Initialize the History manager with empty stacks.
        
        Args:
            max_history_size (int): Maximum number of operations to store.
                                   Default is 20 to balance memory and usability.
        
        Raises:
            ValueError: If max_history_size is less than 1
        """
        if max_history_size < 1:
            raise ValueError("max_history_size must be at least 1")
        
        self.max_history_size: int = max_history_size
        self.undo_stack: deque = deque(maxlen=max_history_size)
        self.redo_stack: deque = deque(maxlen=max_history_size)
    
    def add_operation(self, operation_name: str, image_state: Any, 
                     metadata: Optional[Dict] = None) -> None:
        """
        Record an operation in the undo stack.
        
        When a new operation is added, the redo stack is automatically cleared
        since the operation history branches at this point.
        
        Args:
            operation_name (str): Name/description of the operation
                                 (e.g., "Grayscale", "Blur", "Rotate 90°")
            image_state (Any): The image state (typically numpy array from OpenCV)
            metadata (Dict, optional): Additional operation parameters
                                      (e.g., {"blur_intensity": 5})
        """
        # Create operation record with all relevant information
        operation: Dict[str, Any] = {
            'name': operation_name,
            'image_state': image_state,
            'metadata': metadata or {}
        }
        
        # Add to undo stack (deque will auto-remove oldest if at max_length)
        self.undo_stack.append(operation)
        
        # Clear redo stack as history has branched
        self.redo_stack.clear()
    
    def undo(self) -> Tuple[Optional[str], Optional[Any], Dict]:
        """
        Revert to the previous operation state.
        
        Moves the last operation from undo stack to redo stack,
        allowing the user to redo if desired.
        
        Returns:
            Tuple containing:
            - operation_name (str): Name of the undone operation
            - image_state (Any): The previous image state
            - metadata (dict): Operation metadata
            
            Returns (None, None, {}) if undo stack is empty.
        
        Example:
            >>> if history.can_undo():
            ...     op_name, img, meta = history.undo()
        """
        if self.can_undo():
            operation = self.undo_stack.pop()
            self.redo_stack.append(operation)
            return operation['name'], operation['image_state'], operation['metadata']
        
        # Return empty state if nothing to undo
        return None, None, {}
    
    def redo(self) -> Tuple[Optional[str], Optional[Any], Dict]:
        """
        Re-apply the last undone operation.
        
        Moves an operation from redo stack back to undo stack,
        effectively re-applying a previously undone action.
        
        Returns:
            Tuple containing:
            - operation_name (str): Name of the redone operation
            - image_state (Any): The image state with operation applied
            - metadata (dict): Operation metadata
            
            Returns (None, None, {}) if redo stack is empty.
        
        Example:
            >>> if history.can_redo():
            ...     op_name, img, meta = history.redo()
        """
        if self.can_redo():
            operation = self.redo_stack.pop()
            self.undo_stack.append(operation)
            return operation['name'], operation['image_state'], operation['metadata']
        
        # Return empty state if nothing to redo
        return None, None, {}
    
    def can_undo(self) -> bool:
        """
        Check if undo operation is available.
        
        Returns:
            bool: True if there are operations to undo, False otherwise
        """
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """
        Check if redo operation is available.
        
        Returns:
            bool: True if there are operations to redo, False otherwise
        """
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        """
        Clear all undo and redo history.
        
        Useful when opening a new image or resetting the application state.
        """
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_stack_size(self) -> int:
        """Get current number of operations in undo stack."""
        return len(self.undo_stack)
    
    def get_redo_stack_size(self) -> int:
        """Get current number of operations in redo stack."""
        return len(self.redo_stack)


# ============================================================================
# CLASS 2: STATUS BAR
# ============================================================================

class StatusBar:
    """
    Manages status bar display with real-time image and application information.
    
    Updates a Tkinter Label widget with current image file path, dimensions,
    and application status. Provides a clean interface for updating status information.
    
    Attributes:
        status_label: Tkinter Label widget for displaying status text
        current_image_path (str): Path/name of currently loaded image
        current_dimensions (tuple): Image width and height in pixels
        current_operation (str): Current application status/operation
    
    Example:
        >>> status_bar = StatusBar(label_widget)
        >>> status_bar.update_image_info("photo.jpg", 800, 600)
        >>> status_bar.update_operation("Applying Blur...")
        >>> status_bar.set_ready()
    """
    
    def __init__(self, status_label):
        """
        Initialize StatusBar with a Tkinter Label widget.
        
        Args:
            status_label: Tkinter Label widget to display status messages
        """
        self.status_label = status_label
        self.current_image_path: str = "No image loaded"
        self.current_dimensions: Tuple[int, int] = (0, 0)
        self.current_operation: str = "Ready"
        
        # Display initial status
        self._refresh_display()
    
    def update_image_info(self, filename: str, width: int, height: int) -> None:
        """
        Update status bar with image file and dimension information.
        
        Typically called when an image is opened or resized.
        
        Args:
            filename (str): Image file path or name
            width (int): Image width in pixels
            height (int): Image height in pixels
        """
        self.current_image_path = filename
        self.current_dimensions = (width, height)
        self._refresh_display()
    
    def update_operation(self, operation_name: str) -> None:
        """
        Update status bar with current operation being performed.
        
        Use this to show real-time feedback to the user (e.g., "Applying Blur...").
        
        Args:
            operation_name (str): Description of current operation
        """
        self.current_operation = operation_name
        self._refresh_display()
    
    def set_ready(self) -> None:
        """
        Set status to 'Ready' state.
        
        Call this when an operation completes or is cancelled.
        """
        self.current_operation = "Ready"
        self._refresh_display()
    
    def _refresh_display(self) -> None:
        """
        Internal method to refresh the status bar display.
        
        Combines all status information into a single formatted string
        and updates the label widget.
        """
        status_text = (
            f"File: {self.current_image_path} | "
            f"Dimensions: {self.current_dimensions[0]}x{self.current_dimensions[1]} | "
            f"Status: {self.current_operation}"
        )
        self.status_label.config(text=status_text)
    
    def reset(self) -> None:
        """
        Reset status bar to default 'No image loaded' state.
        
        Call this when closing an image or clearing the application.
        """
        self.current_image_path = "No image loaded"
        self.current_dimensions = (0, 0)
        self.current_operation = "Ready"
        self._refresh_display()


# ============================================================================
# CLASS 3: MESSAGE BOX MANAGER
# ============================================================================

class MessageBoxManager:
    """
    Centralizes all message box dialogs for consistent user feedback.
    
    Provides a unified interface for all user dialogs including info, warnings,
    errors, and confirmation prompts. Using this class ensures consistent
    dialog behavior and styling throughout the application.
    
    All methods are static for convenient access without instantiation.
    
    Example:
        >>> if MessageBoxManager.ask_yes_no("Save?", "Save changes?"):
        ...     save_file()
        >>> MessageBoxManager.show_error("Error", "Failed to load image")
    """
    
    @staticmethod
    def show_info(title: str, message: str) -> None:
        """
        Display an information message box.
        
        Args:
            title (str): Dialog window title
            message (str): Message to display
        """
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str) -> None:
        """
        Display a warning message box.
        
        Args:
            title (str): Dialog window title
            message (str): Warning message to display
        """
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_error(title: str, message: str) -> None:
        """
        Display an error message box.
        
        Args:
            title (str): Dialog window title
            message (str): Error message to display
        """
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """
        Display a Yes/No confirmation dialog.
        
        Args:
            title (str): Dialog window title
            message (str): Question/message to display
        
        Returns:
            bool: True if user clicks Yes, False if user clicks No
        """
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def ask_ok_cancel(title: str, message: str) -> bool:
        """
        Display an OK/Cancel confirmation dialog.
        
        Args:
            title (str): Dialog window title
            message (str): Message to display
        
        Returns:
            bool: True if user clicks OK, False if user clicks Cancel
        """
        return messagebox.askokcancel(title, message)
    
    @staticmethod
    def ask_retry_cancel(title: str, message: str) -> bool:
        """
        Display a Retry/Cancel confirmation dialog.
        
        Args:
            title (str): Dialog window title
            message (str): Message to display
        
        Returns:
            bool: True if user clicks Retry, False if user clicks Cancel
        """
        return messagebox.askretrycancel(title, message)
    
    # ========================================================================
    # CONVENIENCE METHODS FOR COMMON DIALOGS
    # ========================================================================
    
    @staticmethod
    def show_file_error(filename: str) -> None:
        """
        Show error dialog for file operation failure.
        
        Args:
            filename (str): Name of the file that failed to load
        """
        MessageBoxManager.show_error(
            "File Error",
            f"Could not process file: {filename}\n\n"
            f"Make sure the file exists and is a valid image format "
            f"(JPG, PNG, BMP)."
        )
    
    @staticmethod
    def show_save_success(filename: str) -> None:
        """
        Show success message after saving a file.
        
        Args:
            filename (str): Path where file was saved
        """
        MessageBoxManager.show_info(
            "Save Successful",
            f"Image saved successfully to:\n{filename}"
        )
    
    @staticmethod
    def confirm_overwrite(filename: str) -> bool:
        """
        Ask user to confirm overwriting an existing file.
        
        Args:
            filename (str): Name of existing file
        
        Returns:
            bool: True to overwrite, False to cancel
        """
        return MessageBoxManager.ask_yes_no(
            "File Exists",
            f"The file '{filename}' already exists.\n"
            f"Do you want to overwrite it?"
        )
    
    @staticmethod
    def confirm_unsaved_changes() -> bool:
        """
        Ask user to confirm discarding unsaved changes.
        
        Returns:
            bool: True to discard changes, False to keep editing
        """
        return MessageBoxManager.ask_yes_no(
            "Unsaved Changes",
            "You have unsaved changes.\n"
            "Do you want to discard them?"
        )
    
    @staticmethod
    def show_unsupported_format(filename: str) -> None:
        """
        Show error for unsupported image format.
        
        Args:
            filename (str): Name of the unsupported file
        """
        MessageBoxManager.show_error(
            "Unsupported Format",
            f"File '{filename}' format is not supported.\n\n"
            f"Supported formats: JPG, PNG, BMP"
        )
    
    @staticmethod
    def confirm_exit() -> bool:
        """
        Ask user to confirm exiting the application.
        
        Returns:
            bool: True to exit, False to cancel
        """
        return MessageBoxManager.ask_yes_no(
            "Exit Application",
            "Are you sure you want to exit?"
        )
