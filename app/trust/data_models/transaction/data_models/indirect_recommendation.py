from __future__ import annotations

from typing import TYPE_CHECKING


from uuid import UUID


from trust.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.data_models.transaction.data_models.direct_recommendation import DirectRecommendation



if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.data_models.transaction.data_models.trust_transaction import Transaction
    from trust.data_models.transaction.status import TransactionStatus
    from trust.data_models.transaction.type import TransactionType

from uuid import UUID



class IndirectRecommendation(DirectRecommendation):
    def __init__(self, recommender: GenericDevice, recommended_trust_subject: GenericDevice, recommended_trust_value: float, reporting_time: float, original_transaction_id: UUID, transaction_type: TransactionType,  transaction_status: TransactionStatus, task_context: SendingPacket = None, parent_transaction : DirectRecommendation = None, verification_time : float = None):
        
        super().__init__(recommender=recommender,
                         recommendee=recommended_trust_subject, 
                         recommended_trust_value=recommended_trust_value,
                         reporting_time=reporting_time,
                         original_transaction_id=original_transaction_id,
                         transaction_type=transaction_type,
                         transaction_status=transaction_status,
                         task_context=task_context,
                         parent_transaction=parent_transaction,
                         role=TrustVerfierRoles.RECOMMENDER,
                         verification_time=verification_time)


