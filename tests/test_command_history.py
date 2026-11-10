from src.model.command_history import CommandHistory
from src.model.document import TextDocument


def test_command_history_singleton_identity():
    h1 = CommandHistory()
    h2 = CommandHistory()
    assert h1 is h2


def test_command_history_push_pop_clear():
    history = CommandHistory()
    history.clear()
    assert history.is_empty()
    assert len(history) == 0

    history.push({"test": 1})
    history.push({"test": 2})
    assert len(history) == 2
    assert not history.is_empty()

    item = history.pop()
    assert item == {"test": 2}
    assert len(history) == 1

    history.clear()
    assert history.is_empty()
    assert history.pop() is None


def test_command_history_capacity_limit():
    history = CommandHistory()
    history.clear()
    for i in range(120):
        history.push({"index": i})
    assert len(history) == 100
    stack = history.get_stack()
    assert stack[0]["index"] == 20
    assert stack[-1]["index"] == 119
    history.clear()


def test_document_integration_with_history_singleton():
    doc = TextDocument("initial text")
    assert doc.get_history() is CommandHistory()
    doc.insert_text(" added")
    assert not doc.get_history().is_empty()
    assert doc.undo() is True
    assert doc.get_text() == "initial text"
