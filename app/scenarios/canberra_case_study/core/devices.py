




from typing import Any, Dict, List


INDUCTION_SENSOR_SPECIFICATION : List[Dict[str, Any]] = [
    {
        'id':'induction_loop_1',
        'edgeID':'673118337',
        'position':[796.67,216.25,787.59,221.86 ],
        'induction_position':100,
        'manufacturer': 'Manufacturer1',
        'model': 'Model1',
        'firmware_version': '1.0.0',
        'hardware_version': '1.0',
        'serial_number': '12345',
        'date_of_manufacture': '2022-01-01',
        'last_maintenance_date': '2023-01-01',
        'next_maintenance_date': '2023-07-01',
        'color': (0,0,225,255)
    }
]



TRAFFIC_CAMERA_SPECIFICATION : List[Dict[str, Any]]= [
    {
        'edgeID': ['668452809', '668452814'],
        'position': [577.69, 866.63],
                'x': -35.279528,
        'y': 149.128568,
        'color' : (105,105,105, 255)
    },
    {
        'edgeID': ['489692411#1', '668468055'],
        'position': [703.90, 850.16],
                'x': -35.279616,
        'y': 149.129465,
        'color' : (105,105,105, 255)
    },
    {
        'edgeID': ['307292406', '138708547'],
        'position': [560.31, 272.15],
                'x': -35.283972,
        'y': 149.128353,
        'color' : (105,105,105, 255)
    },
    {
        'edgeID': ['49478489#1', '668485027#2'],
        'position': [311.55, 330.69],
                'x': -35.283517,
        'y': 149.126185,
        'color' : (105,105,105, 255)
    },
    {
        'edgeID': ['4189987', '572132657'],
        'position': [862.55, 324.02],

        'x': -35.283846,
        'y': 149.126185,
        'color' : (105,105,105, 255)
    }
]


EMERGENCY_CENTER_SPECIFICATION : List[Dict[str, Any]]= [
    {
        "device_id": "Emergency Response",
        "manufacturer": 'Motorola Solutions',
        "model": 'Motorola Center 1',
        "firmware_version": '1.0.0',
        "hardware_version": '1.0.0',
        "serial_number": '123456789',
        "date_of_manufacture": '2020-01-01',
        "last_maintenance_date": '2020-01-01',
        "next_maintenance_date": '2020-01-01',
        "color": (0, 0, 0)
    }
]



EMERGENCY_VEHS: List[Dict[str, Any]] = [
  {
            'emergency_drop_off': '668452814',
            'emergency_drop_off_lane': '668452814_0',
            'emergency_drop_off_position': 145,
            'initial_emergency_location': '994397868',
            'initial_parking_time': 10800,
            'emergency_vehicle_type': 'emergency_vehicle'
        },
  {
            'emergency_drop_off': '668452814',
            'emergency_drop_off_lane': '668452814_0',
            'emergency_drop_off_position': 120,
            'initial_emergency_location': '994397868',
            'initial_parking_time': 10800,
            'emergency_vehicle_type': 'emergency_vehicle'
        },
]
