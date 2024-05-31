import json
import logging
from logstash_async.constants import Constants


Constants.QUEUED_EVENTS_BATCH_SIZE = 2000

            
from logstash_async.handler import AsynchronousLogstashHandler

from elasticsearch import Elasticsearch
from enum import Enum, auto

import pandas as pd

from data.simulation.scenario_constants import Constants as sc

from data_models.simulation.logging import ObjectType
from experiments.settings import Settings


from pathlib import Path
import pickle
import pathlib
import os


class LogLevel(Enum):
    ERROR = auto()
    WARNING = auto()
    DEBUG = auto()
    EXCEPTION = auto()
    INFO = auto()

class JsonOnlyFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, str):
            try:
                json.loads(record.msg)
                return record.msg
            except ValueError:
                pass
        return super().format(record)



class Logging(object):
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, logger_name='python-logger', host='canberra-small-logstash-1', port=50000):
        
        if not hasattr(self, "is_initialized"):
            self.async_handler : AsynchronousLogstashHandler = None
            self.is_initialized = True
            self.es : Elasticsearch = None
            try:
                self.es = Elasticsearch(['http://canberra-small-elasticsearch-1:9200'], 
                                        http_auth=('elastic', 'changeme'), 
                                        retry_on_timeout=True, 
                                        request_timeout=30)
            except ConnectionError as e:
                print(str(e)) 

            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
            
            self.async_handler = AsynchronousLogstashHandler(host,port,database_path=None)
            
            self.async_handler.setFormatter(JsonOnlyFormatter())   
            logger.addHandler(self.async_handler)
            
            self.logger_ls = logger
    
        
    def delete_index(self, index_name='sumo'):
        
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
        
        if self.es.indices.exists(index='sumo'):
            print("Deleting index: sumo")
        
        if self.es.indices.exists(index='log'):
            self.es.indices.delete(index='log')
            
        if self.es.indices.exists(index='logs'):
            self.es.indices.delete(index='logs')
            
    def create_index(self, index_name='sumo'):
        settings = {
            "settings": {
                "number_of_shards": 1
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "email": {"type": "keyword"},
                    # ... define the rest of your fields here ...
                }
            }
        }
        
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=settings)
        
        # self.es.indices.create(index=index_name, body=settings)

    def get_instance(self) -> logging.Logger:
        return self.logger_ls
        
    
def exception(e: Exception, message=""):

    exception_log = {
        'log_level': LogLevel.EXCEPTION.name,
        'exception': str(e),
        'time':sc.TIME,
    }
    
    exception_log.update(message)
    json_message = json.dumps(exception_log)

    get_logger().get_instance().exception(json_message)


def error(object_type: ObjectType,  message : dict):

    error_log = {
        'log_level': LogLevel.ERROR.name,
        'object_type': object_type.name,
        'time': sc.TIME,
        'message': message
        
    } 
    
    error_log.update(message)
    
    json_message = json.dumps(error_log)

    get_logger().get_instance().error(json_message)


class LoggingBehaviour(Enum):
    STATUS = auto()
    SENSING = auto()
    NONE = auto()


def info(object_type: ObjectType, message : dict, log_object: LoggingBehaviour = LoggingBehaviour.NONE):

    info_log = {
        'log_level': LogLevel.INFO.name,
        'object_type': object_type.name,
        'time': sc.TIME,
        'experiment_id': Settings.EXPERIMENT_ID,
        'simulation_run_id': Settings.SIMULATION_RUN_INDEX
    } 
    
    
    if log_object != LoggingBehaviour.NONE:
        if log_object == LoggingBehaviour.STATUS:
            info_log.update({"id": f"{LoggingBehaviour.STATUS.name}_time_{sc.TIME}_{message['device_id']}"})
        
        
        elif log_object == LoggingBehaviour.SENSING:
            info_log.update({"id": f"{LoggingBehaviour.SENSING.name}_time_{sc.TIME}_{message['sensor_id']}_sensing_{message['device_id']}"})
        
    info_log.update(message)

    if sc.logging_info_active == True:
        
        json_message = json.dumps(info_log)
        
        try:
            get_logger().get_instance().info(json_message)
        except Exception as e:
            print(f"Failed to log message: {e}")

def get_logger() -> Logging:
    return Logging(port=50000, host='canberra-small-logstash-1', logger_name='python-logger')



def write_pickle(file_path, python_object):
    
    filepath = Path(file_path)
    directory = pathlib.Path(filepath).parent.resolve()
  
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(filepath, "wb") as f:
            info = {"experiment_id": Settings.EXPERIMENT_ID, "simulation_run_index": Settings.SIMULATION_RUN_INDEX, "data": python_object}
            # print(info)
            pickle.dump(info, f)

    except pickle.PicklingError:
        print("PicklingError: Object could not be pickled")
    except pickle.UnpicklingError:
        print("UnpicklingError: Object could not be unpickled")
    except AttributeError:
        print("AttributeError: A non-picklable attribute was encountered")
    except EOFError:
        print("EOFError: End of file reached prematurely")
    except ImportError:
        print("ImportError: A required module for unpickling is missing")
    except IndexError:
        print("IndexError: Index out of range error")
    except KeyError:
        print("KeyError: Key not found error")
    except MemoryError:
        print("MemoryError: Not enough memory to complete the operation")
    except TypeError:
        print("TypeError: Argument of an inappropriate type")
    except ValueError:
        print("ValueError: Inappropriate argument value")
    except OSError as e:
        print(f"OSError: OS error occurred - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    


def write_csv(file_path, python_object):
    filepath = Path(file_path)
    directory = filepath.parent.resolve()

    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        # Assuming python_object is a pandas DataFrame
        if isinstance(python_object, pd.DataFrame):
            python_object.to_csv(filepath, index=False)
        else:
            # If it's not a DataFrame, attempt to convert it
            df = pd.DataFrame(python_object)
            df.to_csv(filepath, index=False)

    except Exception as e:
        print(e)
        print("Error while writing CSV file")
