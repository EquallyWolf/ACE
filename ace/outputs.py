from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Output(ABC):
    prefix: str = None


class CommandLineOutput:
    def __init__(self, prefix: str = None):
        self.prefix = prefix
