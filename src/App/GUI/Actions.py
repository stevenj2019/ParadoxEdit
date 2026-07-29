from dataclasses import dataclass
from typing import Callable, List, TypeAlias


@dataclass
class Action:
    text: str
    callback: Callable
    enabled: bool

@dataclass 
class ActionGroup:
    text: str
    actions:List[Action]

@dataclass 
class ActionSubMenu:
    text: str
    actions:List[Action]

ActionsResult: TypeAlias = list[Action|ActionGroup|ActionSubMenu]