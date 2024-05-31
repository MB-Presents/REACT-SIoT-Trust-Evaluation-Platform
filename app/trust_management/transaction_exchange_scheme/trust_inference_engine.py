from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Dict
from uuid import UUID
from scipy.spatial import KDTree
from data_models.iot_devices.common import DeviceType

from data_models.iot_devices.genric_iot_device import GenericDevice
from trust_management.data_models.TrasactionExchangeScheme import TransactionExchangeScheme

import networkx as nx
import scenario_identification.visualization.create_images as network_visualization
from data.simulation.scenario_constants import Constants as sc
from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust_management.data_models.transaction.data_models.direct_recommendation import DirectRecommendation
from trust_management.data_models.transaction.data_models.indirect_recommendation import IndirectRecommendation
from trust_management.data_models.transaction.data_models.trust_transaction import Transaction


from trust_management.settings import TrustManagementSettings
from multiprocessing import Pool, cpu_count

class TrustManagementEngine:
    
    def __init__(self):
        self.device_locks = {}




    def exchange_transaction_between_devices(self, requestor: GenericDevice, respondee: GenericDevice) -> None:
        
        sending_transactions = respondee.trust_manager.trust_transaction_controller.transaction_manager.trust_transactions_excluding_indirect_recommendations
        
        suitable_transactions : Dict[UUID,AbstractTransaction] = {}

        for transaction_id, transaction in sending_transactions.items():
            if self._check_requirements(transaction, requestor):
                suitable_transactions[transaction_id] = transaction
        
        for trans_id, transaction in suitable_transactions.items():
            source_trans : Transaction = transaction
            
            recommender = respondee
            recommendee = requestor
            
            if recommender._id != source_trans.trustor._id:
                raise Exception("Recommendee and trustor are not the same")
            
            if isinstance(source_trans, Transaction):
                trust_subject = source_trans.trustee
                requestor.trust_manager.add_direct_trust_recommendation(recommendee=recommendee, recommender=recommender, trust_subject=trust_subject, transaction=source_trans)
                

            elif isinstance(source_trans, DirectRecommendation):
                trust_subject = source_trans.trustee
                requestor.trust_manager.add_indirect_trust_recommendation(recommendee=recommendee, recommender=recommender, trust_subject=trust_subject, transaction=source_trans)
                
            elif isinstance(source_trans, IndirectRecommendation):
                continue
            
            
    def _check_requirements(self, transaction : AbstractTransaction, receiving_device : GenericDevice) -> bool:
        
        if isinstance(transaction, Transaction):
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_in_recommendations(transaction._id):
                return False
                    
                
            if transaction._id in receiving_device.trust_manager.trust_transaction_controller.transaction_manager.trust_transactions.keys():
                return False
                
        
            return True
            
        elif isinstance(transaction, DirectRecommendation):
            

            
            if TrustManagementSettings.TRANSACTION_EXCHANGE_SCHEME == TransactionExchangeScheme.ONLY_DIRECT_TRANSACTION_EXCHANGE.value:
                return False

            if transaction.trustee._id == receiving_device._id:
                return False
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_in_recommendations(transaction._id):
                return False
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_in_recommendations(transaction.parent_transaction._id):
                return False
            
            if transaction._id in receiving_device.trust_manager.trust_transaction_controller.transaction_manager.trust_transactions.keys():    
                return False
            
            return True
            
            
        elif isinstance(transaction, IndirectRecommendation):
            raise Exception("Should not be come here.")
            
            if TrustManagementSettings.TRANSACTION_EXCHANGE_SCHEME == TransactionExchangeScheme.ONLY_DIRECT_TRANSACTION_AND_DIRECT_RECOMMENDATION_EXCHANGE.value:
                return False
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_transaction(transaction.parent_transaction._id):
                return False
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_transaction(transaction.parent_transaction.parent_transaction._id):
                return False
        

            if transaction.trustee._id == receiving_device._id:
                return False

            if receiving_device.trust_manager.trust_transaction_controller.exists_in_recommendations(transaction._id):
                return False
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_in_recommendations(transaction.parent_transaction._id):
                return False
            
            if receiving_device.trust_manager.trust_transaction_controller.exists_in_recommendations(transaction.parent_transaction.parent_transaction._id):
                return False
        
        
        raise Exception("Transaction type is not supported")
            



    def exchangeTransactions(self, devices: Dict[str, GenericDevice]) -> None:
        
        if TrustManagementSettings.TRANSACTION_EXCHANGE_SCHEME == TransactionExchangeScheme.NO_TRANSACTION_EXCHANGE.value:
            return
        
        
        for device_id in devices:
            if device_id not in self.device_locks:
                self.device_locks[device_id] = Lock()
        
        
        device_positions = [device._position for device in devices.values()]
        tree = KDTree(device_positions)
        exchange_pairs = []

        for requesting_device_id, requesting_device in devices.items():
            nearby_indices = tree.query_ball_point(requesting_device._position, TrustManagementSettings.MAX_TRANSACTION_EXCHANGE_DISTANCE)
            for index in nearby_indices:
                responding_device_id = list(devices.keys())[index]
                if responding_device_id != requesting_device_id:
                    # self.exchange_transaction_between_devices(requesting_device, devices[responding_device_id])
                    exchange_pairs.append((requesting_device, devices[responding_device_id]))
                    

        # with ThreadPoolExecutor(max_workers=10) as executor:
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Container to hold future tasks
            future_to_pair = {}
            try:
                for pair in exchange_pairs:
                    
                    requesting_device : GenericDevice = pair[0]
                    responding_device  : GenericDevice = pair[1]
                    
                    if self.device_locks[requesting_device._id].acquire(blocking=False):
                        try:
                            
                            future = executor.submit(self.exchange_transactions_pair, requesting_device, responding_device)
                            future_to_pair[future] = (requesting_device, responding_device)
                        except RuntimeError as e:
                            self.device_locks[requesting_device._id].release()
                            print(f"Exception occurred during transaction exchange between {requesting_device} and {responding_device}: {e}")
                        except Exception as e:
                            self.device_locks[requesting_device._id].release()
                            print(f"Exception occurred during transaction exchange between {requesting_device} and {responding_device}: {e}")


                for future in as_completed(future_to_pair):
                    pair = future_to_pair[future]
                    requesting_device, responding_device = pair
                    try:
                        result = future.result()
                        # Process the result
                        # print(f"Transaction exchange completed between {requesting_device._id} and {responding_device._id}")
                    except Exception as e:
                        # Handle exceptions
                        print(f"Exception occurred during transaction exchange between {requesting_device._id} and {responding_device._id}: {e}")
                    finally:
                        self.device_locks[requesting_device._id].release()
                        # self.device_locks[pair[1]._id].release()
            except Exception as e:
                print(f"Exception occurred during transaction exchange: {e}")
                raise e

                    

    def exchange_transactions_pair(self, requesting_device, responding_device):

        self.exchange_transaction_between_devices(requesting_device, responding_device)    


        
    def visualise_trust_network(self, devices: Dict[str, GenericDevice], is_transaction_exchange : bool):
        G = nx.Graph()
        
        for device_id, device in devices.items():

            G.add_node(device._id, device_type=device._type, position=device._position)

            transaction : Transaction
            for transaction_id, transaction in device.trust_manager.trust_transaction_controller.transaction_manager.trust_transactions.items():
                
                trustor = transaction.trustor
                trustee = transaction.trustee
                
                
                self.add_node(G, trustor)
                self.add_node(G, trustee)

                G.add_edge(transaction.trustor._id, transaction.trustee._id, trust_value=transaction.trust_value)

        # Extract attributes for visualization
        node_positions = {device_id: device['position'] for device_id, device in G.nodes(data=True)}
        node_colors = network_visualization.get_node_colors(G,scenario_identification=False)  # You'd adjust this function to get 
        
        target_labels = [data['device_type'] for node, data in G.nodes(data=True)]
        
        network_visualization.setup_plot()
        
        nx.draw_networkx_nodes(G, pos=node_positions, node_color=node_colors, node_shape='o', node_size=300)
        nx.draw_networkx_edges(G, pos=node_positions, edge_color='gray', alpha=0.5)
        
        network_visualization.draw_labels(G, node_positions)
        
        if is_transaction_exchange:
            output_directory = "/app/output/trust_network/with_transaction_exchange"
        elif not is_transaction_exchange:
            output_directory = "/app/output/trust_network/without_transaction_exchange"
        
        network_visualization.save_plot(sc.TIME, output_directory)

    def add_node(self, G : nx.Graph, transaction_device : GenericDevice):
        
        
        nodes = G.nodes
        if transaction_device._id in nodes:
            return
        
        if not isinstance(transaction_device._id, str):
            print("trustor._id: ", transaction_device._id)
                
        if not isinstance(transaction_device._type, DeviceType):
            print("trustor._type: ", transaction_device._type)
                
        if not isinstance(transaction_device._position, tuple):
            print("trustor._position: ", transaction_device._position)
        
        
        G.add_node(transaction_device._id, device_type=transaction_device._type, position=transaction_device._position)