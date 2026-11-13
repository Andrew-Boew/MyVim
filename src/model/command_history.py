from typing import Any, Dict, List, Optional


class SingletonMeta(type):
    _instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def reset_instance(cls):
        cls._instances.pop(cls, None)


class CommandHistory(metaclass=SingletonMeta):
    def __init__(self, capacity: int = 100) -> None:
        if not hasattr(self, "_undo_stack"):
            self._capacity = capacity
            self._undo_stack: List[Dict[str, Any]] = []

    @classmethod
    def reset_instance(cls) -> None:
        SingletonMeta._instances.pop(cls, None)

    def push(self, snapshot: Dict[str, Any]) -> None:
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self._capacity:
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
