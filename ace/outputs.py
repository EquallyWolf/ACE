from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Output(ABC):
    prefix: str = None


class CommandLineOutput(Output):
    pass
