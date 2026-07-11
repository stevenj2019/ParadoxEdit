from PyQt5.QtCore import Qt
from enum import Enum, auto, IntEnum

class QtStorage(IntEnum):
    def _generate_next_value_(name, start, count, last_values):
        return Qt.UserRole + count
    FILE = auto()
    IS_BLOCK = auto()
    IS_COMPARATOR = auto()
    IS_CATEGORY = auto()
    CATEGORY = auto()
    NODE = auto()
    STATE = auto()
    CONTEXT = auto()
    PARENT = auto()
    PARENT_CONTEXT = auto()
    INDEX = auto()
    
class PDXTokens(Enum):
    ANY = auto()
    CHARACTER = auto()
    COUNTRY = auto()
    ORGANISATION = auto()
    OPERATION = auto()
    CONTRACTS = auto()
    RAID = auto()
    SPECIAL_PROJECT = auto()
    STATE = auto()
    STRATEGIC_REGION = auto()

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
