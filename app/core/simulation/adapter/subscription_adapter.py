from typing import Any, Dict, List, Tuple
from sympy import pde_separate_add
import traci
import traci.constants as tc


class SubscriptionAdapter:
    def get_departed_vehicles(self) -> List[str]:
        """Get IDs of vehicles that have departed in the current simulation step."""
        departed_id_list = traci.simulation.getDepartedIDList()
        assert isinstance(departed_id_list, list)
        return departed_id_list

    def get_departed_persons(self) -> List[str]:
        """Get IDs of persons that have departed in the current simulation step."""
        departed_person_id_list = traci.simulation.getDepartedPersonIDList()
        assert isinstance(departed_person_id_list, list)
        return departed_person_id_list

    def subscribe_vehicle(self, vehicle_id: str, features: List[int]) -> None:
        """Subscribe a vehicle to specified features."""
        traci.vehicle.subscribe(vehicle_id, features)

    def subscribe_person(self, person_id: str, features: List[int]) -> None:
        """Subscribe a person to specified features."""
        traci.person.subscribe(person_id, features)

    def unsubscribe_vehicle(self, vehicle_id: str) -> None:
        """Unsubscribe a vehicle from all features."""
        traci.vehicle.unsubscribe(vehicle_id)

    def unsubscribe_person(self, person_id: str) -> None:
        """Unsubscribe a person from all features."""
        traci.person.unsubscribe(person_id)
        
        
    def subscribe_traffic_light(self, tls_id: str, features: List[int]) -> None:
        traci.trafficlight.subscribe(tls_id, features)

    def unsubscribe_traffic_light(self, tls_id: str) -> None:
        traci.trafficlight.unsubscribe(tls_id)


    def subscribe_simulation(self) -> None:
        traci.simulation.subscribe()
        
    def get_pedestrian_subscriptition_result(self) -> Dict[str, Dict[int,Any]]:
        pedestrian_data = traci.person.getAllSubscriptionResults()
        return pedestrian_data

    def get_bicyclist_subscription_result(self) -> Dict[str, Dict[int,Any]]:
        
        vehicle_data = traci.vehicle.getAllSubscriptionResults()

        bicycle_data = {veh_id: bicycle for veh_id, bicycle in vehicle_data.items() if bicycle[tc.VAR_VEHICLECLASS] == 'bicycle'}

        return bicycle_data


    def get_vehicle_subscription_result(self) -> Dict[str, Dict[int,Any]]:
        vehicles = traci.vehicle.getAllSubscriptionResults()
        return vehicles

        # existing_vehicles = {veh_id: vehicle for veh_id, vehicle in vehicles.items() if vehicle[tc.VAR_VEHICLECLASS] != 'bicycle'}

        # current_vehicle_ids = list(derevices.keys())
        # nonexistent_vehicle_ids = [
        #     veh_id for veh_id in current_vehicle_ids
        #     if veh_id not in vehicle_ids_in_simulation or devices[veh_id]._vehicle_type in ['bike_bicycle', 'ped_pedestrian']
        # ]
        # for veh_id in nonexistent_vehicle_ids:
        #     del devices[veh_id]
        # return {
        #     veh_id: vehicle for veh_id, vehicle in vehicle_in_simulation.items()
        #     if vehicle[tc.VAR_VEHICLECLASS] not in ['bicycle', 'ped_pedestrian']
        # }
        
        
          
          
          
          