# Link Prediction in Medical Knowledge Graph

This project implements a Hybrid learning model for link prediction in a medical knowledge graph. It uses a combination of Graph Convolutional Networks (GCN), Graph Attention Networks (GAT), and Relational Graph Convolutional Networks (RGCN) to predict relationships between entities in the graph.

## Prerequisites

Before you begin, ensure you have met the following requirements:

* Python 3.8 or higher
* PyTorch 2.0 or higher
* PyTorch Geometric
* pandas
* scikit-learn
* wandb (for logging experiments)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/chemplusx/MedKG.git
   cd MedKG
   ```

2. Install the required packages:
   ```
   pip install torch torch-geometric pandas scikit-learn tqdm wandb
   ```
   
   or directly using the requirements.txt

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Prepare your data:
   - Place your `nodes_dd.csv` and `edges_dd.csv` files in the project directory or set the `MEDKG_DATA` environment variable to the directory containing these files.
   
   Data format requirements:
   
   a. Nodes file (`nodes_dd.csv`):
      - Format: id, label, properties
      - id: unique identifier for each node
      - label: category of the node (e.g., Drug, Disease)
      - properties: JSON string containing all relevant metadata for the node
   
   Example:
   ```
   id,label,properties
   MESH:D000001,Drug,{"name": "Aspirin", "molecular_weight": 180.16}
   MESH:C000001,Disease,{"name": "Headache", "icd10": "R51"}
   ```
   
   b. Edges file (`edges_dd.csv`):
      - Format: source, target, type
      - source: id of the source node (matching an id in the nodes file)
      - target: id of the target node (matching an id in the nodes file)
      - type: the relationship type between the source and target nodes
   
   Example:
   ```
   source,target,type
   MESH:D000001,MESH:C000001,treats
   MESH:D000002,MESH:C000001,may_treat
   ```

2. Run the link prediction model:
   ```
   python link_prediction.py
   ```

3. The script will train the model and output performance metrics (AUC and MRR) periodically. The best model will be saved as `best_model.pth`.

4. To use the trained model for predicting links between specific entities:

   ```python
   # Load the best model
   best_model = GAE(
       DeepRGCNEncoder(data.num_nodes, hidden_channels, data.edge_type.max().item() + 1, num_bases, num_layers=8),
       DistMultDecoder(data.edge_type.max().item() + 1, hidden_channels),
   ).to(device)
   best_model.load_state_dict(torch.load('best_model.pth'))

   # Predict a link
   drug_id = "your_drug_id"
   disease_id = "your_disease_id"
   score, message = predict_drug_disease_link(best_model, data, drug_id, disease_id)
   print(f"Prediction score: {score}")
   print(f"Message: {message}")
   ```

## Model Architecture

The model uses a combination of different graph neural network layers:
- Graph Attention Networks (GAT)
- Graph Convolutional Networks (GCN)
- Relational Graph Convolutional Networks (RGCN)

This combination allows the model to capture different aspects of the graph structure and relationships between entities.

## Performance

The model's performance is evaluated using the following metrics:
- Area Under the ROC Curve (AUC)
- Mean Reciprocal Rank (MRR)

## Logging

This project uses Weights & Biases (wandb) for experiment tracking. You can view your experiment results by creating an account at [wandb.ai](https://wandb.ai/) and logging in before running the script.
