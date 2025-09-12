
import pathlib
import sys

from core.models.devices.common import DeviceType
sys.path.insert(0, '/app')

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import os

from dataset_builder.utils.path_helper import DatasetType, get_dataset_path, get_graph_images_timeslot_output_path, get_image_output_directory
import matplotlib.patches as mpatches


def setup_plot():
    plt.figure(figsize=(24, 24))


def draw_nodes(G, node_positions, node_colors, target_labels,time_slice):
    
    node_shapes = get_node_shapes(time_slice)
    
    for shape, marker in zip(set(node_shapes), ['o', 's', 'v', '^', '<', '>']):
        nx.draw_networkx_nodes(G, pos=node_positions, nodelist=[node for node, shape_ in zip(G.nodes(), node_shapes) if shape_ == shape], node_shape=marker, node_color='none', linewidths=2)
    
    border_colors = ['white' if label == 0 else 'red' for label in target_labels]
    nx.draw_networkx_nodes(G, pos=node_positions, node_color=node_colors, node_shape='o', node_size=300)
    nx.draw_networkx_nodes(G, pos=node_positions, node_color='none', edgecolors=border_colors, node_shape='o', node_size=400, linewidths=2)

def draw_labels(G, node_positions):
    label_positions = {}
    dx = 0.05
    dy = 0.05
    for node, (x, y) in node_positions.items():
        label_positions[node] = (x + dx, y + dy)
    nx.draw_networkx_labels(G, pos=label_positions)

def save_plot(time, output_directory):
    
    
    plt.text(160, 160, f'Time: {time}', fontsize=12)
    legend_labels = get_legend_labels()
    plt.legend(handles=legend_labels)
    
    
    plt.xticks(range(150, 1101, 100))
    plt.yticks(range(150, 1101, 100))
    plt.xlim(150, 1100)
    plt.ylim(150, 1100)
    plt.axis([150, 1100, 150, 1100])
    
    filepath = os.path.join(output_directory, f'graph_{time}.png')
    directory = pathlib.Path(filepath).parent.resolve()
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(filepath)
    plt.close()

def visualize_node_classification_graph(G, target_labels, node_positions, time, label_names, output_directory,time_slice):
    node_colors = get_node_colors(G,time_slice)
    
    
    setup_plot()

    draw_nodes(G, node_positions, node_colors, target_labels,time_slice)
    draw_labels(G, node_positions,label_names)
    save_plot(time, output_directory)



def get_legend_labels():
    legend_labels = [
        # mpatches.Patch(color='red', label='Emergency Vehicle'),
        mpatches.Patch(color='green', label='Induction Loop'),
        mpatches.Patch(color='blue', label='Smart Phone'),
        mpatches.Patch(color='purple', label='Traffic Camera'),
        mpatches.Patch(color='yellow', label='Traffic Light'),
        mpatches.Patch(color='orange', label='Vehicle'),
        mpatches.Patch(color='grey', label='Other')
    ]
    
    return legend_labels

def get_node_shapes(df_time_slice):
    node_shapes = []
    for _, row in df_time_slice.iterrows():
        if row['shape_status_DEFORMED']:
            node_shapes.append('o')
        # elif row['shape_status_DENTS']:
        #     node_shapes.append('s')
        # elif row['shape_status_HEAVILY_DAMAGED']:
            # node_shapes.append('v')
        elif row['shape_status_ORIGINAL_MANUFACTURED']:
            node_shapes.append('^')
        # elif row['shape_status_SCRATCHES']:
        #     node_shapes.append('<')
        else:
            node_shapes.append('>')
    return node_shapes

def get_node_colors(G : nx.Graph ,df_time_slice=None,scenario_identification=True):
    
    node_colors = []
    
    if scenario_identification:
    
        for node in G.nodes():
            row = df_time_slice[df_time_slice['device_id'] == node].iloc[0]
            # if row['type_EMERGENCY_VEHICLE']:
            #     node_colors.append('red')
            if row['type_INDUCTION_LOOP']:
                node_colors.append('green')
            elif row['type_SMART_PHONE']:
                node_colors.append('blue')
            elif row['type_TRAFFIC_CAMERA']:
                node_colors.append('purple')
            elif row['type_TRAFFIC_LIGHT']:
                node_colors.append('yellow')
            elif row['type_VEHICLE']:
                node_colors.append('orange')
            else:
                node_colors.append('grey')
    
    elif not scenario_identification:
        for node_id, node in G.nodes(data=True):
            
            # node_ = G.nodes[node]
            
            # device_type = node[1]['device_type']
            device_type = node['device_type']
            
            if device_type == DeviceType.INDUCTION_LOOP:
                node_colors.append('green')
            elif device_type == DeviceType.SMART_PHONE:
                node_colors.append('blue')
            elif device_type == DeviceType.TRAFFIC_CAMERA:
                node_colors.append('purple')
            elif device_type == DeviceType.TRAFFIC_LIGHT:
                node_colors.append('yellow')
            elif device_type == DeviceType.VEHICLE:
                node_colors.append('orange')
            elif device_type == DeviceType.EMERGENCY_CENTER:
                node_colors.append('red')
            else:
                node_colors.append('grey')
            
    
    return node_colors
    # plt.show()
    
def visualize_edge_prediction_graph(G, target_labels, node_positions, time):
    # Your code for visualizing edge prediction graphs
    pass
    

def visualize_graph(G, target_labels, node_positions, time, dataset_type, label_names,output_directory,df_time_slice):
    if dataset_type == 'node_classification':
        visualize_node_classification_graph(G, target_labels, node_positions, time,label_names,output_directory,df_time_slice)
        
    elif dataset_type == 'edge_prediction':
        G = add_edge_attributes(df_time_slice, G)
        visualize_edge_prediction_graph(G, target_labels, node_positions, time,label_names)

def get_node_positions(df_time_slice):
    node_positions = {}
    for index, row in df_time_slice.iterrows():
        node_positions[row['device_id']] = (row['longitude'],row['latitude'])
    return node_positions

def add_edge_attributes(df_time_slice, G):
    for index, row in df_time_slice.iterrows():
        u, v = row['u'], row['i']
        distance = row['distance']
        G.add_edge(u, v, edge_attr=distance)
    return G

def add_nodes_to_graph(df_time_slice, G):
    for index, row in df_time_slice.iterrows():
        G.add_node(row['device_id'])
    return G

from concurrent.futures import ThreadPoolExecutor

def visualize_time_slice(time):

    df_time_slice = df_dataset[df_dataset['time'] == time]
    G = nx.Graph()
    G = add_nodes_to_graph(df_time_slice, G)
    
    
    target_label = df_time_slice['situation_label'].values
    label_names = {device_id: device_name for device_id, device_name in zip(df_time_slice['device_id'].values, df_time_slice['device_name'].values)}
    node_positions = get_node_positions(df_time_slice)
    
    output_directory = get_image_output_directory(DATASET_TYPE, BUILD_DEVICE)
    
    visualize_graph(G, target_labels=target_label, node_positions=node_positions, time=time, dataset_type='node_classification', label_names=label_names,output_directory=output_directory,df_time_slice=df_time_slice)

# Main part of the code
if __name__ == "__main__":
    BUILD_DEVICE = 'local'
    DATASET_TYPE= DatasetType.NODE_CLASSIFICATION_SITUATION_LABELS
    
    dataset_path = get_dataset_path(BUILD_DEVICE)
    dataset_path = '/app/scenario_identification/data/iot-unsw_node_classification'
    dataset_name = 'ml_iot-unsw_situation_labels.csv'
    csv_dataset = os.path.join(dataset_path, dataset_name)
    df_dataset = pd.read_csv(csv_dataset)
    unique_timesteps = df_dataset['time'].unique()
    
    
    for time in unique_timesteps:
        
        visualize_time_slice(time)
        
