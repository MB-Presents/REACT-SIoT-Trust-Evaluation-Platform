
import sys
sys.path.insert(0, '/app')

# from data_processing.parser import parse_osm
from elasticsearch import Elasticsearch
import elasticsearch
# Load Geographical Map Network

# import logging
# logging.basicConfig(level=logging.ERROR)


es = Elasticsearch(['http://react-siot-trust-evaluation-platform-elasticsearch-1:9200'], 
                   basic_auth=('elastic', 'changeme'), 
                   retry_on_timeout=True, 
                   request_timeout=30)


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
                    'firmware_version',
                    'hardware_version',
                    'serial_number',
                    'date_of_manufacture', 
                    'last_maintenance_date',
                    'next_maintenance_date',
                    'properties',
                    'services'
                    ]

    vehicle_specific_keys = [
                        # 'speed',
                        'signal',
                        'edge_id',
                        'lane_id',
                        'lane_position',
                        # 'vehicle_type',
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

def es_search(query, index="sumo", size=5000, scroll=None):
    try:
        if scroll:
            return es.search(index=index, body=query, scroll=scroll, size=size, allow_partial_search_results=True )
        elif scroll is None:
            return es.search(index=index, body=query, size=size, allow_partial_search_results=True )
    except elasticsearch.exceptions.ConnectionError as e:
        print(e)
        return None    
    except elasticsearch.exceptions.ConnectionTimeout as e:
        print(e)
        return None 
    except elasticsearch.exceptions.RequestError as e:
        print(e)
    except elasticsearch.exceptions.SerializationError as e:
        print(e)
    except Exception as e:
        print(e)
        return None

def get_generic_object_query(experiment_id, simulation_run_id, object_type):
    return {
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

def get_data(query, batched=False, scroll_time='1m'):
    try:
        if batched:
            
            all_matched_objects = []
            page = es_search(query, scroll=scroll_time)
            scroll_id = page['_scroll_id']
            
            scroll_size = page['hits']['total']['value']
            
            all_matched_objects.extend([hit["_source"] for hit in page["hits"]["hits"]])
            
            
            
            scroll_index = 0
            scroll_index += len(page["hits"]["hits"])
            
            while scroll_index < scroll_size:
                
                batch = es.scroll(scroll_id=scroll_id, scroll=scroll_time)
                scroll_id = batch['_scroll_id']
                hits = batch['hits']['hits']
                
                all_matched_objects.extend([hit["_source"] for hit in hits])
                
                if scroll_index == 400000:
                    print("Reached 400,000")
                
                
                scroll_index += len(hits)
                
            es.clear_scroll(scroll_id=scroll_id)
            return all_matched_objects
        
        else:
            
            response = es_search(query)
            return [hit["_source"] for hit in response["hits"]["hits"]]
    
    except Exception as e:
        print(e)
        return None 


def get_max_time(experiment_id, simulation_run_id):
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"term": {"experiment_id.keyword": experiment_id}},
                    {"term": {"simulation_run_id": simulation_run_id}}
                ]
            }
        },
        "aggs": {"max_time": {"max": {"field": "time"}}}
    }
    response = es.search(index="sumo", body=query)
    
    max_time = response['aggregations']['max_time']['value']
    
    
    
    max_time = int(max_time) if max_time is not None else None
    
    return max_time





def get_object_states_for_time_range(start_time, end_time, experiment_id, simulation_run_id, object_types):
    
    object_type_queries = [{"term": {"type.keyword": object_type}} for object_type in object_types]
    query = {
        # "size": 5000,
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
    
    
    records = get_data(query, batched=True, scroll_time='10m') 
    return records


def get_object_state_at_timestep(time, experiment_id, simulation_run_id, object_types):
    
    object_type_queries = [{"term": {"type.keyword": object_type}} for object_type in object_types]
    query = {
        # "size": 5000,
        "query": {
            "bool": {
                "must": [
                    {"term": {"experiment_id.keyword": experiment_id}},
                    {"term": {"simulation_run_id": simulation_run_id}},
                    {"term": {"time": time}},
                    {"term": {"record_type.keyword": "STATUS"}}
                ],
                "should": object_type_queries,
                "minimum_should_match": 1
            }
        }
    }
    return get_data(query)

def get_reports(experiment_id, simulation_run_id):
    query = get_generic_object_query(experiment_id, simulation_run_id, "REPORT")
    return get_data(query, batched=True, scroll_time='8m')

def get_events(experiment_id, simulation_run_id):
    query = get_generic_object_query(experiment_id, simulation_run_id, "EVENT")
    return get_data(query, batched=True, scroll_time='8m')

def get_trust_transactions(experiment_id, simulation_run_id):
    query = get_generic_object_query(experiment_id, simulation_run_id, "TRUST_TRANSACTION")
    return get_data(query, batched=True, scroll_time='8m')

def get_route_messages(experiment_id, simulation_run_id):
    query = get_generic_object_query(experiment_id, simulation_run_id, "ROUTE_MESSAGE")
    return get_data(query, batched=True, scroll_time='7m')

def get_debug_accident_status(experiment_id, simulation_run_id):
    query = get_generic_object_query(experiment_id, simulation_run_id, "DEBUG_ACCIDENT_STATUS")
    return get_data(query, batched=True, scroll_time='7m')






# Get object states for a time range
# object_states = get_object_states_for_time_range(0, 100, experiment_id, simulation_run_id, ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE", "TRAFFIC_CAMERA", "TRAFFIC_LIGHT", "EMERGENCY_CENTER"])

# Get object state at a specific timestep
# object_state_at_time = get_object_state_at_timestep(50, experiment_id, simulation_run_id, ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE", "TRAFFIC_CAMERA"])