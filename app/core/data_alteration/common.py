from enum import Enum, auto

class AlterationType(Enum):
    STATIC = auto()
    DYNAMIC = auto()

class SignificanceLevel(Enum):
    SLIGHT = auto()
    SIGNIFICANT = auto()
    SELECTIVE = auto()
    TRUE = auto()