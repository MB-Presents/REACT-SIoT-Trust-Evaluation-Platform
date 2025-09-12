from __future__ import annotations
from collections import defaultdict

from typing import TYPE_CHECKING, List, Tuple, Union

from copy import copy
from typing import Dict
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

from uuid import UUID


from core.simulation.logging import ObjectType
from trust.data_models.TrustVerifierRoles import TrustVerfierRoles


from trust.data_models.transaction.context import TransactionContext
from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.data_models.transaction.status import TransactionStatus
from trust.data_models.transaction.transaction_manager import TransactionManager
from trust.data_models.transaction.type import TransactionType
from trust.settings import TrustManagementSettings

import utils.logging as logger
import itertools

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from trust.data_models.relationship.relationship_controller import RelationshipController
    from core.models.uniform.components.report import SendingPacket
    from core.models.events.simulation_events import SimulationEventManager
    from trust.data_models.reputation.reputation_controller import ReputationController

from uuid import UUID


    
class Transaction(AbstractTransaction):
    
    def __init__(self, trustor: GenericDevice, trustee: GenericDevice, trust_value: float, reporting_time : float = None, task_context: SendingPacket = None, parent_transaction : Transaction = None, role : TrustVerfierRoles = None):
        super().__init__(trustor, trustee, trust_value, reporting_time, TransactionType.DIRECT_TRANSACTION, TransactionStatus.PENDING, task_context, role)
        self.parent_transaction : Transaction = parent_transaction


