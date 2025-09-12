from abc import ABC, abstractmethod

from datetime import datetime, timedelta
import random
import string
from typing import Any, Dict, List, Optional


from core.data_alteration.profiles.device_profile_generator import generate_device_profiles
from core.models.devices.common import DeviceBehaviour, DeviceType


class DeviceProfileFacade:
    def __init__(
        self, 
        manufacturer: str,
        model: str,
        firmware_version: str,
        hardware_version: str,
        serial_number: str,
        date_of_manufacture: str,
        last_maintenance_date: Optional[str] = None,
        next_maintenance_date: Optional[str] = None
    ) -> None:
        self._manufacturer: str = manufacturer
        self._model: str = model
        self._affiliations: List[str] = []
        self._firmware_version: str = firmware_version
        self._hardware_version: str = hardware_version
        self._serial_number: str = serial_number
        self._date_of_manufacture: str = date_of_manufacture
        self._last_maintenance_date: Optional[str] = last_maintenance_date
        self._next_maintenance_date: Optional[str] = next_maintenance_date


    def get_device_profile_dict(self) -> dict:
        return {
            'manufacturer': self._manufacturer,
            'model': self._model,
            'affiliations': self._affiliations,
            'firmware_version': self._firmware_version,
            'hardware_version': self._hardware_version,
            'serial_number': self._serial_number,
            'date_of_manufacture': self._date_of_manufacture,
            'last_maintenance_date': self._last_maintenance_date,
            'next_maintenance_date': self._next_maintenance_date
        }

class IDeviceProfile(ABC):
    
    @abstractmethod
    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]={}) -> DeviceProfileFacade:
        pass   





class VehicleProfileFactory(IDeviceProfile):
    
    
    def __init__(self) -> None:
        self.trustworthy_vehicle_profiles, self.untrustworthy_vehicle_profiles = generate_device_profiles('vehicle', 20, 20)
        


    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]={}) -> DeviceProfileFacade:
        
        
        if device_behaviour == DeviceBehaviour.TRUSTWORTHY:
            config = random.choice(self.trustworthy_vehicle_profiles)
        elif device_behaviour == DeviceBehaviour.MALICIOUS:
            config = random.choice(self.untrustworthy_vehicle_profiles)
        
        return DeviceProfileFacade(
            manufacturer=config['manufacturer'],
            model=config['model'],
            firmware_version=config['firmware_version'],
            hardware_version=config['hardware_version'],
            serial_number=config['serial_number'],
            date_of_manufacture=config['manufacture_date'],
            last_maintenance_date=config['last_maintenance_date'],
            next_maintenance_date=config['next_maintenance_date']
        )

class SmartPhoneProfileFactory(IDeviceProfile):
    
    def __init__(self):
        self.trustworthy_smartphone_profiles, self.untrustworthy_smartphone_profiles = generate_device_profiles('smartphone', 20, 20)
        self.profile_counter = 0

    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]={}) -> DeviceProfileFacade:
        if device_behaviour == DeviceBehaviour.TRUSTWORTHY:            
            config = random.choice(self.trustworthy_smartphone_profiles)
        elif device_behaviour == DeviceBehaviour.MALICIOUS:
            config = random.choice(self.untrustworthy_smartphone_profiles)
            self.profile_counter = (self.profile_counter + 1) % len(self.untrustworthy_smartphone_profiles)
        return DeviceProfileFacade(
            manufacturer=config['manufacturer'],
            model=config['model'],
            firmware_version=config['firmware_version'],
            hardware_version=config['hardware_version'],
            serial_number=config['serial_number'],
            date_of_manufacture=config['manufacture_date'],
            last_maintenance_date=config['last_maintenance_date'],
            next_maintenance_date=config['next_maintenance_date']
        )

class EmergencyResponseCenterProfileFactory(IDeviceProfile):
    
    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]={}) -> DeviceProfileFacade:

        return DeviceProfileFacade(
            manufacturer='Motorola Solutions',
            model='Motorola Center 1',
            firmware_version='1.0.0',
            hardware_version='1.0.0',
            serial_number='123456789',
            date_of_manufacture='2020-01-01',
            last_maintenance_date='2020-01-01',
            next_maintenance_date='2020-01-01',
        )
        
class InductionLoopProfileFactory(IDeviceProfile):
    
    def __init__(self):
        pass
    
    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]) -> DeviceProfileFacade:
        
            
        return DeviceProfileFacade(
            manufacturer=config['manufacturer'], 
                                      model=config['model'], 
                                      firmware_version=config['firmware_version'], 
                                      hardware_version=config['hardware_version'], 
                                      serial_number=config['serial_number'], 
                                      date_of_manufacture=config['date_of_manufacture'], 
                                      last_maintenance_date=config['last_maintenance_date'],
                                      next_maintenance_date=config['next_maintenance_date']
        )

class TrafficCameraProfileFactory(IDeviceProfile):

    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]={}) -> DeviceProfileFacade:


        # Generate random values for static fields
        manufacturer = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        model = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        firmware_version = 'v' + '.'.join(str(random.randint(1, 9)) for _ in range(3))
        hardware_version = 'HW' + ''.join(str(random.randint(0, 9)) for _ in range(3))
        serial_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

        time = datetime.now()
        
        date_of_manufacture = (time - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d')
        last_maintenance_date = (time - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')
        next_maintenance_date = (time + timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')

        return DeviceProfileFacade(
            manufacturer=manufacturer,
            model=model,
            firmware_version=firmware_version,
            hardware_version=hardware_version,
            serial_number=serial_number,
            date_of_manufacture=date_of_manufacture,
            last_maintenance_date=last_maintenance_date,
            next_maintenance_date=next_maintenance_date
        )
        
class TrafficLightProfileFactory(IDeviceProfile):

    def get_device_profile(self, device_behaviour : DeviceBehaviour, config : Dict[str,Any]={}) -> DeviceProfileFacade:

        return DeviceProfileFacade(
            manufacturer=config['manufacturer'],
            model=config['model'],
            firmware_version=config['firmware_version'],
            hardware_version=config['hardware_version'],
            serial_number=config['serial_number'],  
            date_of_manufacture=config['manufacture_date'],  
            last_maintenance_date=config['last_maintenance_date'],
            next_maintenance_date=config['next_maintenance_date'],  
        )


        
        
    
class DeviceProfileFactory:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceProfileFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.device_profile_factory : Dict[DeviceType, IDeviceProfile] = {
                DeviceType.TRAFFIC_CAMERA: TrafficCameraProfileFactory(),
                DeviceType.INDUCTION_LOOP: InductionLoopProfileFactory(),
                DeviceType.EMERGENCY_CENTER: EmergencyResponseCenterProfileFactory(),
                DeviceType.SMART_PHONE: SmartPhoneProfileFactory(),
                DeviceType.VEHICLE: VehicleProfileFactory(),
                DeviceType.TRAFFIC_LIGHT: TrafficLightProfileFactory()
            }
            DeviceProfileFactory._initialized = True

    def get_profile(self, device_type: DeviceType, device_behaviour: DeviceBehaviour, config: Dict[str,Any]={}) -> DeviceProfileFacade:

        assert device_type in self.device_profile_factory, f"Unknown device type: {device_type}"
        factory : IDeviceProfile = self.device_profile_factory[device_type]
        if factory:
            return factory.get_device_profile(device_behaviour, config)
        raise ValueError(f"Unknown device type: {device_type}")