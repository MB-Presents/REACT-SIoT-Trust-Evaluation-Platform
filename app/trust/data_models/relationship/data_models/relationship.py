from __future__ import annotations

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, List


if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    from trust.data_models.relationship.context import RelationshipContext

class Relationship:
    def __init__(self, trustor: str, trustee : str, trust_value: float = 0, relationship_context : RelationshipContext = None):
    
        self.trustor : GenericDevice = trustor
        self.trustee : GenericDevice = trustee
        self.trust_value : float = trust_value
        
        self.context : RelationshipContext = relationship_context
        

        
        

        