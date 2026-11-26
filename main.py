import os
import sys
from typing import Optional

os.environ.setdefault("ESCDELAY", "25")

from src.adapter.curses_adapter import CursesAdapter
from src.controller.editor_controller import EditorController
from src.model.document import TextDocument
from src.view.editor_view import EditorView, EditorStatusView
from src.framework.builder import ApplicationBuilder


class EditorApplication:
    def __init__(self, filepath: Optional[str] = None):
        self.doc = TextDocument()
        if filepath:
            if os.path.exists(filepath):
                self.doc.load(filepath)
            else:
                self.doc.set_filename(filepath)

        self.adapter = CursesAdapter()
        self.view = EditorView(self.adapter, include_status=False)
        self.status_view = EditorStatusView(self.adapter)
        self.controller = EditorController(
            self.doc,
            self.adapter,
            views=[self.view, self.status_view],
        )

        builder = ApplicationBuilder()
        self.app = (
            builder
            .set_adapter(self.adapter)
            .set_model(self.doc)
            .add_view(self.view)
            .add_view(self.status_view)
            .set_controller(self.controller)
            .build()
        )

    def create_editor(self) -> EditorController:
        return self.controller

    def run(self) -> None:
        self.app.run()

    @classmethod
    def main(cls) -> None:
        filepath = sys.argv[1] if len(sys.argv) > 1 else None
        app = cls(filepath)
        app.run()


def main() -> None:
    EditorApplication.main()


if __name__ == "__main__":
    main()
