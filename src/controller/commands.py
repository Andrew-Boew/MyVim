from abc import ABC, abstractmethod
from typing import Optional, Any, Callable, Dict, List, Tuple


class ICommand(ABC):
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        pass


class SetLineNumbersCommand(ICommand):
    def __init__(self, view: Any = None, enabled: Optional[bool] = None, controller: Optional[Any] = None):
        self._view = view
        self._enabled = enabled
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        target_view = self._view if self._view is not None else (self._controller.get_view() if self._controller is not None else None)
        if target_view is None:
            return False
        if self._enabled is None:
            state = target_view.toggle_line_numbers()
        else:
            target_view.set_line_numbers(self._enabled)
            state = self._enabled
        if self._controller is not None:
            msg = "Line numbers enabled" if state else "Line numbers disabled"
            self._controller.set_status_message(msg)
        return state


class SaveCommand(ICommand):
    def __init__(self, doc: Any, filename: Optional[str] = None, controller: Optional[Any] = None):
        self._doc = doc
        self._filename = filename
        self._controller = controller

    def execute(self, filename: Optional[str] = None, *args: Any, **kwargs: Any) -> bool:
        target = filename if filename is not None else self._filename
        try:
            self._doc.save(target)
            if self._controller is not None:
                fname = target or self._doc.get_filename() or "[No Name]"
                self._controller.set_status_message(f'"{fname}" written')
            return True
        except Exception as e:
            if self._controller is not None:
                self._controller.set_status_message(str(e))
            return True


class UndoCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None):
        self._doc = doc
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        res = self._doc.undo()
        if self._controller is not None:
            msg = "Change undone" if res else "Already at oldest change"
            self._controller.set_status_message(msg)
        return res


class UndoLineCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None):
        self._doc = doc
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        res = self._doc.undo_line()
        if self._controller is not None:
            msg = "Line restored" if res else "Line not modified"
            self._controller.set_status_message(msg)
        return res


class RevertCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None):
        self._doc = doc
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        try:
            self._doc.revert()
            if self._controller is not None:
                self._controller.set_status_message("Changes reverted")
            return True
        except Exception as e:
            if self._controller is not None:
                self._controller.set_status_message(str(e))
            return True


class SyntaxCommand(ICommand):
    def __init__(self, controller: Any, enabled: Optional[bool] = None):
        self._controller = controller
        self._enabled = enabled

    def execute(self, arg: Optional[str] = None, *args: Any, **kwargs: Any) -> bool:
        if arg is not None and arg != "":
            val = arg.strip().lower()
            if val in ("on", "1"):
                state = self._controller.toggle_syntax_highlighting(True)
                self._controller.set_status_message("Syntax highlighting enabled")
                return state
            elif val in ("off", "0"):
                state = self._controller.toggle_syntax_highlighting(False)
                self._controller.set_status_message("Syntax highlighting disabled")
                return state
        target_enabled = self._enabled
        state = self._controller.toggle_syntax_highlighting(target_enabled)
        msg = "Syntax highlighting enabled" if state else "Syntax highlighting disabled"
        self._controller.set_status_message(msg)
        return state


class QuitCommand(ICommand):
    def __init__(self, controller: Any, doc: Optional[Any] = None, force: bool = False):
        self._controller = controller
        self._doc = doc
        self._force = force

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        if not self._force and self._doc is not None and self._doc.is_modified():
            self._controller.set_status_message("No write since last change (add ! to override)")
            return True
        self._controller.stop()
        return False


class SaveAndQuitCommand(ICommand):
    def __init__(self, doc: Any, controller: Any):
        self._doc = doc
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        try:
            self._doc.save()
            self._controller.stop()
            return False
        except Exception as e:
            self._controller.set_status_message(str(e))
            return True


class OpenFileCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None, filename: Optional[str] = None):
        self._doc = doc
        self._controller = controller
        self._filename = filename

    def execute(self, filename: Optional[str] = None, *args: Any, **kwargs: Any) -> bool:
        target = filename if filename is not None else self._filename
        try:
            if target:
                self._doc.load(target)
                if self._controller is not None:
                    self._controller.set_status_message(f'"{target}" loaded')
        except Exception as e:
            if self._controller is not None:
                self._controller.set_status_message(str(e))
        return True


class GotoLineCommand(ICommand):
    def __init__(self, doc: Any, line_num: Optional[int] = None):
        self._doc = doc
        self._line_num = line_num

    def execute(self, line_num: Optional[int] = None, *args: Any, **kwargs: Any) -> bool:
        target = line_num if line_num is not None else self._line_num
        if target is not None:
            self._doc.move_cursor_to_line(target)
        return True


class HelpCommand(ICommand):
    def __init__(self, controller: Any):
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._controller.set_status_message(":w save | :q exit | :o open | :set num | :sy syntax | / search | i insert")
        return True


class DeleteCharCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.delete_char()
        return True


class CutLineCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.cut_line()
        return True


class DeleteWordCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.delete_word()
        return True


class CopyLineCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None):
        self._doc = doc
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.copy_line()
        if self._controller is not None:
            self._controller.set_status_message("Line yanked")
        return True


class CopyWordCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None):
        self._doc = doc
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.copy_word()
        if self._controller is not None:
            self._controller.set_status_message("Word yanked")
        return True


class PasteCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.paste()
        return True


class CursorLeftCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_left()
        return True


class CursorRightCommand(ICommand):
    def __init__(self, doc: Any, allow_past_end: bool = False):
        self._doc = doc
        self._allow_past_end = allow_past_end

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_right(allow_past_end=self._allow_past_end)
        return True


class CursorUpCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_up()
        return True


class CursorDownCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_down()
        return True


class CursorLineStartCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_line_start()
        return True


class CursorLineEndCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_line_end()
        return True


class CursorPageUpCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.page_up()
        return True


class CursorPageDownCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.page_down()
        return True


class CursorWordForwardCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_word_forward()
        return True


class CursorWordBackwardCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_word_backward()
        return True


class CursorFileStartCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_file_start()
        return True


class CursorFileEndCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.move_cursor_file_end()
        return True


class InsertTextCommand(ICommand):
    def __init__(self, doc: Any, text: str = ""):
        self._doc = doc
        self._text = text

    def execute(self, text: Optional[str] = None, *args: Any, **kwargs: Any) -> bool:
        t = text if text is not None else self._text
        self._doc.insert_text(t)
        return True


class SplitLineCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.split_line()
        return True


class BackspaceCommand(ICommand):
    def __init__(self, doc: Any):
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._doc.backspace()
        return True


class RepeatSearchCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None, reverse: bool = False):
        self._doc = doc
        self._controller = controller
        self._reverse = reverse

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        res = self._doc.repeat_search(reverse=self._reverse)
        if not res and self._controller is not None:
            self._controller.set_status_message("Pattern not found")
        return res


class SearchCommand(ICommand):
    def __init__(self, doc: Any, controller: Optional[Any] = None, query: Optional[str] = None, forward: bool = True):
        self._doc = doc
        self._controller = controller
        self._query = query
        self._forward = forward

    def execute(self, query: Optional[str] = None, *args: Any, **kwargs: Any) -> bool:
        q = query if query is not None else self._query
        if q:
            res = self._doc.search(q, forward=self._forward)
            if not res and self._controller is not None:
                self._controller.set_status_message(f"Pattern not found: {q}")
            return res
        return True


class ChangeModeCommand(ICommand):
    def __init__(self, controller: Any, mode: Any, prep: Optional[Callable[[], Any]] = None):
        self._controller = controller
        self._mode = mode
        self._prep = prep

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._controller.set_mode(self._mode)
        self._controller.set_status_message("")
        if self._prep is not None:
            self._prep()
        return True


class NormalQuitCommand(ICommand):
    def __init__(self, controller: Any, doc: Any):
        self._controller = controller
        self._doc = doc

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        if not self._doc.is_modified():
            self._controller.stop()
            return False
        self._controller.set_status_message("No write since last change (use :q! to override)")
        return True


class EnterReplaceModeCommand(ICommand):
    def __init__(self, controller: Any):
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        self._controller.set_replace_mode(True)
        return True


class ReplaceCharCommand(ICommand):
    def __init__(self, doc: Any, char: Optional[str] = None):
        self._doc = doc
        self._char = char

    def execute(self, char: Optional[str] = None, *args: Any, **kwargs: Any) -> bool:
        c = char if char is not None else self._char
        if c is not None:
            self._doc.replace_char(c)
        return True


class EscCommand(ICommand):
    def __init__(self, controller: Any):
        self._controller = controller

    def execute(self, *args: Any, **kwargs: Any) -> bool:
        if self._controller.get_pending_keys() == "ESC":
            self._controller.stop()
            return False
        self._controller.set_pending_keys("ESC")
        self._controller.set_status_message("Press ESC again to exit, or type :q")
        return True


class CommandRegistry:
    def __init__(self) -> None:
        self._exact_commands: Dict[str, Any] = {}
        self._prefix_commands: List[Tuple[str, Any]] = []
        self._numeric_handler: Optional[Any] = None
        self._normal_keys: Dict[Any, ICommand] = {}
        self._multi_keys: Dict[str, ICommand] = {}
        self._insert_keys: Dict[Any, ICommand] = {}

    def register(self, name: str, handler: Any) -> None:
        self._exact_commands[name] = handler

    def register_prefix(self, prefix: str, handler: Any) -> None:
        self._prefix_commands.append((prefix, handler))

    def register_numeric(self, handler: Any) -> None:
        self._numeric_handler = handler

    def register_normal_key(self, key: Any, command: ICommand) -> None:
        self._normal_keys[key] = command

    def register_multi_key(self, sequence: str, command: ICommand) -> None:
        self._multi_keys[sequence] = command

    def register_insert_key(self, key: Any, command: ICommand) -> None:
        self._insert_keys[key] = command

    def get_normal_key(self, key: Any) -> Optional[ICommand]:
        return self._normal_keys.get(key)

    def get_multi_key(self, sequence: str) -> Optional[ICommand]:
        return self._multi_keys.get(sequence)

    def has_multi_key_prefix(self, prefix: str) -> bool:
        return any(k.startswith(prefix) for k in self._multi_keys)

    def get_insert_key(self, key: Any) -> Optional[ICommand]:
        return self._insert_keys.get(key)

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
                arg = cmd_stripped[len(prefix):].strip()
                if isinstance(phandler, ICommand):
                    return phandler.execute(arg)
                if callable(phandler):
                    return phandler(cmd_stripped)
        if cmd_stripped.isdigit() and self._numeric_handler is not None:
            if isinstance(self._numeric_handler, ICommand):
                return self._numeric_handler.execute(int(cmd_stripped))
            if callable(self._numeric_handler):
                return self._numeric_handler(int(cmd_stripped))
        return None

    def register_defaults(self, controller: Any, doc: Any, view: Any) -> None:
        from src.adapter.base import KeyCode

        quit_forced = QuitCommand(controller, doc, force=True)
        quit_normal = QuitCommand(controller, doc, force=False)
        save_and_quit = SaveAndQuitCommand(doc, controller)
        save_current = SaveCommand(doc, controller=controller)
        save_target = SaveCommand(doc, controller=controller)
        open_file = OpenFileCommand(doc, controller=controller)
        revert_file = RevertCommand(doc, controller=controller)
        line_num_on = SetLineNumbersCommand(view, enabled=True, controller=controller)
        line_num_off = SetLineNumbersCommand(view, enabled=False, controller=controller)
        line_num_toggle = SetLineNumbersCommand(view, enabled=None, controller=controller)
        help_cmd = HelpCommand(controller)
        syntax_toggle = SyntaxCommand(controller, enabled=None)
        syntax_on = SyntaxCommand(controller, enabled=True)
        syntax_off = SyntaxCommand(controller, enabled=False)
        goto_line = GotoLineCommand(doc)

        for name in ("q!", "quit!", "й!", "й! "):
            self.register(name, quit_forced)

        for name in ("q", "quit", "й"):
            self.register(name, quit_normal)

        for name in ("wq!", "wq", "x", "x!", "цй!", "цй", "ч", "ч!"):
            self.register(name, save_and_quit)

        for name in ("w", "ц"):
            self.register(name, save_current)

        for prefix in ("w ", "ц "):
            self.register_prefix(prefix, save_target)

        for prefix in ("o ", "щ ", "e ", "у "):
            self.register_prefix(prefix, open_file)

        for name in ("e!", "у!"):
            self.register(name, revert_file)

        for name in ("set num", "set nu"):
            self.register(name, line_num_on)

        for name in ("set nonu", "set nonumber"):
            self.register(name, line_num_off)

        for name in ("set invnu", "set nu!", "set num!"):
            self.register(name, line_num_toggle)

        for name in ("sy", "syntax", "sy!", "syntax!", "сы", "сы!"):
            self.register(name, syntax_toggle)

        for name in ("sy on", "syntax on", "сы on"):
            self.register(name, syntax_on)

        for name in ("sy off", "syntax off", "сы off"):
            self.register(name, syntax_off)

        for prefix in ("sy ", "syntax ", "сы "):
            self.register_prefix(prefix, syntax_toggle)

        for name in ("h", "help"):
            self.register(name, help_cmd)

        self.register_numeric(goto_line)

        normal_bindings = {
            KeyCode.ESC: EscCommand(controller),
            27: EscCommand(controller),
            ord("q"): NormalQuitCommand(controller, doc),
            1081: NormalQuitCommand(controller, doc),
            ord(":"): ChangeModeCommand(controller, "COMMAND", prep=lambda: controller.set_command_buffer(":")),
            ord("/"): ChangeModeCommand(controller, "SEARCH", prep=lambda: controller.set_command_buffer("/")),
            ord("?"): ChangeModeCommand(controller, "SEARCH", prep=lambda: controller.set_command_buffer("?")),
            ord("i"): ChangeModeCommand(controller, "INSERT"),
            ord("I"): ChangeModeCommand(controller, "INSERT", prep=doc.move_cursor_line_start),
            ord("A"): ChangeModeCommand(controller, "INSERT", prep=lambda: (doc.move_cursor_line_end(), doc.move_cursor_right(allow_past_end=True))),
            ord("o"): ChangeModeCommand(controller, "INSERT", prep=doc.open_line_below),
            ord("O"): ChangeModeCommand(controller, "INSERT", prep=doc.open_line_above),
            ord("S"): ChangeModeCommand(controller, "INSERT", prep=doc.clear_current_line),
            ord("r"): EnterReplaceModeCommand(controller),
            ord("x"): DeleteCharCommand(doc),
            KeyCode.DELETE: DeleteCharCommand(doc),
            ord("p"): PasteCommand(doc),
            ord("u"): UndoCommand(doc, controller=controller),
            ord("U"): UndoLineCommand(doc, controller=controller),
            ord("n"): RepeatSearchCommand(doc, controller=controller, reverse=False),
            ord("N"): RepeatSearchCommand(doc, controller=controller, reverse=True),
            KeyCode.LEFT: CursorLeftCommand(doc),
            ord("h"): CursorLeftCommand(doc),
            KeyCode.RIGHT: CursorRightCommand(doc),
            ord("l"): CursorRightCommand(doc),
            KeyCode.UP: CursorUpCommand(doc),
            ord("k"): CursorUpCommand(doc),
            KeyCode.DOWN: CursorDownCommand(doc),
            ord("j"): CursorDownCommand(doc),
            ord("0"): CursorLineStartCommand(doc),
            ord("^"): CursorLineStartCommand(doc),
            KeyCode.HOME: CursorLineStartCommand(doc),
            ord("$"): CursorLineEndCommand(doc),
            KeyCode.END: CursorLineEndCommand(doc),
            KeyCode.PAGE_UP: CursorPageUpCommand(doc),
            KeyCode.PAGE_DOWN: CursorPageDownCommand(doc),
            ord("w"): CursorWordForwardCommand(doc),
            ord("b"): CursorWordBackwardCommand(doc),
            ord("G"): CursorFileEndCommand(doc),
        }
        for k, v in normal_bindings.items():
            self.register_normal_key(k, v)

        multi_bindings = {
            "dd": CutLineCommand(doc),
            "dw": DeleteWordCommand(doc),
            "diw": DeleteWordCommand(doc),
            "yy": CopyLineCommand(doc, controller=controller),
            "yw": CopyWordCommand(doc, controller=controller),
            "gg": CursorFileStartCommand(doc),
        }
        for seq, v in multi_bindings.items():
            self.register_multi_key(seq, v)

        insert_bindings = {
            KeyCode.ESC: ChangeModeCommand(controller, "NORMAL", prep=doc.move_cursor_left),
            27: ChangeModeCommand(controller, "NORMAL", prep=doc.move_cursor_left),
            KeyCode.ENTER: SplitLineCommand(doc),
            KeyCode.RETURN: SplitLineCommand(doc),
            10: SplitLineCommand(doc),
            13: SplitLineCommand(doc),
            343: SplitLineCommand(doc),
            KeyCode.KEY_BACKSPACE: BackspaceCommand(doc),
            KeyCode.BACKSPACE: BackspaceCommand(doc),
            8: BackspaceCommand(doc),
            127: BackspaceCommand(doc),
            KeyCode.LEFT: CursorLeftCommand(doc),
            KeyCode.RIGHT: CursorRightCommand(doc, allow_past_end=True),
            KeyCode.UP: CursorUpCommand(doc),
            KeyCode.DOWN: CursorDownCommand(doc),
        }
        for k, v in insert_bindings.items():
            self.register_insert_key(k, v)
