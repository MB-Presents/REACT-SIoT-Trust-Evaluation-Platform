from __future__ import annotations
# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union

from typing import List, Dict, Tuple

from core.models.devices.factories.behaviour_factory import DeviceBehaviorProfile, DeviceBehaviourFactory
from core.models.devices.factories.computation_factory import ComputationCapabilityFactory
from core.models.devices.factories.device_profile_facade import DeviceProfileFacade, DeviceProfileFactory
from core.models.devices.factories.id_generator import DeviceIDGenerator
from core.models.devices.factories.service_factory import ServiceFactory
from core.models.interfaces.device import IDevice
from core.models.interfaces.service import IService
from core.models.uniform.components.report import SendingPacket
from core.models.devices.common import DeviceBehaviour, DeviceComputationCapabilityClass, DeviceInternalStatus, DeviceShapeStatus, Service



from core.models.devices.common import DeviceType
from core.simulation.simulation_context import SimulationContext
from trust.data_models.relationship.relationship_controller import RelationshipController
from trust.data_models.reputation.reputation_controller import ReputationController
from trust.data_models.transaction.transaction_controller import TransactionController
from trust.data_models.trust_manager import TrustManager
from trust.data_models.trust_manager import TrustManager
from trust.settings import TrustManagementSettings


if TYPE_CHECKING:
    from core.models.properties.properties import GenericProperty
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle





class GenericDevice(IDevice):

    def __init__(self, 
                 device_id: str, 
                 device_type: DeviceType, 
                 color: Optional[Tuple[float, float, float]] = None,
                 device_behaviour : DeviceBehaviour = DeviceBehaviour.TRUSTWORTHY,
                 profile_config : Dict[Any,Any] = {},
                 simulation_context : Optional[SimulationContext]= None): # Uncomment last parameter if needed
        
        
        self._id : str = device_id
        self._device_map_id : int = DeviceIDGenerator().get_next_id()
        
        self._type : DeviceType = device_type
        self._position : Optional[Tuple[float,float]] = None
        self._color : Tuple[float, float, float] = color if color else (255, 0, 0)
        self._speed : float = 0.0
        self._internal_status : DeviceInternalStatus = DeviceInternalStatus.ACTIVE
        self._shape_status : DeviceShapeStatus = DeviceShapeStatus.ORIGINAL_MANUFACTURED
        self._device_behaviour : DeviceBehaviour = device_behaviour
        self._alternated_device_data : Optional[Union[Vehicle,SmartPhone]] = None
        self._properties : Dict[str, GenericProperty] = {}


        self._services : Dict[Service, IService] = {}
        self._simulation_context : Optional[SimulationContext] = simulation_context
        
        self._computation_capability_class :DeviceComputationCapabilityClass
        self._device_behavior_profile : DeviceBehaviorProfile
        self._device_profile_facade : DeviceProfileFacade
        self.relationship_controller : RelationshipController
        self.transaction_controller : TransactionController 
        self.reputation_controller : ReputationController 
        self.trust_manager : TrustManager 
        



        # self._computation_capability_class : DeviceComputationCapabilityClass = ComputationCapabilityFactory().create(device_type=self._type)
        # self._services : Dict[Service, IService] = ServiceFactory().get_services(device=self)
        
        # self._device_behavior_profile : DeviceBehaviorProfile = DeviceBehaviourFactory().create(device_behaviour)
        # self._device_profile_facade : DeviceProfileFacade = DeviceProfileFactory().get_profile(device_type, self._device_behavior_profile._ground_truth, config=profile_config)

        # self.relationship_controller : RelationshipController = RelationshipController()
        # self.transaction_controller : TransactionController = TransactionController()
        # self.reputation_controller : ReputationController = ReputationController(
        #     self.transaction_controller,
        #     TrustManagementSettings.REPUTATION_CONTEXT,
        #     TrustManagementSettings.REPUTATION_SCOPE,
        #     TrustManagementSettings.REPUTATION_COMPUTATION_STRATEGY
        # )
        
        # self.trust_manager : TrustManager = TrustManager(self.relationship_controller, self.transaction_controller, self.reputation_controller)
        
    def initialize_dependencies(self):
        """Initialize dependencies using simulation context (called by builder)"""
        if not self._simulation_context:
            return
            
        try:
            # Initialize factories through context
            comp_factory = self._simulation_context.get_computation_capability_factory()
            self._computation_capability_class = comp_factory.create(device_type=self._type)
            
            behaviour_factory = self._simulation_context.get_device_behaviour_factory()
            self._device_behavior_profile = behaviour_factory.create(self._device_behaviour)
            
            profile_factory = self._simulation_context.get_device_profile_factory()
            self._device_profile_facade = profile_factory.get_profile(
                self._type, 
                self._device_behavior_profile._ground_truth, 
                config=self._properties
            )
            
            # Initialize trust management
            self.relationship_controller = RelationshipController()
            self.transaction_controller = TransactionController()
            self.reputation_controller = ReputationController(
                self.transaction_controller,
                TrustManagementSettings.REPUTATION_CONTEXT,
                TrustManagementSettings.REPUTATION_SCOPE,
                TrustManagementSettings.REPUTATION_COMPUTATION_STRATEGY
            )
            self.trust_manager = TrustManager(
                self.relationship_controller, 
                self.transaction_controller, 
                self.reputation_controller
            )
            
        except Exception as e:
            print(f"Warning: Could not initialize all dependencies for {self._id}: {e}")
        

    def with_position(self, position : Tuple[float, float]) -> GenericDevice:
        self._position = (position[0], position[1]) 
        return self
    
    def with_type(self, device_type : DeviceType) -> GenericDevice:
        self._type = device_type
        return self
    
    def with_color(self, color : Tuple[float, float, float]) -> GenericDevice:
        self._color = color
        return self

    def with_services(self, services : Dict[Service, IService]) -> GenericDevice:
        self._services = services
        return self
    
    def get_device_id(self) -> str:
        return self._id
    
    def get_device_type(self) -> DeviceType:
        return self._type
    
    def update_position(self, position: List[float]) -> None:
        self._position = (position[0], position[1]) if position else None
    
    def get_position(self) -> List[float]:
        return list(self._position) if self._position else []
    
    def set_property(self, key: str, value: Any) -> 'GenericDevice':
        """Set a device property"""
        self._properties[key] = value
        return self
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a device property"""
        return self._properties.get(key, default)
    

    
    def update_request_status(self, request : SendingPacket):
        assert self.trust_manager, "Trust manager is not initialized"
        self.trust_manager.update_request_status(request)        
    
    def update_status(self, status : DeviceInternalStatus):
        self._internal_status = status
    
    def get_status(self) -> DeviceInternalStatus:  
        return self._internal_status

    
    def to_dict(self) -> Dict[str, Any]:
        assert self.trust_manager, "Trust manager is not initialized"
        assert self._device_profile_facade, "Device profile facade is not initialized"
        trust_management = self.trust_manager.get_trust_data()
        device_profile = self._device_profile_facade.get_device_profile_dict()
        
        assert not isinstance(trust_management, dict), f"Expected trust_management to be a dict, got {type(trust_management)}"
        assert not isinstance(device_profile, dict), f"Expected device_profile to be a dict, got {type(device_profile)}"

        assert self._computation_capability_class is not None, "Computation capability class is not initialized"
        assert self._device_behavior_profile is not None, "Device behavior profile is not initialized"

        device_dict = {
            'device_id': self._id,
            'type': self._type.name if self._type else None,
            'position': self._position,
            'color': self._color,
            'speed': self._speed,
            'status': self._internal_status.name if self._internal_status else None,
            'shape_status': self._shape_status.name if self._shape_status else None,
            'computation_capability' : self._computation_capability_class.name,
            'device_behaviour' : self._device_behavior_profile._ground_truth,
        }
        
        device_dict.update(device_profile)
        device_dict.update(trust_management)

        assert not isinstance(device_dict, dict), f"Expected device_dict to be a dict, got {type(device_dict)}"
        

        return device_dict
            




