from abc import ABC, abstractmethod
from typing import Optional, Any, Callable, Dict, List, Tuple


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


class CommandRegistry:
    def __init__(self) -> None:
        self._exact_commands: Dict[str, Any] = {}
        self._prefix_commands: List[Tuple[str, Any]] = []

    def register(self, name: str, handler: Any) -> None:
        self._exact_commands[name] = handler

    def register_prefix(self, prefix: str, handler: Any) -> None:
        self._prefix_commands.append((prefix, handler))

    def execute(self, cmd: str) -> Optional[bool]:
        cmd_stripped = cmd.strip()
        handler = self._exact_commands.get(cmd_stripped)
        if handler is not None:
            if isinstance(handler, ICommand):
                return handler.execute()
            if callable(handler):
                return handler(cmd_stripped)
        for prefix, phandler in self._prefix_commands:
            if cmd_stripped.startswith(prefix):
                if isinstance(phandler, ICommand):
                    return phandler.execute()
                if callable(phandler):
                    return phandler(cmd_stripped)
        return None

    def register_defaults(self, controller: Any, doc: Any, view: Any) -> None:
        def _quit_forced(cmd: str) -> bool:
            controller.stop()
            return False

        def _quit_normal(cmd: str) -> bool:
            if doc.is_modified():
                controller.set_status_message("No write since last change (add ! to override)")
                return True
            controller.stop()
            return False

        def _save_and_quit(cmd: str) -> bool:
            try:
                SaveCommand(doc).execute()
                controller.stop()
                return False
            except Exception as e:
                controller.set_status_message(str(e))
                return True

        def _save_current(cmd: str) -> bool:
            try:
                SaveCommand(doc).execute()
                fname = doc.get_filename() or "[No Name]"
                controller.set_status_message(f'"{fname}" written')
            except Exception as e:
                controller.set_status_message(str(e))
                return True

        def _save_with_target(cmd: str) -> bool:
            target = cmd[2:].strip()
            try:
                SaveCommand(doc, target).execute()
                controller.set_status_message(f'"{target}" written')
            except Exception as e:
                controller.set_status_message(str(e))
                return True

        def _open_file(cmd: str) -> bool:
            target = cmd[2:].strip()
            try:
                doc.load(target)
                controller.set_status_message(f'"{target}" loaded')
            except Exception as e:
                controller.set_status_message(str(e))
            return True

        def _revert_file(cmd: str) -> bool:
            try:
                RevertCommand(doc).execute()
                controller.set_status_message("Changes reverted")
            except Exception as e:
                controller.set_status_message(str(e))
            return True

        def _line_numbers_on(cmd: str) -> bool:
            if view is not None:
                SetLineNumbersCommand(view, enabled=True).execute()
            controller.set_status_message("Line numbers enabled")
            return True

        def _line_numbers_off(cmd: str) -> bool:
            if view is not None:
                SetLineNumbersCommand(view, enabled=False).execute()
            controller.set_status_message("Line numbers disabled")
            return True

        def _line_numbers_toggle(cmd: str) -> bool:
            if view is not None:
                state = SetLineNumbersCommand(view).execute()
                controller.set_status_message("Line numbers enabled" if state else "Line numbers disabled")
            return True

        def _help(cmd: str) -> bool:
            controller.set_status_message(":w save | :q exit | :q! force | :o open | / search | i insert")
            return True

        for name in ("q!", "quit!", "й!", "й! "):
            self.register(name, _quit_forced)

        for name in ("q", "quit", "й"):
            self.register(name, _quit_normal)

        for name in ("wq!", "wq", "x", "x!", "цй!", "цй", "ч", "ч!"):
            self.register(name, _save_and_quit)

        for name in ("w", "ц"):
            self.register(name, _save_current)

        for prefix in ("w ", "ц "):
            self.register_prefix(prefix, _save_with_target)

        for prefix in ("o ", "щ ", "e ", "у "):
            self.register_prefix(prefix, _open_file)

        for name in ("e!", "у!"):
            self.register(name, _revert_file)

        for name in ("set num", "set nu"):
            self.register(name, _line_numbers_on)

        for name in ("set nonu", "set nonumber"):
            self.register(name, _line_numbers_off)

        for name in ("set invnu", "set nu!", "set num!"):
            self.register(name, _line_numbers_toggle)

        for name in ("h", "help"):
            self.register(name, _help)
