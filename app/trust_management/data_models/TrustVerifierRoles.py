from enum import Enum, auto


class TrustVerfierRoles(Enum):
    REPORTER = auto()
    SERVICE_PROVIDER = auto()
    RECOMMENDER = auto()