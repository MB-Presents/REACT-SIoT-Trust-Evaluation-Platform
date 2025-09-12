
from torch_geometric.datasets import JODIEDataset
import torch
from sklearn.metrics import average_precision_score, roc_auc_score
from torch.nn import Linear

from torch_geometric.loader import TemporalDataLoader
from torch_geometric.nn import TGNMemory, TransformerConv
from torch_geometric.nn.models.tgn import (
    IdentityMessage,
    LastAggregator,
    LastNeighborLoader,
)

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


from collections import Counter
import matplotlib.pyplot as plt

from torch_geometric.utils.convert import to_networkx, from_networkx
import os
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

from torch_geometric.data import TemporalData,InMemoryDataset
import argparse
from torch.utils.data import TensorDataset

from dataset_builder.utils.path_helper import DatasetType, get_in_memory_dataset_path
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')



def get_dataframe(path=None):
    
    data_name="iot-unsw"
    
    if os.path.exists(path):
        DATA_DIR = path
    else:
        raise ValueError("Invalid path specified.")
    
    
    
    OUT_EDGES = os.path.join(DATA_DIR, 'ml_{}_edges.csv'.format(data_name))
    OUT_NOES = os.path.join(DATA_DIR, 'ml_{}_nodes.csv'.format(data_name))
    OUT_EGEE_FEAT = os.path.join(DATA_DIR, 'ml_{}_edge_features.npy'.format(data_name))
    OUT_NODE_FEAT = os.path.join(DATA_DIR, 'ml_{}_node_features.npy'.format(data_name))

    OUT_DATASET = os.path.join(DATA_DIR, 'ml_{}.csv'.format(data_name))
        
    data = pd.read_csv(OUT_DATASET)
    
    return data




# def process_node_classification_situation_label_dataset(dataset):
    
#     sources = dataset['device_id'].values
#     timestamps = dataset['time'].values
#     edge_idxs = dataset.index.values



#     # node_features_columns = ['distance', 'latitude', 'longitude', 'shape_status_DEFORMED', 
#     node_features_columns = ['shape_status_DEFORMED',  
#                             'shape_status_ORIGINAL_MANUFACTURED', 
#                             'signal', 'speed', 'status_ACTIVE', 'status_ERROR', 
#                             'status_INACTIVE', 'type_EMERGENCY_CENTER', 
#                             'type_INDUCTION_LOOP', 'type_SMART_PHONE', 'type_TRAFFIC_CAMERA', 
#                             'type_TRAFFIC_LIGHT', 'type_VEHICLE']

#     node_features = dataset[node_features_columns].values

#     src_labels = []

#     nodes_dict = {**{(row['device_id'], row['time']): row['situation_label'] for _, row in dataset.iterrows()}}

#     for u,  ts in zip(sources, timestamps):
#         src_label = nodes_dict.get((u, ts), -1) 
#         src_labels.append(src_label)

#     src_labels = np.array(src_labels)



#     src = torch.from_numpy(sources).to(torch.long)          # Maybe a problem?
#     t = torch.from_numpy(timestamps).to(torch.long)
#     source_node_features=torch.from_numpy(node_features).to(torch.float) 

#     path = get_in_memory_dataset_path()

    
#     data = TemporalData(src=src, dst=dst, t=t, msg=msg, y=y, source_node_features=source_node_features)
#     torch.save(InMemoryDataset.collate([data]), path)
#     data, slices = torch.load(path)
    
    
#     return data, slices


def process_node_classification_dataset(dataset,node_features, label):
    
    # destinations = dataset['i'].values
    # edge_idxs = dataset.index.values

    # edge_features = dataset[edge_features].values.reshape(-1, 1)
    
    

    sources = dataset['u'].values
    timestamps = dataset['ts'].values
    node_features = dataset[node_features].values
    dst_node_label = dataset[label].values


    # dst = torch.from_numpy(destinations).to(torch.long)
    # dst += int(src.max()) + 1                               # Maybe a problem?
    src = torch.from_numpy(sources).to(torch.long)
    node_features=torch.from_numpy(node_features).to(torch.float) 
    t = torch.from_numpy(timestamps).to(torch.long)
    y = torch.from_numpy(dst_node_label).to(torch.float)
    # msg = torch.from_numpy(edge_features).to(torch.float)


    path = get_in_memory_dataset_path()

    
    
    
    
    data = TensorDataset(src, t, node_features, y)
    # data = TemporalData(src=src, dst=dst, t=t, msg=msg, y=y, destination_node_features=node_features)
    # torch.save(InMemoryDataset.collate([data]), path)
    # data, slices = torch.load(path)
    
    
    return data
    return data, slices



def process_subgraph_dataset(dataset,node_features_attr, edge_features_attr, label):

    dataset
    
    subgraphs = []
        
    
    for ts, subgraphs_at_time_t in subgraphs.items():
        
        for subgraph in subgraphs_at_time_t:
            
            pyg_graph = from_networkx(subgraph)
            subgraphs.append(pyg_graph)
            
    return subgraphs
    
    
    
    
    # dataset_new[ts]
    # for ts, subgraphs_at_time_t in subgraphs.items():
    #     for subgraph in subgraphs_at_time_t:
        
    #             # timestamps.append(data.get(ts, 0))
            
    #         for u, v, data in subgraph.edges(data=True):
    #             nodes.append(u)
    #             node_features.append(subgraph.nodes[v].get(node_features_attr, []))
                
    #         subgraph_label.append(subgraph.graph['label'])
        
    
    

    # nodes = dataset['u'].values
    # timestamps = dataset['ts'].values
    # node_features = dataset[node_features].values
    # dst_node_label = dataset[label].values


    # # dst = torch.from_numpy(destinations).to(torch.long)
    # # dst += int(src.max()) + 1                               # Maybe a problem?
    # src = torch.from_numpy(nodes).to(torch.long)
    # node_features=torch.from_numpy(node_features).to(torch.float) 
    # t = torch.from_numpy(timestamps).to(torch.long)
    # y = torch.from_numpy(dst_node_label).to(torch.float)
    # # msg = torch.from_numpy(edge_features).to(torch.float)


    # path = get_in_memory_dataset_path()

    
    
    
    
    # data = TensorDataset(src, t, node_features, y)
    # data = TemporalData(src=src, dst=dst, t=t, msg=msg, y=y, destination_node_features=node_features)
    # torch.save(InMemoryDataset.collate([data]), path)
    # data, slices = torch.load(path)
    
    
  





def process_link_label_dataset(dataset, node_features, edge_features,label):
    sources = dataset['u'].values
    destinations = dataset['i'].values
    timestamps = dataset['ts'].values
    # edge_idxs = dataset.index.values

    sources = dataset['u'].values
    destinations = dataset['i'].values
    timestamps = dataset['ts'].values



    # node_features_columns = ['shape_status_DEFORMED', 
    #                      'shape_status_ORIGINAL_MANUFACTURED',  
    #                      'signal', 'speed', 'status_ACTIVE', 'status_ERROR', 
    #                      'status_INACTIVE', 'type_EMERGENCY_CENTER', 
    #                      'type_INDUCTION_LOOP', 'type_SMART_PHONE', 'type_TRAFFIC_CAMERA', 
    #                      'type_TRAFFIC_LIGHT', 'type_VEHICLE']

    # node_features = dataset[node_features].values
    edge_features = dataset[edge_features].values.reshape(-1, 1)
    edge_labels = dataset[label].values





    src = torch.from_numpy(sources).to(torch.long)
    dst = torch.from_numpy(destinations).to(torch.long)
    dst += int(src.max()) + 1                               # Maybe a problem?
    t = torch.from_numpy(timestamps).to(torch.long)
    y = torch.from_numpy(edge_labels).to(torch.float)
    msg = torch.from_numpy(edge_features).to(torch.float)

    # destination_node_features=torch.from_numpy(node_features).to(torch.float) 
    
    path = get_in_memory_dataset_path()

    data = TemporalData(src=src, dst=dst, t=t, msg=msg, y=y)
    # data = TemporalData(src=src, dst=dst, t=t, msg=msg, y=y)
    torch.save(InMemoryDataset.collate([data]), path)
    data, slices = torch.load(path)
    
    
    return data, slices


def remove_self_loops(dataset):
    data_array = dataset.to_numpy()

    u_idx = dataset.columns.get_loc('u')
    i_idx = dataset.columns.get_loc('i')

    filtered_array = data_array[data_array[:, u_idx] != data_array[:, i_idx]]
    filtered_df = pd.DataFrame(filtered_array, columns=dataset.columns)

    dataset = filtered_df
    return dataset



def get_temporal_data_loader(train_data, val_data, test_data, batch_size=32):
    
    train_loader = TemporalDataLoader(
        train_data,
        batch_size=batch_size,
        neg_sampling_ratio=1.0,
        )
    
    val_loader = TemporalDataLoader(
        val_data,
        batch_size=batch_size,
        neg_sampling_ratio=1.0,
        )
    
    test_loader = TemporalDataLoader(
        test_data,
        batch_size=batch_size,
        neg_sampling_ratio=1.0,
        )
    
    return train_loader, val_loader, test_loader


def get_temporal_classification_data_loader(train_data, val_data, test_data, batch_size=32):
    
    train_loader = TemporalDataLoader(
        train_data,
        batch_size=batch_size,
        # neg_sampling_ratio=1.0,
        )
    
    val_loader = TemporalDataLoader(
        val_data,
        batch_size=batch_size,
        # neg_sampling_ratio=1.0,
        )
    
    test_loader = TemporalDataLoader(
        test_data,
        batch_size=batch_size,
        # neg_sampling_ratio=1.0,
        )
    
    return train_loader, val_loader, test_loader