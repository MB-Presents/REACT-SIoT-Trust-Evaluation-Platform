from enum import Enum, auto

class TransactionType(Enum):
    DIRECT_TRANSACTION = auto()
    DIRECT_RECOMMENDATION = auto()
    INDIRECT_RECOMMENDATION = auto()