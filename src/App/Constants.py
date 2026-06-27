from PyQt5.QtCore import Qt
from enum import Enum, auto

class ChangeState(Enum):
    CLEAN = auto()
    MODIFIED = auto()
    ADDED = auto()
    DELETED = auto()

FILE = Qt.UserRole
NODE = Qt.UserRole + 1
IS_BLOCK = Qt.UserRole + 2
STATE = Qt.UserRole + 3
CATEGORY = Qt.UserRole + 4
IS_CATEGORY = Qt.UserRole + 5