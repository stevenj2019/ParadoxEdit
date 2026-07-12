from PyQt5.QtCore import Qt
from enum import Enum, auto, IntEnum

class QtStorage(IntEnum):
    def _generate_next_value_(name, start, count, last_values):
        return Qt.UserRole + count
    READ_ONLY = auto()
    FILE = auto()
    IS_BLOCK = auto()
    IS_COMPARATOR = auto()
    IS_DIRECTORY = auto()
    DIRECTORY = auto()
    NODE = auto()
    STATE = auto()
    CONTEXT = auto()
    PARENT = auto()
    PARENT_CONTEXT = auto()
    INDEX = auto()

class ExpansionMode(Enum):
    ALL = auto()
    DEPTH = auto()
    FROM_NODE = auto()