from __future__ import annotations

from typing import TYPE_CHECKING

from copy import copy
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters
from trust.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust.data_models.transaction.context import TransactionContext


import itertools


if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.data_models.transaction.status import TransactionStatus
    from trust.data_models.transaction.type import TransactionType


class AbstractTransaction:
    
    id_iter = itertools.count()

    def __init__(self, trustor: GenericDevice, trustee: GenericDevice, trust_value: float, reporting_time : float, type: TransactionType, status: TransactionStatus, task_context: SendingPacket = None, role : TrustVerfierRoles = None, verification_time : float = None):
        self._id : int = next(self.id_iter)
        self.trustor: GenericDevice = trustor
        self.trustee: GenericDevice = trustee
        

        self.transaction_context: TransactionContext = self.get_transaction_context(trustor, trustee)
        self.trust_value: float = trust_value
        self.reporting_time: float = copy(reporting_time)
        self.verification_time: float = verification_time
    
        self.type : TransactionType= type
        self.status : TransactionStatus= status
        self.task_context : SendingPacket = task_context
        self.role : TrustVerfierRoles = role
    
    def get_transaction_context(self, trustor: GenericDevice, trustee: GenericDevice):
        transaction_context = TransactionContext()
        transaction_context.creation_time = copy(ScenarioParameters.TIME)
        transaction_context.trustor_location = copy(trustor._position)
        transaction_context.trustee_location = copy(trustee._position)
        return transaction_context
    
    
    def to_dict(self, last_trust_value : float = None, last_verified_transaction_trust_value : float = None, last_verified_transaction_id : int = None, last_transaction_id : int = None, parent_transaction_id : int = None, interaction_frequency : int = None, degree_of_trustworthiness : float = None):
        
        
        
        trustor = self.trustor
        trustee = self.trustee
        transaction = self
        
        interaction_frequency = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transaction_frequency(transaction.trustor._id, transaction.trustee._id)
        degree_of_trustworthiness = trustor.trust_manager.trust_transaction_controller.get_friendship_similarity_by_transaction(transaction)

        last_transaction_id, last_trust_value = trustor.trust_manager.trust_transaction_controller.get_last_transaction_of_trustee(transaction.trustee._id)
        last_verified_transaction_id, last_verified_transaction_trust_value = trustor.trust_manager.trust_transaction_controller.get_last_verified_transaction(transaction.trustee._id)
        
        
        
        try:
            transaction_dict = {
                'transaction_id' : self._id,
                'transaction_type' : self.type.name,
                'trustor' : self.trustor._id,
                'trustee' : self.trustee._id,
                'time': self.transaction_context.creation_time,
                'trustor_location' : self.transaction_context.trustor_location,
                'trustee_location' : self.transaction_context.trustee_location,
                'trust_value' : self.trust_value,
                'status' : self.status.name,
                'task_context': self.task_context.request_type.name,
                'trustworthiness' : self.trustee._behaviour.name,
                'role' : self.role.name,
                'last_trust_value' : last_trust_value,
                'last_verified_transaction_trust_value' : last_verified_transaction_trust_value,
                'last_verified_transaction_id' : last_verified_transaction_id,
                'last_transaction_id' : last_transaction_id,
                'parent_transaction_id' : parent_transaction_id,
                'interaction_frequency' : interaction_frequency,
                'degree_of_common_friendship' : degree_of_trustworthiness,
                'reporting_time' : self.reporting_time,
                'verification_time' : self.verification_time,
                'report_trustworthiness' : self.task_context.simulation_event.is_authentic,
            }
            
            
            return transaction_dict
        
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)
