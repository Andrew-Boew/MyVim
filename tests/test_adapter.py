import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adapter.base import KeyCode
from src.adapter.mock_adapter import MockTuiAdapter


def test_mock_adapter_init_and_size():
    adapter = MockTuiAdapter(rows=30, cols=100)
    adapter.initialize()
    assert adapter.is_initialized is True
    assert adapter.get_size() == (30, 100)
    adapter.shutdown()
    assert adapter.is_initialized is False


def test_mock_adapter_write_and_clear():
    adapter = MockTuiAdapter(rows=5, cols=20)
    adapter.initialize()
    adapter.add_str(0, 0, "Hello, VIM!")
    adapter.add_str(1, 2, "Test")

    assert adapter.get_line_text(0) == "Hello, VIM!"
    assert adapter.get_line_text(1) == "  Test"

    adapter.clear_line(0)
    assert adapter.get_line_text(0) == ""
    assert adapter.get_line_text(1) == "  Test"

    adapter.clear()
    assert adapter.get_line_text(1) == ""


def test_mock_adapter_cursor_and_clamping():
    adapter = MockTuiAdapter(rows=10, cols=20)
    adapter.initialize()
    adapter.move_cursor(5, 7)
    assert adapter.cursor_row == 5
    assert adapter.cursor_col == 7

    adapter.move_cursor(100, 100)
    assert adapter.cursor_row == 9
    assert adapter.cursor_col == 19

    adapter.move_cursor(-5, -5)
    assert adapter.cursor_row == 0
    assert adapter.cursor_col == 0


def test_mock_adapter_input_queue():
    adapter = MockTuiAdapter()
    adapter.feed_input([ord("i"), KeyCode.ESC, KeyCode.UP])

    assert adapter.get_key() == ord("i")
    assert adapter.get_key() == KeyCode.ESC
    assert adapter.get_key() == KeyCode.UP
    assert adapter.get_key() == -1
