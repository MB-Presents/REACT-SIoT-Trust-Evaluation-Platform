# from __future__ import annotations
# from typing import TYPE_CHECKING


# from core.models.reports.components.report import SendingPacket



# from trust.data_models.relationship.relationship_controller import RelationshipController
# from trust.data_models.reputation.reputation_controller import ReputationController
# from trust.data_models.transaction.transaction_controller import  TransactionController
# from trust.data_models.trust_manager import TrustManager
# from trust.settings import TrustManagementSettings


# if TYPE_CHECKING:
#     from core.models.properties.properties import GenericProperty


#     from core.models.devices.smart_phone import SmartPhone
#     from core.models.devices.vehicle import Vehicle
#     from core.models.devices.device_handler import DevicesGroupHandler



# # class TrustManagementFacade:
# #     def __init__(self):
        
        

        
        
        
    
#     # def update_request_status(self, request: SendingPacket) -> None:
#     #     self.trust_manager.update_request_status(request)
    
#     # def get_trust_data(self) -> dict:
#     #     """Extract trust-related data for serialization."""
#     #     return {
#     #         'trustworthy_devices': self.trust_manager.relationship_controller.relationship_manager.get_trustworthy_devices(),
#     #         'untrustworthy_devices': self.trust_manager.relationship_controller.relationship_manager.get_untrustworthy_devices(),
#     #         'num_untrustworthy_relationships': self.trust_manager.relationship_controller.relationship_manager.get_num_untrustworthy_relationships(),
#     #         'num_trustworthy_relationships': self.trust_manager.relationship_controller.relationship_manager.get_num_trustworthy_relationships(),
#     #         'num_related_devices': self.trust_manager.relationship_controller.relationship_manager.get_num_relationships(),
#     #         'num_trust_transactions': self.trust_manager.trust_transaction_controller.transaction_manager.get_num_transactions(),
#     #     }