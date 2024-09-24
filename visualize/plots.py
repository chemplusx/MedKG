# PLot the metrics data generated from medlink run

import matplotlib.pyplot as plt
import pandas as pd

# Read the CSV data
data = pd.read_csv('../metrics/loss.csv')

# Create the plot
plt.figure(figsize=(14, 8))
plt.plot(data['Step'], data['Conventional RGCN - loss'], label='Conventional RGCN')
plt.plot(data['Step'], data['Med-LINK - loss'], label='MedLINK')

# Customize the plot
plt.title('Training Loss Comparison: Conventional RGCN vs MedLINK')
plt.xlabel('Epoch', fontsize=16)
plt.ylabel('Loss', fontsize=16)
plt.legend(fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Increase tick label size
plt.tick_params(axis='both', which='major', labelsize=12)

# Show the plot
plt.tight_layout()
plt.show()

# Now for Test AUC

data = pd.read_csv('../metrics/test_auc.csv')

# Create the plot
plt.figure(figsize=(14, 8))
plt.plot(data['Step'], data['Conventional RGCN - test_auc'], label='Conventional RGCN')
plt.plot(data['Step'], data['Med-LINK - test_auc'], label='MedLINK')

# Customize the plot
plt.title('Test AUC Comparison: Conventional RGCN vs MedLINK')
plt.xlabel('Epoch', fontsize=16)
plt.ylabel('Test AUC (ROC)', fontsize=16)
plt.legend(fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Increase tick label size
plt.tick_params(axis='both', which='major', labelsize=12)

# Show the plot
plt.tight_layout()
plt.show()


# Now for Train AUC

data = pd.read_csv('../metrics/train_auc.csv')

# Create the plot
plt.figure(figsize=(14, 8))
plt.plot(data['Step'], data['Conventional RGCN - train_auc'], label='Conventional RGCN')
plt.plot(data['Step'], data['Med-LINK - train_auc'], label='MedLINK')

# Customize the plot
plt.title('Train AUC Comparison: Conventional RGCN vs MedLINK')
plt.xlabel('Epoch', fontsize=16)
plt.ylabel('Train AUC (ROC)', fontsize=16)
plt.legend(fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Increase tick label size
plt.tick_params(axis='both', which='major', labelsize=12)

# Show the plot
plt.tight_layout()
plt.show()


# Now for Test MRR
data = pd.read_csv('../metrics/test_mrr.csv')

# Create the plot
plt.figure(figsize=(14, 8))
plt.plot(data['Step'], data['Conventional RGCN - test_mrr'], label='Conventional RGCN')
plt.plot(data['Step'], data['Med-LINK - test_mrr'], label='MedLINK')

# Customize the plot
plt.title('Test MRR Comparison: Conventional RGCN vs MedLINK')
plt.xlabel('Epoch', fontsize=16)
plt.ylabel('Test MRR', fontsize=16)
plt.legend(fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Increase tick label size
plt.tick_params(axis='both', which='major', labelsize=12)

# Show the plot
plt.tight_layout()
plt.show()


# Optionally, save the plot as an image file
# plt.savefig('loss_comparison_plot.png', dpi=300, bbox_inches='tight')
