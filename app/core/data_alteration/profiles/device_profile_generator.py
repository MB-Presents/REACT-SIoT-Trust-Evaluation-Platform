import random
import json
from typing import Tuple, List, Dict

from scenarios.canberra_case_study.simulation.mock_data import DEVICE_PROFILES, AFFILIATIONS

def generate_device_profiles(device_type: str, num_trustworthy: int, num_untrustworthy: int) -> Tuple[List[Dict], List[Dict]]:
    """Generate unique trustworthy and untrustworthy device profiles."""
    trustworthy_profiles = []
    untrustworthy_profiles = []
    all_profiles = set()



    manufacturers = list(DEVICE_PROFILES[device_type].keys())
    models = {man: list(DEVICE_PROFILES[device_type][man]) for man in manufacturers}

    while len(trustworthy_profiles) < num_trustworthy:
        profile = create_profile(manufacturers, models)
        profile_key = json.dumps(profile, sort_keys=True)
        if profile_key not in all_profiles:
            all_profiles.add(profile_key)
            trustworthy_profiles.append(profile)

    while len(untrustworthy_profiles) < num_untrustworthy:
        profile = create_profile(manufacturers, models)
        profile_key = json.dumps(profile, sort_keys=True)
        if profile_key not in all_profiles:
            all_profiles.add(profile_key)
            untrustworthy_profiles.append(profile)

    return trustworthy_profiles, untrustworthy_profiles

def create_profile(manufacturers: List[str], models: Dict[str, List[str]]) -> Dict:
    """Create a single device profile with randomized attributes."""
    manufacturer = random.choice(manufacturers)
    model = random.choice(models[manufacturer])
    
    details = {
        'firmware_version': f"{random.randint(1, 2)}.{random.randint(0, 1)}.{random.randint(0, 1)}",
        'hardware_version': f"{random.randint(1, 2)}.{random.randint(0, 1)}",
        'manufacture_date': f"20{random.randint(15, 22)}-01-01",
    }
    
    return {
        'manufacturer': manufacturer,
        'model': model,
        'firmware_version': details['firmware_version'],
        'hardware_version': details['hardware_version'],
        'manufacture_date': details['manufacture_date'],
        'serial_number': f"{random.randint(1000000000000000, 9999999999999999)}",
        'last_maintenance_date': f"20{random.randint(15, 22)}-01-01",
        'next_maintenance_date': f"20{random.randint(15, 22)}-01-01",
        'affiliation': random.choice(AFFILIATIONS)
    }