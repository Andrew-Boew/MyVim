import tempfile
import os
from src.adapter.mock_adapter import MockTuiAdapter
from src.model.document import TextDocument
from src.view.editor_view import EditorView
from src.controller.editor_controller import EditorController
from src.controller.commands import (
    ICommand,
    SetLineNumbersCommand,
    SaveCommand,
    UndoCommand,
    RevertCommand,
    SyntaxCommand,
)
from src.view.syntax_decorator import SyntaxHighlightDecorator, EditorViewDecorator


def test_command_inheritance():
    assert issubclass(SetLineNumbersCommand, ICommand)
    assert issubclass(SaveCommand, ICommand)
    assert issubclass(UndoCommand, ICommand)
    assert issubclass(RevertCommand, ICommand)


def test_set_line_numbers_command_direct():
    adapter = MockTuiAdapter(24, 80)
    view = EditorView(adapter)
    assert not view.is_line_numbers_enabled()

    cmd_enable = SetLineNumbersCommand(view, enabled=True)
    res = cmd_enable.execute()
    assert res is True
    assert view.is_line_numbers_enabled()

    cmd_disable = SetLineNumbersCommand(view, enabled=False)
    res = cmd_disable.execute()
    assert res is False
    assert not view.is_line_numbers_enabled()

    cmd_toggle = SetLineNumbersCommand(view)
    res = cmd_toggle.execute()
    assert res is True
    assert view.is_line_numbers_enabled()

    res = cmd_toggle.execute()
    assert res is False
    assert not view.is_line_numbers_enabled()


def test_document_commands():
    doc = TextDocument("Initial text")
    assert doc.get_text() == "Initial text"

    doc.cut_line()
    assert doc.get_text() == ""

    undo_cmd = UndoCommand(doc)
    assert undo_cmd.execute() is True
    assert doc.get_text() == "Initial text"

    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        save_cmd = SaveCommand(doc, tmp_name)
        assert save_cmd.execute() is True

        doc.cut_line()
        assert doc.get_text() == ""

        revert_cmd = RevertCommand(doc)
        assert revert_cmd.execute() is True
        assert doc.get_text() == "Initial text"
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def test_controller_set_num_commands():
    adapter = MockTuiAdapter(24, 80)
    doc = TextDocument("Line 1\nLine 2")
    view = EditorView(adapter)
    ctrl = EditorController(doc, adapter, view)

    for ch in ":set nu\n":
        ctrl.handle_key(ord(ch) if ch != "\n" else 10)

    assert view.is_line_numbers_enabled()
    assert ctrl.get_status_message() == "Line numbers enabled"

    for ch in ":set nonu\n":
        ctrl.handle_key(ord(ch) if ch != "\n" else 10)

    assert not view.is_line_numbers_enabled()
    assert ctrl.get_status_message() == "Line numbers disabled"

    for ch in ":set num\n":
        ctrl.handle_key(ord(ch) if ch != "\n" else 10)

    assert view.is_line_numbers_enabled()

    for ch in ":set nu!\n":
        ctrl.handle_key(ord(ch) if ch != "\n" else 10)

    assert not view.is_line_numbers_enabled()
    assert ctrl.get_status_message() == "Line numbers disabled"


def test_view_render_with_line_numbers():
    adapter = MockTuiAdapter(10, 40)
    doc = TextDocument("First line\nSecond line")
    view = EditorView(adapter)

    view.set_line_numbers(True)
    view.render(doc, "NORMAL")

    screen_lines = adapter.get_screen_lines()
    assert "  1 First line" in screen_lines[0]
    assert "  2 Second line" in screen_lines[1]

    cursor_r, cursor_c = adapter.cursor_row, adapter.cursor_col
    assert cursor_r == 0
    assert cursor_c == 4

    view.set_line_numbers(False)
    view.render(doc, "NORMAL")

    screen_lines_no_num = adapter.get_screen_lines()
    assert screen_lines_no_num[0].startswith("First line")
    cursor_r, cursor_c = adapter.cursor_row, adapter.cursor_col
    assert cursor_r == 0
    assert cursor_c == 0


def test_syntax_command_and_decorator():
    adapter = MockTuiAdapter(10, 40)
    base_view = EditorView(adapter)
    doc = TextDocument("def test():\n    return 42\n# comment")
    ctrl = EditorController(doc, adapter, base_view)

    assert not ctrl.get_view().is_syntax_enabled()

    for ch in ":sy\n":
        ctrl.handle_key(ord(ch) if ch != "\n" else 10)

    assert ctrl.get_view().is_syntax_enabled()
    assert isinstance(ctrl.get_view(), SyntaxHighlightDecorator)
    assert ctrl.get_status_message() == "Syntax highlighting enabled"

    ctrl.render()
    screen_lines = adapter.get_screen_lines()
    assert "[syntax]" in screen_lines[8]
    assert "def test():" in screen_lines[0]

    for ch in ":sy off\n":
        ctrl.handle_key(ord(ch) if ch != "\n" else 10)

    assert not ctrl.get_view().is_syntax_enabled()
    assert ctrl.get_status_message() == "Syntax highlighting disabled"

    decorator = SyntaxHighlightDecorator(base_view)
    tokens = decorator._tokenize("def foo(x = 123):\n    return 'hello' # comment\nprint(x)")
    kinds = [k for _, k in tokens]
    assert "KEYWORD" in kinds
    assert "FUNCTION" in kinds
    assert "STRING" in kinds
    assert "COMMENT" in kinds
    assert "NUMBER" in kinds
    assert "BUILTIN" in kinds
    assert "SELF" in [k for _, k in decorator._tokenize("self._value")]
    assert "DECORATOR" in [k for _, k in decorator._tokenize("@classmethod")]
    tokens_rt = decorator._tokenize("return True")
    assert tokens_rt[0] == ("return", "KEYWORD")
    assert tokens_rt[2] == ("True", "CONSTANT")
    assert decorator.unwrap() is base_view
