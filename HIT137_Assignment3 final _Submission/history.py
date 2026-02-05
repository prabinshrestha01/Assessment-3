"""
history.py
Undo/Redo management and helper UI components (status text + message boxes).

This file is intended to satisfy the "3rd class" requirement from the assignment.
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
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self, current: np.ndarray) -> Optional[np.ndarray]:
        if not self.can_undo() or current is None:
            return None
        self._redo_stack.append(current.copy())
        return self._undo_stack.pop()

    def redo(self, current: np.ndarray) -> Optional[np.ndarray]:
        if not self.can_redo() or current is None:
            return None
        self._undo_stack.append(current.copy())
        return self._redo_stack.pop()
