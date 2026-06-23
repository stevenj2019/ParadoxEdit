from dataclasses import dataclass
from typing import Callable

@dataclass
class Action:
    text: str
    callback: Callable
    enabled: bool

@dataclass
class NodeUIConfig:
    label: str
    editor: Callable