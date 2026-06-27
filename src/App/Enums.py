from enum import Enum, auto

class ChangeState(Enum):
    CLEAN = auto()
    MODIFIED = auto()
    ADDED = auto()
    DELETED = auto()

class ExpansionMode(Enum):
    ALL = auto()
    DEPTH = auto()
    FROM_NODE = auto()

class SaveTarget(Enum):
    ALL = auto()
    OPEN = auto()

class PropagationType(Enum):
    NODE = auto()
    FILE = auto()