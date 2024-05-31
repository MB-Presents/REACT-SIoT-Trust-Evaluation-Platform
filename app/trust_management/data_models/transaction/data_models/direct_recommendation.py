from __future__ import annotations

from typing import TYPE_CHECKING


from uuid import UUID


from trust_management.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction

from data.simulation.scenario_constants import Constants as sc

if TYPE_CHECKING:
    from data_models.iot_devices.genric_iot_device import GenericDevice
    from data_models.report_management.report.report import SendingPacket
    from trust_management.data_models.transaction.data_models.trust_transaction import Transaction
    from trust_management.data_models.transaction.status import TransactionStatus
    from trust_management.data_models.transaction.type import TransactionType

from uuid import UUID



class DirectRecommendation(AbstractTransaction):
    def __init__(self, recommender: GenericDevice, recommendee: GenericDevice, recommended_trust_value: float, reporting_time : float, original_transaction_id: UUID, transaction_type: TransactionType,  transaction_status: TransactionStatus, task_context: SendingPacket = None, parent_transaction : Transaction = None, role : TrustVerfierRoles =TrustVerfierRoles.RECOMMENDER, verification_time : float = None):
        
        super().__init__(trustor=recommender, 
                         trustee=recommendee, 
                         trust_value=recommended_trust_value,
                         reporting_time=reporting_time,
                         type=transaction_type,
                         status=transaction_status,
                         task_context=task_context,
                         role=role,
                         verification_time=verification_time)

        self.recommender_quality : float = None
        self.original_transaction_id : UUID = original_transaction_id
        self.parent_transaction : Transaction = parent_transaction

