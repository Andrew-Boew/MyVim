from typing import Any, Dict, List, Optional


class CommandHistory:
    _instance: Optional["CommandHistory"] = None

    def __new__(cls) -> "CommandHistory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._undo_stack = []
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def push(self, snapshot: Dict[str, Any]) -> None:
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > 100:
            self._undo_stack.pop(0)

    def pop(self) -> Optional[Dict[str, Any]]:
        if not self._undo_stack:
            return None
        return self._undo_stack.pop()

    def is_empty(self) -> bool:
        return len(self._undo_stack) == 0

    def clear(self) -> None:
        self._undo_stack.clear()

    def get_stack(self) -> List[Dict[str, Any]]:
        return self._undo_stack

    def __len__(self) -> int:
        return len(self._undo_stack)

    def __iter__(self):
        return iter(self._undo_stack)
