from enum import Enum, auto


class TransactionExchangeScheme(Enum):
    NO_TRANSACTION_EXCHANGE = auto()
    ONLY_DIRECT_TRANSACTION_EXCHANGE = auto()
    ONLY_DIRECT_TRANSACTION_AND_DIRECT_RECOMMENDATION_EXCHANGE = auto()
    ALL_TRANSACTION_EXCHANGE = auto()