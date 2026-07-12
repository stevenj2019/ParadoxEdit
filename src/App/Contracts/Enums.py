from enum import Enum, auto

class SaveTarget(Enum):
    ALL = auto()
    OPEN = auto()

class PropagationType(Enum):
    NODE = auto()
    FILE = auto()

class ChangeState(Enum):
    CLEAN = auto()
    MODIFIED = auto()
    ADDED = auto()
    DELETED = auto()
