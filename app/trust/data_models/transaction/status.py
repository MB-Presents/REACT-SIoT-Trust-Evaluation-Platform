from enum import Enum, auto

class TransactionStatus(Enum):
    PENDING = auto()
    VERIFIED = auto()
    EXPIRED = auto()