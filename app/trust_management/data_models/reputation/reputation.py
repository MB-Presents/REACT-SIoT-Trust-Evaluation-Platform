


from enum import Enum, auto


class ReputationScope(Enum):
    GLOBAL = auto()
    LOCAL = auto()
    NO_REPUTATION_SCORE = auto()


class ReputationContextSettings(Enum):
    NO_CONTEXT = auto()
    TASK_CONTEXT = auto()
    

class ReputationComputationStrategy(Enum):
    AVERAEG_OF_LAST_N_TRANSACTIONS = auto()
    ALL_TRANSACTIONS = auto()
    ONLY_DIRECT_TRANSACTIONS = auto()
    ALL_TRANSACTIONS_IN_TIME_RANGE = auto()
    LAST_N_TRANSACTIONS_IN_TIME_RANGE = auto()
    LAST_N_TRANSACTIONS_IN_TIME_RANGE_EXPONENTIAL_DECAY = auto()
    