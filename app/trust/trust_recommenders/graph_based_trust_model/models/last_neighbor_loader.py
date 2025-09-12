import copy
from typing import Callable, Dict, Tuple

import torch
from torch import Tensor
from torch.nn import GRUCell, Linear
 

from torch_geometric.nn.inits import zeros
from torch_geometric.utils import scatter
from torch_geometric.utils._scatter import scatter_argmax

TGNMessageStoreType = Dict[int, Tuple[Tensor, Tensor, Tensor, Tensor]]



class LastNeighborLoader:
    def __init__(self, num_nodes: int, size: int, device=None):
        self.size = size

        # (rows, column)
        #shape [300, 10]
        self.neighbors = torch.empty((num_nodes, size), dtype=torch.long,
                                     device=device)
        self.e_id = torch.empty((num_nodes, size), dtype=torch.long,
                                device=device)
        self._assoc = torch.empty(num_nodes, dtype=torch.long, device=device)

        self.reset_state()

    # e_id = Event ID
    # n_id = Batch ID
    def __call__(self, n_id: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
        # Gets the neighbors of both nodes (2, 10)
        neighbors = self.neighbors[n_id]
        
        # nodes = (columns of node interactions, 2) - 2  is due to repeat(1)
        nodes = n_id.view(-1, 1).repeat(1, self.size)
        
        # 2D vecotr with shape [row -> num_nodes, columns -> size] -> returns the event ids of the last 10 interactions
        e_id = self.e_id[n_id]

        # Filter invalid neighbors (identified by `e_id < 0`).
        mask = e_id >= 0
        neighbors, nodes, e_id = neighbors[mask], nodes[mask], e_id[mask]
        
        

        # Relabel node indices. Basically n_id receives the [[src,dst], [num_nodes -> 300, size -> 10]]
        n_id = torch.cat([n_id, neighbors]).unique()
        
        # Helping vector with shape [row -> num_nodes, columns -> 1] -> returns the index of the node
        temp = n_id.size(0)
        self._assoc[n_id] = torch.arange(temp, device=n_id.device)
        
        
        neighbors, nodes = self._assoc[neighbors], self._assoc[nodes]
        edge_index = torch.stack([neighbors, nodes])
        return n_id, edge_index, e_id
    
    def load(self, n_id: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
        
        neighbors = self.neighbors[n_id]
        nodes = n_id.view(-1, 1).repeat(1, self.size)
        e_id = self.e_id[n_id]

        # Filter invalid neighbors (identified by `e_id < 0`).
        mask = e_id >= 0
        neighbors, nodes, e_id = neighbors[mask], nodes[mask], e_id[mask]

        # Relabel node indices.
        n_id = torch.cat([n_id, neighbors]).unique()
        self._assoc[n_id] = torch.arange(n_id.size(0), device=n_id.device)
        neighbors, nodes = self._assoc[neighbors], self._assoc[nodes]

        return n_id, torch.stack([neighbors, nodes]), e_id

    def insert(self, src: Tensor, dst: Tensor):
        # Inserts newly encountered interactions into an ever-growing
        # (undirected) temporal graph.

        # Collect central nodes, their neighbors and the current event ids.
        neighbors = torch.cat([src, dst], dim=0)
        
        
        nodes = torch.cat([dst, src], dim=0)
        
        end_point = src.size(0)
        temp = self.cur_e_id + end_point 
        # src.size(0) => 1 ( increase the number of cur_e_id by 1)
        e_id = torch.arange(self.cur_e_id, temp,
                            device=src.device).repeat(2)
        
        
        # Increase the number of cur_e_id by the number of elements in src with is supposed to be always 1
        self.cur_e_id += src.numel()

        # Convert newly encountered interaction ids so that they point to
        # locations of a "dense" format of shape [num_nodes, size].
        # Returns the node position and the permutation vector( which is the index of the node before the shift)
        nodes, perm = nodes.sort()
        
        # Get neighbor of the destination nodes
        neighbors, e_id = neighbors[perm], e_id[perm]
        
        # (lower_node_id, higher_node_id) -> (higher_node_id, lower_node_id)
        n_id = nodes.unique()

        # numel = number of elements(represents the number of nodes)
        self._assoc[n_id] = torch.arange(n_id.numel(), device=n_id.device)

        # Number of columns division of the number of nodes by the size of the matrix to compute the Id of the offset
        dense_id = torch.arange(nodes.size(0), device=nodes.device) % self.size
        
        # Multiply the dense_id by the number of nodes
        dense_id += self._assoc[nodes].mul_(self.size)

        # Create a dense matrix with shape [num_nodes, size] and fill it with -1
        dense_e_id = e_id.new_full((n_id.numel() * self.size, ), -1)
        
        # Fill the matrix with the event ids
        dense_e_id[dense_id] = e_id
        
        # Reshape the matrix to [num_nodes, size]
        dense_e_id = dense_e_id.view(-1, self.size)

        # Create a dense matrix with shape [num_nodes, size] and fill it with -1
        dense_neighbors = e_id.new_empty(n_id.numel() * self.size)
        
        # Fill the matrix with the neighbors
        dense_neighbors[dense_id] = neighbors
        
        # Reshape the matrix to [num_nodes, size]
        dense_neighbors = dense_neighbors.view(-1, self.size)

        # Collect new and old interactions...
        e_id = torch.cat([self.e_id[n_id, :self.size], dense_e_id], dim=-1)
        
        # ...and their neighbors.
        # ... contains the neighbors of the last n interactions 
        neighbors = torch.cat(
            [self.neighbors[n_id, :self.size], dense_neighbors], dim=-1)

        # And sort them based on `e_id`.
        # Get the last n interactions of the node
        e_id, perm = e_id.topk(self.size, dim=-1)
        
        #
        self.e_id[n_id] = e_id
        
        
        self.neighbors[n_id] = torch.gather(neighbors, 1, perm)

    def reset_state(self):
        self.cur_e_id = 0
        self.e_id.fill_(-1)
