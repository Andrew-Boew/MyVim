from abc import ABC, abstractmethod
from typing import Optional, Any


class ICommand(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass


class SetLineNumbersCommand(ICommand):
    def __init__(self, view: Any, enabled: Optional[bool] = None):
        self._view = view
        self._enabled = enabled

    def execute(self) -> bool:
        if self._enabled is None:
            return self._view.toggle_line_numbers()
        self._view.set_line_numbers(self._enabled)
        return self._enabled


class SaveCommand(ICommand):
    def __init__(self, doc: Any, filename: Optional[str] = None):
        self._doc = doc
        self._filename = filename

    def execute(self) -> bool:
        self._doc.save(self._filename)
        return True


class UndoCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self) -> bool:
        return self._doc.undo()


class RevertCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self) -> bool:
        self._doc.revert()
        return True
