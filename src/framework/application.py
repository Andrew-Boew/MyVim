from typing import Any
from src.adapter.base import ITuiAdapter
from src.framework.base import ITuiApplication


class TuiApplication(ITuiApplication):
    def __init__(
        self,
        adapter: ITuiAdapter,
        model: Any,
        view: Any,
        controller: Any,
    ):
        self._adapter = adapter
        self._model = model
        self._view = view
        self._controller = controller

    def get_adapter(self) -> ITuiAdapter:
        return self._adapter

    def get_model(self) -> Any:
        return self._model

    def get_view(self) -> Any:
        return self._view

    def get_controller(self) -> Any:
        return self._controller

    def run(self) -> None:
        if hasattr(self._controller, "run"):
            self._controller.run()
            return

        self._adapter.initialize()
        try:
            if hasattr(self._controller, "start"):
                self._controller.start()

            if hasattr(self._controller, "render"):
                self._controller.render()

            while getattr(self._controller, "is_running", lambda: True)():
                try:
                    key = self._adapter.get_key()
                except KeyboardInterrupt:
                    break

                if key != -1:
                    if hasattr(self._controller, "handle_key"):
                        if not self._controller.handle_key(key):
                            break

                if hasattr(self._controller, "render"):
                    self._controller.render()
        except KeyboardInterrupt:
            pass
        finally:
            self._adapter.shutdown()
