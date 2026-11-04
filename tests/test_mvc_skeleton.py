import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adapter.base import KeyCode
from src.adapter.mock_adapter import MockTuiAdapter
from src.controller.editor_controller import EditorController, EditorMode
from src.model.document import TextDocument
from src.model.text_line import TextLine
from src.view.editor_view import EditorView


def test_text_line_mystring_wrapper():
    line = TextLine("Hello, VIM!")
    assert line.size() == 11
    assert len(line) == 11
    assert line.c_str() == "Hello, VIM!"
    assert str(line) == "Hello, VIM!"

    line.insert(7, "my ")
    assert line.c_str() == "Hello, my VIM!"

    line.erase(7, 3)
    assert line.c_str() == "Hello, VIM!"

    line.replace_char(0, "h")
    assert line.c_str() == "hello, VIM!"


def test_text_line_word_navigation():
    line = TextLine("first second third")
    assert line.find_word_end(0) == 4
    assert line.find_word_start(10) == 6
    start, end = line.get_word_range_at(7)
    assert start == 6
    assert end == 13


def test_text_document_basic():
    doc = TextDocument("line 1\nline 2\nline 3")
    assert doc.get_line_count() == 3
    assert doc.get_line(0).c_str() == "line 1"
    assert doc.get_line(1).c_str() == "line 2"

    doc.set_cursor(1, 4)
    assert doc.get_cursor() == (1, 4)


def test_text_document_undo():
    doc = TextDocument("initial text")
    doc.record_snapshot()
    doc.get_line(0).insert(0, "prefix ")
    doc.set_modified(True)

    assert doc.get_line(0).c_str() == "prefix initial text"
    assert doc.is_modified() is True

    res = doc.undo()
    assert res is True
    assert doc.get_line(0).c_str() == "initial text"
    assert doc.is_modified() is False


def test_editor_view_render():
    adapter = MockTuiAdapter(rows=10, cols=40)
    adapter.initialize()
    view = EditorView(adapter)
    doc = TextDocument("alpha\nbeta\ngamma")

    view.render(doc, mode_name="NORMAL", status_message="Ready")

    lines = adapter.get_screen_lines()
    assert lines[0] == "alpha"
    assert lines[1] == "beta"
    assert lines[2] == "gamma"
    assert lines[3] == "~"
    assert "-- NORMAL --" in lines[8]
    assert "Ready" in lines[9]


def test_editor_controller_modes():
    doc = TextDocument("hello")
    adapter = MockTuiAdapter()
    adapter.initialize()
    view = EditorView(adapter)
    controller = EditorController(doc, adapter, view)

    assert controller.get_mode() == EditorMode.NORMAL

    controller.handle_key(ord("i"))
    assert controller.get_mode() == EditorMode.INSERT

    controller.handle_key(KeyCode.ESC)
    assert controller.get_mode() == EditorMode.NORMAL

    controller.handle_key(ord(":"))
    assert controller.get_mode() == EditorMode.COMMAND

    controller.handle_key(ord("q"))
    controller.handle_key(KeyCode.ENTER)
    assert controller.is_running() is False
