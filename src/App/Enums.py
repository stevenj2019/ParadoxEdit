from PyQt5.QtCore import Qt
from enum import Enum, auto, IntEnum
    
class PDXTokens(Enum):
    EVENT = auto()
    CHARACTER = auto()
    COUNTRY = auto()
    ORGANISATION = auto()
    OPERATION = auto()
    CONTRACTS = auto()
    RAID = auto()
    SPECIAL_PROJECT = auto()
    STATE = auto()
    STRATEGIC_REGION = auto()

class PDXMetadata(Enum):
    GFXIcon = auto()
    LocKey = auto()