from enum import Enum


class ColorCode(Enum):
    INDUCTION_LOOP = (0,0,225,255)
    TRAFFIC_CAMERA = (255, 0, 0, 255)

induction_sensors = [
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
    }
    # ,
    # {
    #     'id':'induction_loop_2',
    #     'edgeID':'673118338',
    #     'position':[796.67,216.25,787.59,221.86 ],
    #     'induction_position':200,
    #     'manufacturer': 'Manufacturer2',
    #     'model': 'Model2',
    #     'firmware_version': '2.0.0',
    #     'hardware_version': '2.0',
    #     'serial_number': '23456',
    #     'date_of_manufacture': '2022-02-01',
    #     'last_maintenance_date': '2023-02-01',
    #     'next_maintenance_date': '2023-08-01',
    # },
    # Add more induction sensors as needed...
]



traffic_cameras = [
    {
        'edgeID': ['668452809', '668452814'],
        'position': [577.69, 866.63],
    },
    {
        'edgeID': ['489692411#1', '668468055'],
        'position': [703.90, 850.16],
    },
    {
        'edgeID': ['307292406', '138708547'],
        'position': [560.31, 272.15],
    },
    {
        'edgeID': ['49478489#1', '668485027#2'],
        'position': [311.55, 330.69],
    },
    {
        'edgeID': ['4189987', '572132657'],
        'position': [862.55, 324.02],
    }
]