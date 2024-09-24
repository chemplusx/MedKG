import json
import time

import torch.nn.functional as F
import wandb
from sklearn.preprocessing import LabelEncoder
from torch.nn import Parameter
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm

from torch_geometric.nn import GAE, RGCNConv, RGCNConv, GATConv, GCNConv
import pandas as pd
import torch
from torch_geometric.data import Data
from sklearn.metrics import roc_auc_score
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

def parse_properties(property_string):
    try:
        return json.loads(property_string)
    except json.JSONDecodeError:
        return {}  # Return an empty dict if parsing fails

# Load nodes.csv
nodes_df = pd.read_csv(DATA_DIR + '\\nodes_dd.csv', encoding='ISO-8859-1')
node_mapping = {id: i for i, id in enumerate(nodes_df['id'])}
nodes_df['mapped_id'] = nodes_df['id'].map(node_mapping)
# Parse properties
nodes_df['parsed_properties'] = nodes_df['properties'].apply(parse_properties)

# Get all unique keys from the properties
all_keys = set()
for props in nodes_df['parsed_properties']:
    all_keys.update(props.keys())

# Initialize label encoders for categorical data
label_encoders = {key: LabelEncoder() for key in all_keys}

# Function to process a single property value
def process_property(value, key):
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        return float(label_encoders[key].fit_transform([value])[0])
    else:
        return 0.0

# Create a feature vector for each node
feature_vectors = []
for _, row in nodes_df.iterrows():
    props = row['parsed_properties']
    feature_vector = [process_property(props.get(key), key) for key in all_keys]
    feature_vectors.append(feature_vector)

# Convert to tensor
node_features = torch.tensor(feature_vectors, dtype=torch.float)



# Load edges.csv
edges_df = pd.read_csv(DATA_DIR + '\\edges_dd.csv', encoding='ISO-8859-1')
edges_df['source_mapped'] = edges_df['source'].map(node_mapping)
edges_df['target_mapped'] = edges_df['target'].map(node_mapping)
edge_index = torch.tensor([edges_df['source_mapped'].values, edges_df['target_mapped'].values], dtype=torch.long)
edge_type = torch.tensor(pd.Categorical(edges_df['type']).codes, dtype=torch.long)

num_nodes = len(node_mapping)
num_relations = edge_type.max().item() + 1

data = Data(
    x=node_features,
    edge_index=edge_index,
    edge_type=edge_type,
    num_nodes=num_nodes
)

# Split edges for training, validation, and testing
num_edges = edge_index.size(1)
perm = torch.randperm(num_edges)
train_edges = int(0.8 * num_edges)
valid_edges = int(0.1 * num_edges)

data.train_edge_index = edge_index[:, perm[:train_edges]]
data.train_edge_type = edge_type[perm[:train_edges]]

data.valid_edge_index = edge_index[:, perm[train_edges:train_edges+valid_edges]]
data.valid_edge_type = edge_type[perm[train_edges:train_edges+valid_edges]]

data.test_edge_index = edge_index[:, perm[train_edges+valid_edges:]]
data.test_edge_type = edge_type[perm[train_edges+valid_edges:]]

data = data.to(device)

class DeepRGCNEncoder(torch.nn.Module):
    def __init__(self, num_nodes, hidden_channels, num_relations, num_bases, num_layers):
        super().__init__()
        self.node_emb = torch.nn.Parameter(torch.empty(num_nodes, hidden_channels))
        self.convs = torch.nn.ModuleList()
        
        for i in range(num_layers//3):
            self.convs.append(GATConv(hidden_channels, hidden_channels, heads=4, concat=False))
        for i in range(num_layers):
            self.convs.append(GCNConv(hidden_channels, hidden_channels))
        for i in range(num_layers//3):
            self.convs.append(RGCNConv(hidden_channels, hidden_channels, num_relations, num_bases=num_bases))
                
        self.dropout = torch.nn.Dropout(0.2)
        self.reset_parameters()

    def reset_parameters(self):
        torch.nn.init.xavier_uniform_(self.node_emb)
        for conv in self.convs:
            conv.reset_parameters()

    def forward(self, edge_index, edge_type):
        x = self.node_emb
        for conv in self.convs:
            if isinstance(conv, RGCNConv):
                x = conv(x, edge_index, edge_type).relu()
            elif isinstance(conv, GATConv):
                x = conv(x, edge_index).relu()
            else:  # gcn
                edge_weight = torch.ones_like(edge_index[0]).float()
                x = conv(x, edge_index, edge_weight=edge_weight).relu()
            x = self.dropout(x)
        return x


class DistMultDecoder(torch.nn.Module):
    def __init__(self, num_relations, hidden_channels):
        super().__init__()
        self.rel_emb = Parameter(torch.empty(num_relations, hidden_channels))
        self.reset_parameters()

    def reset_parameters(self):
        torch.nn.init.xavier_uniform_(self.rel_emb)

    def forward(self, z, edge_index, edge_type):
        z_src, z_dst = z[edge_index[0]], z[edge_index[1]]
        rel = self.rel_emb[edge_type]
        return torch.sum(z_src * rel * z_dst, dim=1)

# Hyperparameters
hidden_channels = 500
num_bases = 30
learning_rate = 0.01
weight_decay = 1e-5

deep_model = GAE(
    DeepRGCNEncoder(data.num_nodes, hidden_channels, data.edge_type.max().item() + 1, num_bases, num_layers=8),
    DistMultDecoder(data.edge_type.max().item() + 1, hidden_channels),
).to(device)

optimizer = Adam(deep_model.parameters(), lr=learning_rate, weight_decay=weight_decay)
scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=5, verbose=True)


def negative_sampling(edge_index, num_nodes):
    # Sample edges by corrupting either the subject or the object of each edge.
    mask_1 = torch.rand(edge_index.size(1)) < 0.5
    mask_2 = ~mask_1

    neg_edge_index = edge_index.clone()
    neg_edge_index[0, mask_1] = torch.randint(num_nodes, (mask_1.sum(), ),
                                              device=neg_edge_index.device)
    neg_edge_index[1, mask_2] = torch.randint(num_nodes, (mask_2.sum(), ),
                                              device=neg_edge_index.device)
    return neg_edge_index


@torch.no_grad()
def compute_rank(ranks):
    # fair ranking prediction as the average
    # of optimistic and pessimistic ranking
    true = ranks[0]
    optimistic = (ranks > true).sum() + 1
    pessimistic = (ranks >= true).sum()
    return (optimistic + pessimistic).float() * 0.5


def margin_loss(pos_score, neg_score, margin=1.0):
    return F.relu(margin - pos_score + neg_score).mean()


def train(model, optimizer, data):
    model.train()
    optimizer.zero_grad()

    z = model.encode(data.edge_index, data.edge_type)
    pos_out = model.decode(z, data.train_edge_index, data.train_edge_type)

    neg_edge_index = negative_sampling(data.train_edge_index, data.num_nodes)
    neg_out = model.decode(z, neg_edge_index, data.train_edge_type)

    loss = margin_loss(pos_out, neg_out)
    loss.backward()
    optimizer.step()

    return float(loss), torch.cat([pos_out, neg_out]).detach().cpu().numpy(), \
        torch.cat([torch.ones_like(pos_out), torch.zeros_like(neg_out)]).cpu().numpy()


@torch.no_grad()
def test(model, data):
    model.eval()
    z = model.encode(data.edge_index, data.edge_type)

    pos_out = model.decode(z, data.test_edge_index, data.test_edge_type)
    neg_edge_index = negative_sampling(data.test_edge_index, data.num_nodes)
    neg_out = model.decode(z, neg_edge_index, data.test_edge_type)

    out = torch.cat([pos_out, neg_out])
    gt = torch.cat([torch.ones_like(pos_out), torch.zeros_like(neg_out)])

    return out.cpu().numpy(), gt.cpu().numpy()


def compute_auc(out, gt):
    return roc_auc_score(gt, out)


def compute_mrr(model, data):
    model.eval()
    z = model.encode(data.edge_index, data.edge_type)

    mrr_sum = 0
    num_edges = data.test_edge_index.size(1)

    for i in range(num_edges):
        src, dst = data.test_edge_index[:, i]
        rel = data.test_edge_type[i]

        # Score for the positive edge
        pos_score = model.decode(z, data.test_edge_index[:, i:i + 1], data.test_edge_type[i:i + 1])

        # Scores for negative edges (replace dst with all other nodes)
        neg_dst = torch.arange(data.num_nodes, device=device)
        neg_dst = neg_dst[neg_dst != dst]
        neg_edge_index = torch.stack([src.repeat(data.num_nodes - 1), neg_dst])
        neg_scores = model.decode(z, neg_edge_index, rel.repeat(data.num_nodes - 1))

        # Combine scores
        all_scores = torch.cat([pos_score, neg_scores])

        # Compute rank
        rank = (all_scores >= pos_score).sum().item()
        mrr_sum += 1.0 / rank

    return mrr_sum / num_edges


def predict_drug_disease_link(model, data, drug_id, disease_id):
    model.eval()
    with torch.no_grad():
        z = model.encode(data.edge_index, data.edge_type)

        # Get the node indices for the drug and disease
        drug_idx = node_mapping.get(drug_id)
        disease_idx = node_mapping.get(disease_id)

        if drug_idx is None or disease_idx is None:
            return None, "Drug or disease not found in the dataset"

        # Create edge index for this pair
        edge_index = torch.tensor([[drug_idx], [disease_idx]], dtype=torch.long, device=device)

        # Assume the edge type for drug-disease link (you may need to adjust this)
        edge_type = torch.tensor([0], dtype=torch.long, device=device)

        # Make prediction
        score = model.decode(z, edge_index, edge_type)

        return score.item(), "Prediction successful"

best_val_auc = 0
patience = 10
epochs_no_improve = 0
max_epochs = 500

with wandb.init(project="MedKG-GCN") as run:
    for epoch in range(1, max_epochs + 1):
        loss, train_out, train_gt = train(deep_model, optimizer, data)
        train_auc = compute_auc(train_out, train_gt)
        wandb.log({
            "epoch": epoch,
            "loss": loss,
            "train_auc": train_auc
        })

        if epoch % 50 == 0:
            test_out, test_gt = test(deep_model, data)
            test_auc = compute_auc(test_out, test_gt)
            test_mrr = compute_mrr(deep_model, data)
            print(f'Epoch: {epoch:05d}, Loss: {loss:.4f}, Train AUC: {train_auc:.4f}, '
                  f'Test AUC: {test_auc:.4f}, Test MRR: {test_mrr:.4f}')
            wandb.log({
                "test_auc": test_auc,
                "test_mrr": test_mrr
            })
            scheduler.step(test_auc)

            if test_auc > best_val_auc:
                best_val_auc = test_auc
                torch.save(deep_model.state_dict(), 'best_model.pth')
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve == patience:
                    print(f'Early stopping triggered after {epoch} epochs')
                    break
        else:
            print(f'Epoch: {epoch:05d}, Loss: {loss:.4f}, Train AUC: {train_auc:.4f}')

print(f"Best validation AUC: {best_val_auc:.4f}")