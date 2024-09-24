import obonet
from neo4j import GraphDatabase

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

def create_ontology_nodes(tx, graph):
    for node_id, data in graph.nodes(data=True):
        properties = {
            "id": node_id,
            "name": data.get("name", ""),
            "namespace": data.get("namespace", ""),
            "definition": data.get("def", ""),
            "is_obsolete": data.get("is_obsolete", False)
        }
        
        # Create node with "Term" label and properties
        tx.run("""
            CREATE (t:Uberon{id:$id}) 
            SET t = $properties
        """, id=node_id, properties=properties) # Change the label to "Entity Type"

def create_relationships(tx, graph):
    for node_id, data in graph.nodes(data=True):
        # Create "is_a" relationships
        is_a_relationships = data.get("is_a", [])
        for parent in is_a_relationships:
            tx.run("""
                MATCH (child:Uberon {id: $child_id}) 
                MATCH (parent:Uberon {id: $parent_id}) 
                MERGE (child)-[:IS_A]->(parent)
            """, child_id=node_id, parent_id=parent) # Change the label to "Entity Type"

def import_obo_to_neo4j(file_path):
    # Read the OBO file
    graph = obonet.read_obo(file_path)

    # Connect to Neo4j
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    with driver.session() as session:
        # Create ontology nodes
        # session.execute_write(create_ontology_nodes, graph)
        
        # Create relationships
        session.execute_write(create_relationships, graph)

    driver.close()
    print("Import completed successfully!")

# Usage
import_obo_to_neo4j("G:\\uberon-full.obo")