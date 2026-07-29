from enum import Enum, IntEnum, auto

from PyQt5.QtCore import Qt


class QtStorage(IntEnum):
    def _generate_next_value_(name:str, start:int, count:int, last_values:list[int]) -> int:
        return Qt.UserRole + count
    READ_ONLY = auto()
    IS_BLOCK = auto()
    IS_COMPARATOR = auto()
    IS_DIRECTORY = auto()
    DIRECTORY = auto()
    FILE = auto()
    NODE = auto()
    STATE = auto()
    CONTEXT = auto()
    PARENT = auto()
    PARENT_CONTEXT = auto()
    INDEX = auto()
    EDITABLE = auto()

class ExpansionMode(Enum):
    ALL = auto()
    DEPTH = auto()
    FROM_NODE = auto()