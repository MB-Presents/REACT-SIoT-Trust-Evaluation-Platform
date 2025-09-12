
import sys
sys.path.insert(0, '/app')

# from data_processing.parser import parse_osm
from elasticsearch import Elasticsearch, exceptions
# Load Geographical Map Network

import logging
logging.basicConfig(level=logging.ERROR)

def remove_extra_record_attributes(object_item):
    
    
    looging_keys = ['program',
                    'logsource',
                    'log_level',
                    'extra',
                    'pid',
                    'host',
                    '@version',
                    '@timestamp',
                    'level',
                    'message',
                    'tags']
    
    
    
        # first_dict_keys and second_dict_keys are lists of keys you want to remove
    generic_device_dict = [
                    # 'device_id',
                    # 'affiliations',
                    # 'type',
                    # 'position',
                    # 'color',
                    # 'speed',
                    # 'status',
                    # 'shape_status',
                    # 'manufacturer', 
                    # 'model',
                    # 'firmware_version',
                    # 'hardware_version',
                    # 'serial_number',
                    # 'date_of_manufacture', 
                    # 'last_maintenance_date',
                    # 'next_maintenance_date',
                    # 'properties',
                    # 'services'
                    ]

    vehicle_specific_keys = [
                        # 'speed',
                        # 'signal',
                        # 'edge_id',
                        # 'lane_id',
                        # 'lane_position',
                        'vehicle_type',
                        'width', 
                        'height',
                        'length',
                        'lane_index',
                        'vehicle_class'
                        ]

    # merge the two lists into keys_to_remove
    keys_to_remove = looging_keys + generic_device_dict + vehicle_specific_keys
    
    
    
    
    for key in keys_to_remove:
        if key in object_item:
            del object_item[key]
    return object_item
    

def remove_extra_attributes(objects : list):
    
    
    looging_keys = ['program',
                    'logsource',
                    'log_level',
                    'extra',
                    'pid',
                    'host',
                    '@version',
                    '@timestamp',
                    'level',
                    'message',
                    'tags']
    
    
    
        # first_dict_keys and second_dict_keys are lists of keys you want to remove
    generic_device_dict = [
                    # 'device_id',
                    # 'affiliations',
                    # 'type',
                    # 'position',
                    # 'color',
                    # 'speed',
                    # 'status',
                    # 'shape_status',
                    # 'manufacturer', 
                    # 'model',
                    'firmware_version',
                    'hardware_version',
                    'serial_number',
                    'date_of_manufacture', 
                    'last_maintenance_date',
                    'next_maintenance_date',
                    # 'properties',
                    # 'services'
                    ]

    vehicle_specific_keys = [
                        # 'speed',
                        # 'signal',
                        # 'edge_id',
                        # 'lane_id',
                        # 'lane_position',
                        'vehicle_type',
                        'width', 
                        'height',
                        'length',
                        'lane_index',
                        'vehicle_class'
                        ]
    
    sumo_specific_keys = [
        'simulation_run_id',
        'experiment_id'
    ]

    # merge the two lists into keys_to_remove
    keys_to_remove = looging_keys + generic_device_dict + vehicle_specific_keys + sumo_specific_keys
    
    
    
    for obj in objects:
        for key in keys_to_remove:
            if key in obj:
                del obj[key]
    return objects
    
    
    
    
    
    
    
def get_trust_transactions():
         
    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)

    # Define the index and query parameters
    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    object_type = "TRUST_TRANSACTION"



    query = {
        "size":1000,
        "query": {
            "bool": {
            "must": [
                {
                "term": {
                    "experiment_id.keyword": experiment_id
                }
                },
                {
                "term": {
                    "simulation_run_id": simulation_run_id
                }
                },
                {
                "term": {
                    "object_type.keyword": object_type
                }
                }
            ]
            }
        }
    }

    response = es.search(index=index, body=query)
    hits = response["hits"]["hits"]
    matched_objects = [hit["_source"] for hit in hits]
    
    return matched_objects


def get_trust_transactions_batched():
    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], 
                       basic_auth=('elastic', 'changeme'), 
                       retry_on_timeout=True, 
                       request_timeout=30)

    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    object_type = "TRUST_TRANSACTION"

    query = {
        "size": 1000,
        "query": {
            "bool": {
                "must": [
                    {"term": {"experiment_id.keyword": experiment_id}},
                    {"term": {"simulation_run_id": simulation_run_id}},
                    {"term": {"object_type.keyword": object_type}}
                ]
            }
        }
    }

    # Initialize the scroll
    page = es.search(index=index, body=query, scroll='1m')
    scroll_id = page['_scroll_id']
    hits = page['hits']['hits']
    scroll_size = len(hits)

    all_matched_transactions = [hit["_source"] for hit in hits]  # Include the first batch of results

    # Start scrolling
    while scroll_size > 0:
        # Get the next batch of results
        batch = es.scroll(scroll_id=scroll_id, scroll='1m')

        # Update the scroll ID and size
        scroll_id = batch['_scroll_id']
        hits = batch['hits']['hits']
        scroll_size = len(hits)

        # Extend the list of all matched transactions with the current batch
        all_matched_transactions.extend([hit["_source"] for hit in hits])

        # Break the loop if no more results are returned
        if scroll_size == 0:
            break

    return all_matched_transactions



        
def get_events():

    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)

    # Define the index and query parameters
    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    object_type = "EVENT"



    query = {
        "size":1000,
        "query": {
            "bool": {
            "must": [
                {
                "term": {
                    "experiment_id.keyword": experiment_id
                }
                },
                {
                "term": {
                    "simulation_run_id": simulation_run_id
                }
                },
                {
                "term": {
                    "object_type.keyword": object_type
                }
                }
            ]
            }
        }
    }

    response = es.search(index=index, body=query)
    hits = response["hits"]["hits"]
    matched_objects = [hit["_source"] for hit in hits]
    
    return matched_objects


def get_max_time():

    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)

    # Define the index and query parameters
    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    object_type = "VEHICLE"

    query = {
        "size": 0,  # No actual documents needed
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "experiment_id.keyword": experiment_id
                        }
                    },
                    {
                        "term": {
                            "simulation_run_id": simulation_run_id
                        }
                    },
                    # {
                    #     "term": {
                    #         "object_type.keyword": object_type
                    #     }
                    # }
                ]
            }
        },
        "aggs": {
            "max_time": {
                "max": {
                    "field": "time"  # replace "time" with your actual time field
                }
            }
        }
    }

    response = es.search(index=index, body=query)

    # Extract maximum time from the response
    max_time = response['aggregations']['max_time']['value']
    
    # Convert it to integer
    max_time = int(max_time) if max_time is not None else None

    return max_time


def get_reports():
    
    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)
        
    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    object_type = "REPORT"


    query = {
        "size":5000,
        "query": {
            "bool": {
            "must": [
                {
                "term": {
                    "experiment_id.keyword": experiment_id
                }
                },
                {
                "term": {
                    "simulation_run_id": simulation_run_id
                }
                },
                {
                "term": {
                    "object_type.keyword": object_type
                }
                }
            ]
            }
        }
    }

    response = es.search(index=index, body=query)
    # Extract the matched objects from the response
    hits = response["hits"]["hits"]
    matched_objects = [hit["_source"] for hit in hits]
    return matched_objects

def get_object_states_for_time_range(start_time: int, end_time: int):
    try:
        print('Test')
        es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=120)

        index = "sumo"
        experiment_id = "EXP001"
        simulation_run_id = 1
        object_types = ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE", "TRAFFIC_CAMERA","TRAFFIC_LIGHT","EMERGENCY_CENTER"]

        object_type_queries = [{"term": {"type.keyword": object_type}} for object_type in object_types]

        query = {
            "size": 1000,  # Number of records per batch; adjust as needed
            "query": {
                "bool": {
                    "must": [
                        {"term": {"experiment_id.keyword": experiment_id}},
                        {"term": {"simulation_run_id": simulation_run_id}},
                        {"term": {"record_type.keyword": "STATUS"}},
                        {"range": {"time": {"gte": start_time, "lte": end_time}}}
                    ],
                    "should": object_type_queries,
                    "minimum_should_match": 1
                }
            }
        }

        # Initialize the scroll
        page = es.search(
            index=index,
            body=query,
            scroll='4m'  # length of time Elasticsearch should keep the search context alive; adjust as needed
        )
        scroll_id = page['_scroll_id']
        scroll_size = len(page['hits']['hits'])
    

        all_matched_objects = []

        # Start scrolling
        page_count = 0
        while scroll_size > 0:
            try:
                page_count += 1
                all_matched_objects.extend([hit["_source"] for hit in page['hits']['hits']])
                
                page = es.scroll(scroll_id=scroll_id, scroll='4m')
                scroll_id = page['_scroll_id']
                scroll_size = len(page['hits']['hits'])
                print(f"Scrolling...  (page: {page_count}, scroll size: {scroll_size})", end='\r')
                # print(f"Scrolling...  (scroll size: {scroll_size}")
            except Exception as e:
                print(f"Error occurred: {e}")
        # print(all_matched_objects)
        print("Done")
        return all_matched_objects
            
    except Exception as e:
            print(f"Error occurred: {e}")
        


def get_object_state_at_timestep(time : int = 0):

    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)

    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    # object_types = ["INDUCTION_LOOP", "SMART_PHONE", "TRAFFIC_CAMERA", "VEHICLE"]
    object_types = ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE","TRAFFIC_CAMERA"]
    

    # Create a series of 'term' queries for each object type
    object_type_queries = [{"term": {"type.keyword": object_type}} for object_type in object_types]

    query = {
        "size": 5000,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "experiment_id.keyword": experiment_id
                        }
                    },
                    {
                        "term": {
                            "simulation_run_id": simulation_run_id
                        }
                    },
                    {
                        "term": {
                            "time": time
                        }
                    }
                    ,
                    {
                        "term": {
                            "record_type.keyword": "STATUS"
                        }
                    }

                ]
                ,
                "should": object_type_queries,
                "minimum_should_match": 1
            }
        }
    }

    response = es.search(index=index, body=query)
    # Extract the matched objects from the response
    hits = response["hits"]["hits"]
    matched_objects = [hit["_source"] for hit in hits]
    return matched_objects

def get_traffic_light_state_at_timestep(time : int = 0):

    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)

    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    # object_types = ["INDUCTION_LOOP", "SMART_PHONE", "TRAFFIC_CAMERA", "VEHICLE"]
    object_types = ["TRAFFIC_LIGHT_SYSTEM"]
    

    # Create a series of 'term' queries for each object type
    object_type_queries = [{"term": {"object_type.keyword": object_type}} for object_type in object_types]

    query = {
        "size": 5000,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "experiment_id.keyword": experiment_id
                        }
                    },
                    {
                        "term": {
                            "simulation_run_id": simulation_run_id
                        }
                    },
                    {
                        "term": {
                            "time": time
                        }
                    }

                ],
                "should": object_type_queries,
                "minimum_should_match": 1
            }
        }
    }

    response = es.search(index=index, body=query)
    # Extract the matched objects from the response
    hits = response["hits"]["hits"]
    matched_objects = [hit["_source"] for hit in hits]
    return matched_objects


def get_device_state(device_id : str, time : int = 0):

    es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], basic_auth=('elastic', 'changeme'), retry_on_timeout=True, request_timeout=30)

    index = "sumo"
    experiment_id = "EXP001"
    simulation_run_id = 1
    # object_types = ["INDUCTION_LOOP", "SMART_PHONE", "TRAFFIC_CAMERA", "VEHICLE"]
    # object_types = ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE","TRAFFIC_CAMERA"]
    

    # Create a series of 'term' queries for each object type
    # object_type_queries = [{"term": {"object_type.keyword": object_type}} for object_type in object_types]

    query = {
        "size": 5000,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "experiment_id.keyword": experiment_id
                        }
                    },
                    {
                        "term": {
                            "simulation_run_id": simulation_run_id
                        }
                    },
                    {
                        "term": {
                            "time": time
                        }
                    },
                    {
                        "term": {
                            "device_id": device_id
                        }
                    }

                ]
                # ,
                # "should": object_type_queries,
                # "minimum_should_match": 1
            }
        }
    }

    response = es.search(index=index, body=query)
    # Extract the matched objects from the response
    hits = response["hits"]["hits"]
    matched_objects = [hit["_source"] for hit in hits]
    return matched_objects
