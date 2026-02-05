"""
this module defines the HistoryManager class, which is responsible for managing the undo and redo functionality for image editing operations. It maintains two stacks: one for undo states and one for redo states. Each state is a copy of the image at a given point in time, allowing users to revert to previous versions of the image or reapply changes they have undone. The class provides methods to push new states onto the undo stack, clear the history, and perform undo and redo operations while ensuring that the current image state is properly managed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


@dataclass
class HistoryManager:
    """
    Manages undo/redo stacks for images (numpy arrays).
    Stores copies so later modifications don't affect previous states.
    """
    max_states: int = 20
    _undo_stack: List[np.ndarray] = field(default_factory=list)
    _redo_stack: List[np.ndarray] = field(default_factory=list)

    def clear(self) -> None:
        """
        Clear all history states. This should be called when a new image is loaded or when the current image is reset to ensure that the undo/redo stacks are cleared and do not contain states from a previous image.
        """
        self._undo_stack.clear()
        self._redo_stack.clear()

    def push(self, img: np.ndarray) -> None:
        """Save current state before applying a change."""
        if img is None:
            return
        self._undo_stack.append(img.copy())
        if len(self._undo_stack) > self.max_states:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        """
        Check if there are states available to undo. This method returns True if there is at least one state in the undo stack, indicating that the user can perform an undo operation. If the undo stack is empty, it returns False, meaning there are no previous states to revert to."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """
        Check if there are states available to redo. This method returns True if there is at least one state in the redo stack, indicating that the user can perform a redo operation. If the redo stack is empty, it returns False, meaning there are no states to reapply after an undo operation.
        """
        return len(self._redo_stack) > 0

    def undo(self, current: np.ndarray) -> Optional[np.ndarray]:
        """
        Perform an undo operation. This method checks if there are states available to undo and if the current image is not None. If both conditions are met, it pushes the current state onto the redo stack and pops the last state from the undo stack to return it as the new current image. If there are no states to undo or if the current image is None, it returns None, indicating that the undo operation cannot be performed.
        """
        if not self.can_undo() or current is None:
            return None
        self._redo_stack.append(current.copy())
        return self._undo_stack.pop()

    def redo(self, current: np.ndarray) -> Optional[np.ndarray]:
        """
        Perform a redo operation. This method checks if there are states available to redo and if the current image is not None. If both conditions are met, it pushes the current state onto the undo stack and pops the last state from the redo stack to return it as the new current image. If there are no states to redo or if the current image is None, it returns None, indicating that the redo operation cannot be performed.
        """
        if not self.can_redo() or current is None:
            return None
        self._undo_stack.append(current.copy())
        return self._redo_stack.pop()
