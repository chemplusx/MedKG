from py2neo import Graph
import json

# Connect to Neo4j
graph = Graph("bolt://localhost:7690", auth=("neo4j", "password"))

# Load the JSON data
with open('hp.json', 'r') as f:
    data = json.load(f)

data = data['graphs'][0] # Get the first graph

# # Iterate over nodes and upsert them
for node in data['nodes']:
    node_id = node['id']
    link = node_id
    node_id = node_id.replace('http://purl.obolibrary.org/obo/', '') # Remove the prefix
    node_id = node_id.replace('_', ':') # Replace underscore with colon

    if node_id == "" or not node_id:
        continue

    lbl = node['lbl']
    node_type = "Phenotype"  # Since you want to store them as Phenotype
    definition = node.get('meta', {}).get('definition', {}).get('val', '')
    synonyms = node.get('meta', {}).get('synonyms', [])
    xref = node.get('meta', {}).get('xrefs', [])

    link = node_id
    node_id = node_id.replace('http://purl.obolibrary.org/obo/', '') # Remove the prefix
    node_id = node_id.replace('_', ':') # Replace underscore with colon

    # Convert the synonyms and xref to strings
    xref = ', '.join([i['val'] for i in xref])
    references = ', '.join([str(i['xrefs']) for i in synonyms if 'xrefs' in i])
    synonyms = ', '.join([i['val'] for i in synonyms])

    

    # Create or update the node
    graph.run(
        """
        MERGE (n:Phenotype {id: $node_id})
        ON CREATE SET n.name = $lbl, n.description = $desc, n.synonyms = $synonyms, n.xref = $xref, n.references = $references, n.link = $link
        ON MATCH SET n.name = $lbl, n.description = $desc, n.synonyms = $synonyms, n.xref = $xref, n.references = $references, n.link = $link
        """,
        node_id=node_id, lbl=lbl, desc=definition, synonyms=synonyms, xref=xref, references=references, link=link
    )

# Iterate over edges and upsert them
for edge in data['edges']:
    sub = edge['sub']
    sub = sub.replace('http://purl.obolibrary.org/obo/', '') # Remove the prefix
    sub = sub.replace('_', ':') # Replace underscore with colon

    obj = edge['obj']
    obj = obj.replace('http://purl.obolibrary.org/obo/', '') # Remove the prefix
    obj = obj.replace('_', ':') # Replace underscore with colon

    pred = edge['pred'].upper()
    
    if pred == 'IS_A':
        pred = 'HAS_PARENT'

    # Create or update the relationship
    graph.run(
        """
        MATCH (a:Phenotype {id: $sub})
        MATCH (b:Phenotype {id: $obj})
        MERGE (a)-[r:%s]->(b)
        """ % pred,
        sub=sub, obj=obj
    )
