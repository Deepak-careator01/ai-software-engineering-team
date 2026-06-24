from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def run(self, input: dict) -> dict:
        pass
