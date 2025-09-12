


from __future__ import annotations

from typing import TYPE_CHECKING, Dict
from ast import Tuple


import sys
import os

import numpy as np
from dataset_builder.models.link_predictor.LinearLinkPredictor import LinkPredictor
from dataset_builder.models.tgn import GraphAttentionEmbedding
from dataset_builder.utils import path_helper
from trust.data_models.TrustVerifierRoles import TrustVerfierRoles

from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.data_models.transaction.status import TransactionStatus
from trust.data_models.transaction.type import TransactionType
from trust.trust_recommenders.graph_based_trust_model.models.last_neighbor_loader import LastNeighborLoader
from trust.trust_recommenders.graph_based_trust_model.preprocessing import get_engineered_features, preprocess_data

project_root = os.getenv("RESEARCH_PROJECT_ROOT", default="/app")
sys.path.insert(0, project_root)

from trust.situation_recognition_module.situation_recognition import SituationSettings
from trust.trust_recommenders.interface_trust_model import ITrustComputationModel

from trust.trust_recommenders.interface_trust_model import ITrustComputationModel

from torch_geometric.data import TemporalData


import torch

from torch_geometric.nn import TGNMemory
from torch_geometric.nn.models.tgn import (
    IdentityMessage,
    LastAggregator,
    # LastNeighborLoader,
)


from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters



if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.situation_recognition_module.situation_recognition import SituationSettings

import trust.trust_recommenders.graph_based_trust_model.config as config

class TemporalGraphBasedTrustModel(ITrustComputationModel):
    
    def check_compliance(   self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> bool:
        pass

    
    def preprocess_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        pass
    
    
    def computate_trust_value(self, trustor : GenericDevice, 
                                    trustee : GenericDevice,
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        
        prediction = trustor.trust_manager._temporal_graph_based_trust_model.trust_update(trustor=trustor, trustee=trustee, trust_value=0.5, request=request,transaction=None, situation_settings=situation_settings)
        
        return prediction
    
    
    def postprocessing_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None, 
                                    situation_settings : SituationSettings = None) -> float:
        pass
    
    
class TemporalGraphNetwork:

    def __init__(self):
    
        self.neighbor_loader : LastNeighborLoader = LastNeighborLoader(num_nodes=config.num_memory_nodes, 
                                                                       size=config.sliding_window_of_events, 
                                                                       device=config.device)
        self.neighbor_loader.reset_state()  
        
        self.data : TemporalData = TemporalData(
            src=torch.tensor([], dtype=torch.long),
            dst=torch.tensor([], dtype=torch.long),
            t=torch.tensor([], dtype=torch.long),
            msg=torch.tensor([], dtype=torch.float),
            y=torch.tensor([], dtype=torch.float),
            node_features=torch.tensor([], dtype=torch.float)
        ).to(config.device)
        
        self.memory : TGNMemory = TGNMemory(
            num_nodes=config.num_memory_nodes,
            raw_msg_dim=config.msg_size,
            memory_dim=config.memory_dim,
            time_dim=config.time_dim,
            message_module=IdentityMessage(config.msg_size, config.memory_dim, config.time_dim),
            aggregator_module=LastAggregator(),
        ).to(config.device)

        self.gnn : GraphAttentionEmbedding = GraphAttentionEmbedding(
            in_channels=config.memory_dim,
            out_channels=config.embedding_dim,
            msg_dim=config.msg_size,
            time_enc=self.memory.time_enc,
        ).to(config.device)

        self.link_pred : LinkPredictor = LinkPredictor(in_channels=config.embedding_dim).to(config.device)

        model_path = path_helper.get_model_base_path()
        
        gnn_model_file_name = path_helper.FILE_NAMES['gnn_model']
        link_prediction_file_name = path_helper.FILE_NAMES['link_prediction_model']
        memeory_mdoel_file_name = path_helper.FILE_NAMES['memory_model']

        gnn_model_output_path = os.path.join(model_path, gnn_model_file_name)
        link_prediction_model_output_path = os.path.join(model_path, link_prediction_file_name)
        memory_model_output_path = os.path.join(model_path, memeory_mdoel_file_name)

        # self.memory.load_state_dict(torch.load(memory_model_output_path))
        self.memory = self.memory.to(config.device)
        self.memory.reset_state()

        self.gnn.load_state_dict(torch.load(gnn_model_output_path))
        self.gnn = self.gnn.to(config.device)

        self.link_pred.load_state_dict(torch.load(link_prediction_model_output_path))
        self.link_pred = self.link_pred.to(config.device)
        
        self.assoc = torch.empty(config.num_memory_nodes, dtype=torch.long, device=config.device)
        self.criterion = torch.nn.BCEWithLogitsLoss()
        
    
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float = 0.5,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:
        

        
        if transaction is None:
            transaction = AbstractTransaction(trustor=trustor, trustee=trustee, trust_value=trust_value, reporting_time=ScenarioParameters.TIME, type=TransactionType.DIRECT_TRANSACTION, status=TransactionStatus.PENDING, task_context=request, role=TrustVerfierRoles.REPORTER)
        
        
        transaction_event : dict = preprocess_data(trustor=trustor, 
                                                          trustee=trustee,
                                                          trust_value=trust_value,
                                                          request=request,
                                                          transaction=transaction,
                                                          situation_settings=situation_settings)
         
        transaction_event : dict = get_engineered_features(transaction_event)
        
                
        

        label = 'trustworthiness'

        sources = np.array(transaction_event['trustor']).reshape(-1)
        destinations = np.array(transaction_event['trustee']).reshape(-1)
        timestamps = np.array(transaction_event['time']).reshape(-1)

        _node_features = config._selected_trustor_features + config._selected_trustee_features
        node_features = np.column_stack([transaction_event[feature] for feature in _node_features])

        _edge_features = config._selected_edge_features
        edge_features = np.column_stack([transaction_event[feature] for feature in _edge_features])

        edge_labels = np.array(transaction_event[label]).reshape(-1)
        
        src = torch.from_numpy(sources).to(torch.long)
        dst = torch.from_numpy(destinations).to(torch.long)

        t = torch.from_numpy(timestamps).to(torch.long)
        y = torch.from_numpy(edge_labels).to(torch.float)
        msg = torch.from_numpy(edge_features).to(torch.float)

        node_features = torch.from_numpy(node_features).to(torch.float)

        
        self.add_new_event(node_features, src, dst, t, y, msg)

        prediction = self.conduct_trust_transaction_update(self.data, trustor, trustee)    
        
        
        return prediction

    def add_new_event(self, node_features, src, dst, t, y, msg):
        self.data.src = torch.cat((self.data.src, src), dim=0)
        self.data.dst = torch.cat((self.data.dst, dst), dim=0)
        self.data.t = torch.cat((self.data.t, t), dim=0)
        self.data.msg = torch.cat((self.data.msg, msg), dim=0)
        self.data.y = torch.cat((self.data.y, y), dim=0)
        self.data.node_features = torch.cat((self.data.node_features, node_features), dim=0)
        
    
    def get_last_element_batch(self, data : TemporalData):
        
        batch = data[-1:]
        n_ids = [batch.src, batch.dst]
        batch.n_id = torch.cat(n_ids, dim=0).unique()
        
        return batch.to(config.device)
    
    
    @torch.no_grad()
    def conduct_trust_transaction_update(self, data : TemporalData, trustor, trustee):
        self.memory.eval()
        self.gnn.eval()
        self.link_pred.eval()

        # torch.manual_seed(12345)  # Ensure deterministic sampling across epochs.
        
        batch = self.get_last_element_batch(data)
            
        n_id, edge_index, e_id = self.neighbor_loader.load(batch.n_id)

        
        self.assoc[n_id] = torch.arange(n_id.size(0), device=config.device)

        z, last_update = self.memory(n_id)
        z = self.gnn(z, last_update, edge_index, data.t[e_id].to(config.device), data.msg[e_id].to(config.device))
        
        out = self.link_pred(z[self.assoc[batch.src]], z[self.assoc[batch.dst]]).squeeze(1)

        y_pred = out.sigmoid().item()
        
        self.memory.update_state(batch.src, batch.dst, batch.t, batch.msg)
        self.neighbor_loader.insert(batch.src, batch.dst)
        
        return y_pred
    
    