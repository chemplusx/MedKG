import plotly.graph_objects as go
import plotly.io as pio
import plotly.offline as pyo
import plotly.colors as colors
import pandas as pd

# Example data
source = ["Disease", "Tissue", "Biological_process", "Molecular_function", "Cellular_component", "Modification", "Phenotype", "Experiment", "Experimental_factor", "Units", "Experimental_factor", "Experimental_factor", "Transcript", "Gene", "Protein", "Peptide", "Gene", "Transcript", "Protein", "Protein", "Protein", "Project", "Project", "User", "Project", "Biological_sample", "Biological_sample", "Analytical_sample", "Modified_protein", "Protein", "Peptide", "Modified_protein", "Protein", "Complex", "Protein", "Protein", "Protein", "Analytical_sample", "Metabolite", "Drug", "Compound", "Drug", "Known_variant", "Known_variant", "Known_variant", "Known_variant", "Clinically_relevant_variant", "Disease", "Tissue", "Protein", "Cellular_component", "Modified_protein", "Functional_region", "Functional_region", "Metabolite", "Protein", "Known_variant", "GWAS_study", "Protein", "Metabolite", "GWAS_study"]
target = ["Disease", "Tissue", "Biological_process", "Molecular_function", "Cellular_component", "Modification", "Phenotype", "Experiment", "Experimental_factor", "Units", "Disease", "Phenotype", "Chromosome", "Transcript", "Amino_acid_sequence", "Protein", "Protein", "Protein", "Cellular_component", "Molecular_function", "Biological_process", "Disease", "Tissue", "Project", "Subject", "Subject", "Analytical_sample", "Protein", "Modification", "Modified_protein", "Modified_protein", "Protein", "Complex", "Biological_process", "Protein", "Disease", "Tissue", "Modified_protein", "Disease", "Protein", "Compound", "Disease", "Chromosome", "Gene", "Protein", "Clinically_relevant_variant", "Disease", "Publication", "Publication", "Publication", "Publication", "Publication", "Protein", "Publication", "Protein", "Protein_structure", "GWAS_study", "Experimental_factor", "Pathway", "Pathway", "Publication"]
value = [14897, 4313, 52886, 13574, 4845, 3569, 24316, 2967, 10800, 412, 2056, 233, 295912, 258487, 20614, 3629058, 172019, 202275, 3660177, 80319, 158067, 7, 7, 14, 169, 170, 172, 797651, 21407, 21339, 82, 994, 10968, 4770, 3244505, 7082494, 6529475, 224478, 25207, 30052, 11609, 46804, 10630108, 10638935, 26818166, 169, 4555, 25506946, 51007551, 11696880, 22895232, 194, 204244, 2435, 861626, 195640, 16128, 9250, 354967, 848842, 3939]

# Read a csv file with thre colums: source, target, value

# Read the data from the csv file
data = pd.read_csv('D:\\workspace\\MedKG\\visualize\\total-relations.csv', header=0)

# Extract the source, target, and value columns
source = data['s'].tolist()[13:]
target = data['t'].tolist()[13:]
value = data['r'].tolist()[13:]


# Create a mapping of unique labels to indices
all_nodes = list(set(source + target))
node_indices = {node: i for i, node in enumerate(all_nodes)}

# Convert source and target to indices
source_indices = [node_indices[s] for s in source]
target_indices = [node_indices[t] for t in target]

colorscale = colors.qualitative.Set3
node_colors = colorscale[:len(all_nodes)]  # Automatically pick distinct colors

# Create the Sankey diagram with improved styling
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,  # Increase padding between nodes
        thickness=30,  # Increase node thickness
        line=dict(color="black", width=1.5),
        label=all_nodes,
        color=node_colors  # Assign custom colors
    ),
    link=dict(
        source=source_indices,
        target=target_indices,
        value=value,
        color='rgba(63, 81, 181, 0.5)',  # Set a uniform color with transparency for links
        hoverlabel=dict(bgcolor='white')  # Customize hover label background
    )
)])

# Update layout with custom styling
fig.update_layout(
    title_text="Enhanced Sankey Diagram",
    font_size=12,  # Increase font size for better readability
    title_font_size=20,  # Make the title more prominent
    height=600,  # Increase the height of the figure for better spacing
    margin=dict(l=20, r=20, t=50, b=20)  # Adjust margins for a tighter layout
)

pyo.plot(fig, filename='sankey_diagram.html')
fig.show()

import time
time.sleep(10)