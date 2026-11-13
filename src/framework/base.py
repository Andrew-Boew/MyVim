from abc import ABC, abstractmethod
from typing import Any


class ITuiModel(ABC):
    @abstractmethod
    def get_state(self) -> Any:
        pass


class ITuiView(ABC):
    @abstractmethod
    def render(self) -> None:
        pass


class ITuiController(ABC):
    @abstractmethod
    def handle_key(self, key: int) -> bool:
        pass

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass


class ITuiApplication(ABC):
    @abstractmethod
    def run(self) -> None:
        pass
