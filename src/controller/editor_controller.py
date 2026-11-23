from enum import Enum
from typing import Optional, Callable, Any

from src.adapter.base import ITuiAdapter, KeyCode
from src.controller.commands import ICommand, CommandRegistry
from src.model.document import TextDocument
from src.view.editor_view import EditorView


class EditorMode(str, Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    COMMAND = "COMMAND"
    SEARCH = "SEARCH"


class EditorController:
    def __init__(
        self,
        doc: Optional[TextDocument] = None,
        adapter: Optional[ITuiAdapter] = None,
        view: Optional[EditorView] = None,
    ):
        self._doc = doc if doc is not None else TextDocument()
        self._adapter = adapter
        self._view = view if view is not None else (EditorView(adapter) if adapter else None)
        self._mode = EditorMode.NORMAL
        self._status_message = ""
        self._command_buffer = ""
        self._pending_keys = ""
        self._replace_mode = False
        self._running = False
        self._registry = CommandRegistry()
        self._registry.register_defaults(self, self._doc, self._view)

    def register_normal_key(self, key: Any, command: ICommand) -> None:
        self._registry.register_normal_key(key, command)

    def register_multi_key(self, sequence: str, command: ICommand) -> None:
        self._registry.register_multi_key(sequence, command)

    def register_insert_key(self, key: Any, command: ICommand) -> None:
        self._registry.register_insert_key(key, command)

    def register_command(self, name: str, handler: Any) -> None:
        self._registry.register(name, handler)

    def register_prefix_command(self, prefix: str, handler: Any) -> None:
        self._registry.register_prefix(prefix, handler)

    def get_command_registry(self) -> CommandRegistry:
        return self._registry

    def get_document(self) -> TextDocument:
        return self._doc

    def get_view(self) -> Optional[Any]:
        return self._view

    def set_view(self, view: Optional[Any]) -> None:
        self._view = view

    def toggle_syntax_highlighting(self, enabled: Optional[bool] = None) -> bool:
        if self._view is None:
            return False
        current_state = self._view.is_syntax_enabled()
        target_state = not current_state if enabled is None else enabled
        if target_state == current_state:
            return current_state
        if target_state:
            from src.view.syntax_decorator import SyntaxHighlightDecorator
            self._view = SyntaxHighlightDecorator(self._view)
        else:
            from src.view.syntax_decorator import EditorViewDecorator
            if isinstance(self._view, EditorViewDecorator):
                self._view = self._view.unwrap()
        return target_state

    def get_adapter(self) -> Optional[ITuiAdapter]:
        return self._adapter

    def get_mode(self) -> EditorMode:
        return self._mode

    def set_mode(self, mode: Any) -> None:
        if isinstance(mode, str) and not isinstance(mode, EditorMode):
            try:
                self._mode = EditorMode(mode)
            except ValueError:
                self._mode = mode
        else:
            self._mode = mode
        self._command_buffer = ""
        self._pending_keys = ""
        self._replace_mode = False

    def get_status_message(self) -> str:
        return self._status_message

    def set_status_message(self, message: str) -> None:
        self._status_message = message

    def get_pending_keys(self) -> str:
        return self._pending_keys

    def set_pending_keys(self, val: str) -> None:
        self._pending_keys = val

    def is_replace_mode(self) -> bool:
        return self._replace_mode

    def set_replace_mode(self, val: bool) -> None:
        self._replace_mode = val

    def get_command_buffer(self) -> str:
        return self._command_buffer

    def set_command_buffer(self, buf: str) -> None:
        self._command_buffer = buf

    def is_running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False

    def handle_key(self, key: int) -> bool:
        if key == -1:
            return True

        if key in (3, 4):
            self.stop()
            return False

        if self._mode == EditorMode.NORMAL:
            return self._handle_normal_mode_key(key)
        elif self._mode == EditorMode.INSERT:
            return self._handle_insert_mode_key(key)
        elif self._mode == EditorMode.COMMAND:
            return self._handle_command_mode_key(key)
        elif self._mode == EditorMode.SEARCH:
            return self._handle_search_mode_key(key)

        return True

    def _handle_normal_mode_key(self, key: int) -> bool:
        if self._replace_mode:
            self._replace_mode = False
            if 32 <= key <= 126 or (key > 127 and key < 65536):
                self._doc.replace_char(chr(key))
            return True

        if self._pending_keys == "ESC" and key not in (KeyCode.ESC, 27):
            self._pending_keys = ""
            self._status_message = ""

        if ord("1") <= key <= ord("9") or (self._pending_keys.isdigit() and ord("0") <= key <= ord("9")):
            self._pending_keys += chr(key)
            return True

        if key == ord("G") and self._pending_keys.isdigit():
            line_num = int(self._pending_keys)
            self._pending_keys = ""
            self._doc.move_cursor_to_line(line_num)
            return True

        char_key = chr(key) if 0 <= key < 65536 else ""
        candidate_seq = self._pending_keys + char_key if char_key else ""

        if candidate_seq:
            cmd = self._registry.get_multi_key(candidate_seq)
            if cmd is not None:
                self._pending_keys = ""
                return cmd.execute()
            if self._registry.has_multi_key_prefix(candidate_seq):
                self._pending_keys = candidate_seq
                return True

        self._pending_keys = ""

        cmd = self._registry.get_normal_key(key)
        if cmd is not None:
            return cmd.execute()

        return True

    def _handle_insert_mode_key(self, key: int) -> bool:
        cmd = self._registry.get_insert_key(key)
        if cmd is not None:
            return cmd.execute()
        if 32 <= key <= 126 or (key > 127 and key < 65536):
            self._doc.insert_text(chr(key))
        return True

    def _handle_command_mode_key(self, key: int) -> bool:
        if key in (KeyCode.ESC, 27):
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            self._status_message = ""
            return True

        if key in (KeyCode.KEY_BACKSPACE, KeyCode.BACKSPACE, 8, 127):
            if len(self._command_buffer) > 1:
                self._command_buffer = self._command_buffer[:-1]
            else:
                self._mode = EditorMode.NORMAL
                self._command_buffer = ""
            return True

        if key in (KeyCode.ENTER, KeyCode.RETURN, 10, 13, 343):
            cmd = self._command_buffer[1:].strip()
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            return self._execute_command(cmd)

        if 32 <= key <= 126 or (key > 127 and key < 65536):
            self._command_buffer += chr(key)

        return True

    def _execute_command(self, cmd: str) -> bool:
        if not cmd:
            return True

        result = self._registry.execute(cmd)
        if result is not None:
            return result

        self._status_message = f"Not an editor command: {cmd}"
        return True

    def _handle_search_mode_key(self, key: int) -> bool:
        if key in (KeyCode.ESC, 27):
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            self._status_message = ""
            return True

        if key in (KeyCode.KEY_BACKSPACE, KeyCode.BACKSPACE, 8, 127):
            if len(self._command_buffer) > 1:
                self._command_buffer = self._command_buffer[:-1]
            else:
                self._mode = EditorMode.NORMAL
                self._command_buffer = ""
            return True

        if key in (KeyCode.ENTER, KeyCode.RETURN, 10, 13, 343):
            forward = self._command_buffer.startswith("/")
            query = self._command_buffer[1:]
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            if query:
                if not self._doc.search(query, forward=forward):
                    self._status_message = f"Pattern not found: {query}"
            return True

        if 32 <= key <= 126 or (key > 127 and key < 65536):
            self._command_buffer += chr(key)

        return True

    def render(self) -> None:
        if self._view:
            mode_str = self._mode.value if hasattr(self._mode, "value") else str(self._mode)
            self._view.render(
                self._doc,
                mode_str,
                self._status_message,
                self._command_buffer,
            )

    def run(self) -> None:
        if not self._adapter or not self._view:
            return

        self._running = True
        self._adapter.initialize()
        try:
            while self._running:
                self.render()
                try:
                    key = self._adapter.get_key()
                except KeyboardInterrupt:
                    break
                if not self.handle_key(key):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self._adapter.shutdown()
