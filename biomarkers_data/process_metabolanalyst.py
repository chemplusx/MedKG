from neo4j import GraphDatabase
import os

# Neo4j connection details
uri = "bolt://localhost:7690"
username = "neo4j"
password = "password"


DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()


# Function to establish Neo4j connection
def get_neo4j_driver(uri, username, password):
    return GraphDatabase.driver(uri, auth=(username, password))

# Function to read Metabolite IDs from file
def read_metabolite_ids(filename):
    with open(filename, 'r') as file:
        metabolite_ids = [line.strip() for line in file if line.strip()]
    return metabolite_ids

# Function to insert relationships
def insert_relationships(driver, metabolite_ids, disease_name):
    with driver.session() as session:
        for metabolite_id in metabolite_ids:
            # Query to find Metabolite node by id
            result = session.run(
                "MATCH (m:Metabolite {id: $metabolite_id}) RETURN m",
                metabolite_id=metabolite_id
            )
            record = result.single()
            if record:
                metabolite_node = record['m']
                # Query to find Disease node by name
                result = session.run(
                    "MATCH (d:Disease {name: $disease_name}) RETURN d",
                    disease_name=disease_name
                )
                record = result.single()
                if record:
                    disease_node = record['d']
                    # Create relationship between Metabolite and Disease
                    session.run(
                        "MATCH (m:Metabolite), (d:Disease) WHERE id(m) = $metabolite_id AND id(d) = $disease_id "
                        "MERGE (m)-[:IS_A_BIOMARKER_OF]->(d)",
                        metabolite_id=metabolite_node._id,
                        disease_id=disease_node._id
                    )
                    print(f"Created relationship IS_A_BIOMARKER_OF between Metabolite {metabolite_id} and Disease {disease_name}")
                else:
                    print(f"Disease '{disease_name}' not found.")
            else:
                print(f"Metabolite with ID '{metabolite_id}' not found.")

# Example usage
if __name__ == "__main__":
    # Connect to Neo4j
    driver = get_neo4j_driver(uri, username, password)

    # Example file containing Metabolite IDs (one per line)
    metabolite_ids_file = DATA_DIR + '\\covid_markers.txt'

    # Read Metabolite IDs from file
    metabolite_ids = read_metabolite_ids(metabolite_ids_file)

    # Disease name to link to
    disease_name = 'COVID-19'

    # Insert relationships between Metabolites and Disease
    insert_relationships(driver, metabolite_ids, disease_name)

    # Close the Neo4j driver
    driver.close()
