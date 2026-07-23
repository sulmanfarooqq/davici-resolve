"""Undo/redo manager for grade state snapshots."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class GradeSnapshot:
    grade_params: Dict[str, Any] = field(default_factory=dict)
    node_graph: Optional[Dict[str, Any]] = None
    lut_path: Optional[str] = None


class UndoManager:
    def __init__(self, max_stack: int = 50):
        self._stack: List[GradeSnapshot] = []
        self._index: int = -1
        self._max = max_stack

    @property
    def can_undo(self) -> bool:
        return self._index >= 0

    @property
    def can_redo(self) -> bool:
        return self._index < len(self._stack) - 1

    def push_state(self, snapshot: GradeSnapshot):
        self._stack = self._stack[:self._index + 1]
        self._stack.append(snapshot)
        if len(self._stack) > self._max:
            self._stack.pop(0)
        self._index = len(self._stack) - 1

    def undo(self) -> Optional[GradeSnapshot]:
        if not self.can_undo:
            return None
        self._index -= 1
        return self._stack[self._index] if self._index >= 0 else None

    def redo(self) -> Optional[GradeSnapshot]:
        if not self.can_redo:
            return None
        self._index += 1
        return self._stack[self._index] if self._index < len(self._stack) else None

    def clear(self):
        self._stack.clear()
        self._index = -1

    def __len__(self) -> int:
        return len(self._stack)
