from PyQt5.QtCore import Qt
from enum import Enum, auto, IntEnum

class QtStorage(IntEnum):
    def _generate_next_value_(name, start, count, last_values):
        return Qt.UserRole + count
    FILE = auto()
    NODE = auto()
    IS_BLOCK = auto()
    STATE = auto()
    CATEGORY = auto()
    IS_CATEGORY = auto()
    CONTEXT = auto()
    PARENT = auto()
    PARENT_CONTEXT = auto()
    INDEX = auto()
    
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
