

# Terminology

Node: In a graph, a node is an entity or instance. For example, in a social network, a node could represent a person.

Node Type: In a heterogeneous graph, nodes can have different types. For example, in a bibliographic network, node types might include "paper", "author", and "venue".

Node Feature: Each node in a graph can have one or multiple features. Node features are attributes or properties of a node, such as a user's age or a paper's text.

Edge Index: An edge index is a pair of node indices (source, target) representing directed edges in a graph. In PyTorch Geometric, edge indices are stored in a PyTorch tensor of shape [2, num_edges].

Edge Type: In a heterogeneous graph, edges can also have different types. For example, in a bibliographic network, edge types might include "cites" (connecting papers) or "written by" (connecting papers to authors).

Edge Attributes: These are properties or features associated with edges in a graph, similar to node features. For example, an edge attribute could be the "weight" of the relationship or a timestamp indicating when an interaction occurred.

Pooling Layer: In the context of graph neural networks, a pooling layer is a layer that reduces the graph structure into a fixed-size representation, which can then be used for tasks like graph classification.

Batch: A batch is a subset of the dataset that is used for a single update step during training. Using batches is more memory efficient than using the entire dataset at once, especially for large datasets.

Weights: Weights are the parameters of the neural network that are learned during training. They determine the importance of each input in the calculation of the outputs.

Bias: A bias is another parameter of the neural network, which is added to the product of inputs and weights. Bias allows for more flexibility in fitting the model to the data.

Hidden Layer: A hidden layer is a layer in the neural network between the input and output layers. Hidden layers extract and transform features from the input to aid in complex pattern recognition.

Input Layer: The input layer is the first layer of the network where the raw data is fed into the network.

Output Layer: The output layer is the last layer of the network where the final prediction or classification is made.

Batch Size: The batch size is the number of samples processed before the model is updated. The size of the batch can significantly impact the training process.

Optimizer: The optimizer is the algorithm used to adjust the parameters (weights and biases) of the network based on the gradients computed during backpropagation. Common optimizers include Stochastic Gradient Descent (SGD), RMSprop, and Adam.





### Preprocessing


#### Message passing from the target node to the source node

- <Author> <writes> <Paper>
- Paper passes it's embeddings into Authors




#### Automattically convert to heterogenuous graph

Add: 
``pythton
model = GAT(hidden_channels=64, out_channels=dataset.num_classes)
model = to_hetero(model, data.metadata(), aggr='sum') // Add this line to convert it to heterogenuous graph
``

Note: Address the NotImplementedError

Soluation
- 1. Transform to Undirected Graph 
- 2. Mannually configure edge_index, i.e.:

``python
data['paper', 'written_by', 'author'].edge_index = data['author', 'writes', 'paper'].edge_index.flip([0])
``

OR 

Use HGTConv (Heterogenuos Graph Transformer Convolution)


``python
fo r_ in range(num_layers):
    conv = HGTConv(in_channels, out_channels, num_types, num_relations, num_bases)
    self.convs.append(conv)
``
    
#### Defining Individual Layers of a Convolutional Graph Neural Network

Opportunities:
- Define the applied layer between the nodes
- Define the aggregation method
- Add the description in init and the forward method

``python

class HeteroGNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels, num_layers):
        super().__init__()

        self.convs = torch.nn.ModuleList()
        for _ in range(num_layers):
            conv = HeteroConv({
                ('paper', 'cites', 'paper'): GCNConv(-1, hidden_channels),
                ('author', 'writes', 'paper'): SAGEConv((-1, -1), hidden_channels),
                ('paper', 'rev_writes', 'author'): GATConv((-1, -1), hidden_channels),
            }, aggr='sum')
            self.convs.append(conv)

        self.lin = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict):
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {key: x.relu() for key, x in x_dict.items()}
        return self.lin(x_dict['author'])

model = HeteroGNN(hidden_channels=64, out_channels=dataset.num_classes,
                  num_layers=2)
``


#### Deal with varying number of input features of different node types in heterogeneous graphs
- Lazy Initialisiation: PyG can make use of lazy initialization to initialize parameters in heterogeneous GNNs (as denoted by -1 as the in_channels argument). This allows us to avoid calculating and keeping track of all tensor sizes of the computation graph.

``

``python
with torch.no_grad():  # Initialize lazy modules.
    out = model(data.x_dict, data.edge_index_dict)
``

When to use...



## Technical Implementations

torch.device('cuda' if torch.cuda.is_available() else 'cpu')