from enum import Enum, auto

class ExpansionMode(Enum):
    ALL = auto()
    DEPTH = auto()
    FROM_NODE = auto()

class SaveTarget(Enum):
    ALL = auto()
    OPEN = auto()