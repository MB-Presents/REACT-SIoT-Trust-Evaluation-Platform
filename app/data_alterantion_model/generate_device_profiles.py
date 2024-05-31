import random
import json
# import data.simulation.dummy_data as data_templates
import data.simulation.dummy_data as data_templates

def generate_profiles(device_type, num_trustworthy, num_untrustworthy):
    trustworthy_profiles = []
    untrustworthy_profiles = []
    
    all_profiles = set()

    manufacturers = []
    models = {}
    model_details = {}
    
    
    manufacturers = list(data_templates.device_profiles[device_type].keys())
    for manufacturer in manufacturers:
        models[manufacturer] = list(data_templates.device_profiles[device_type][manufacturer])


    while len(trustworthy_profiles) < num_trustworthy:
        profile_dict = generate_profile(manufacturers, models)
        profile_str = json.dumps(profile_dict, sort_keys=True)
        
        if profile_str not in all_profiles:
            all_profiles.add(profile_str)
            trustworthy_profiles.append(profile_dict)

    while len(untrustworthy_profiles) < num_untrustworthy:
        profile_dict = generate_profile(manufacturers, models)
        profile_str = json.dumps(profile_dict, sort_keys=True)
        
        if profile_str not in all_profiles:
            all_profiles.add(profile_str)
            untrustworthy_profiles.append(profile_dict)

    return trustworthy_profiles, untrustworthy_profiles


def generate_profile(manufacturers, models):
    manufacturer = random.choice(manufacturers)
    model = random.choice(models[manufacturer])
    details = {
        'firmware_version': f"{random.randint(1, 2)}.{random.randint(0, 1)}.{random.randint(0, 1)}",
        'hardware_version': f"{random.randint(1, 2)}.{random.randint(0, 1)}",
        'manufacture_date': f"20{random.randint(15, 22)}-01-01",
    }
    
    profile = {
        'manufacturer': manufacturer,
        'model': model,
        'firmware_version': details['firmware_version'],
        'hardware_version': details['hardware_version'],
        'manufacture_date': details['manufacture_date'],
        'serial_number': f"{random.randint(1000000000000000, 9999999999999999)}",
        'last_maintenance_date': f"20{random.randint(15, 22)}-01-01",
        'next_maintenance_date': f"20{random.randint(15, 22)}-01-01",
        'affiliation': random.choice(data_templates.affiliations)
    }
    
    return profile
