from __future__ import annotations
from collections import defaultdict

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union

from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from trust_management.data_models.transaction.data_models.trust_transaction import Transaction
    


class ITransactionUpdate(ABC):
    
    @abstractmethod 
    def update(self, transaction : Transaction):
        pass