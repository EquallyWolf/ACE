from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Output(ABC):
    prefix: str = None

    @abstractmethod
    def broadcast(self, message: str) -> None:
        pass


class CommandLineOutput(Output):
    def broadcast(self, message: str) -> None:
        if self.prefix:
            print(f"{self.prefix}: {message}")
        else:
            print(message)
