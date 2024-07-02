from neo4j import GraphDatabase
import csv, os


DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()


# Neo4j connection parameters
uri = "bolt://localhost:7690"
username = "neo4j"
password = "password"

# Function to connect to Neo4j database
def connect_to_db(uri, username, password):
    return GraphDatabase.driver(uri, auth=(username, password))

# Function to process the TSV file and update Neo4j
def process_tsv_file(file_path, driver):
    with open(file_path, mode='r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            # Extract data from the row
            biomarker_type = row['biomarker_type']
            name = row['name']
            hmdb_id = row['hmdb_id']
            condition = row['conditions']
            indication_types = row['indication_types']
            concentration = row['concentration']
            age = row['age']
            sex = row['sex']
            biofluid = row['biofluid']
            citation = row['citation']
            
            # # Skip entries with 'Normal' condition
            # if condition.lower() == 'normal':
            #     continue
            
            # Open session to execute Neo4j queries
            with driver.session() as session:
                # Query to find Metabolite node by hmdb_id
                if condition == 'Normal':
                    # state_values = {
                    #     "concentration": concentration,
                    #     "age": age,
                    #     "sex": sex,
                    #     "biofluid": biofluid,
                    #     "citation": citation
                    # }

                    state_values = f"age: {age},\n sex: {sex},\n biofluid: {biofluid},\n concentration: {concentration},\n citation: {citation}"
                    metabolite_query = (
                        "MERGE (m:Metabolite {id: $hmdb_id}) "
                        "ON CREATE SET m.name = $hmdb_id, "
                        "m.name = $name, "
                        "m.biomarker_type = $biomarker_type, "
                        "m.biomarker_normal_state_values = coalesce(m.biomarker_normal_state_values, []) + $state_values "
                        "ON MATCH SET m.biomarker_type = $biomarker_type, "
                        "m.biomarker_normal_state_values = coalesce(m.biomarker_normal_state_values, []) + $state_values "
                        "RETURN m"
                    )
                    # Execute the queries
                    result = session.run(metabolite_query, hmdb_id=hmdb_id,
                        name=name, biomarker_type=biomarker_type,
                        state_values=state_values
                    )
                    continue
                else:
                    metabolite_query = (
                        "MERGE (m:Metabolite {id: $hmdb_id}) "
                        "ON CREATE SET m.name = $hmdb_id, "
                        "m.name = $name, "
                        "m.biomarker_type = $biomarker_type "
                        "ON MATCH SET m.biomarker_type = $biomarker_type "
                        "RETURN m"
                    )
                    # Execute the queries
                    result = session.run(metabolite_query, hmdb_id=hmdb_id,
                        name=name, biomarker_type=biomarker_type
                        )
                
                
                metabolite_node = result.single()[0]

                # Query to find or create Disease node by name
                disease_query = (
                    "MATCH (d:Disease) where d.name =~ $condition "
                    "RETURN d"
                )

                # Execute the queries
                regex_condition = f"(?i){condition}"
                result = session.run(disease_query, condition=regex_condition)
                if result.peek() is None:
                    print(f"No Disease node for {condition}")
                    continue
                disease_node = result.single()[0]

                if not disease_node or not metabolite_node:
                    print(f"Metabolite or Disease not found for {hmdb_id} and {condition}. Disease: {disease_node}, Metabolite: {metabolite_node}")
                    continue
                
                # Query to create IS_A_BIOMARKER_OF relationship with properties
                state_values = f"age: {age},\n sex: {sex},\n biofluid: {biofluid},\n concentration: {concentration},\n citation: {citation}"
                relationship_query = (
                    "MATCH (m:Metabolite {id: $hmdb_id}), (d:Disease) where id(d) = $internal_id "
                    "MERGE (m)-[r:IS_A_BIOMARKER_OF]->(d) "
                    "SET r.indication_type = $indication_types, "
                    "r.state_values = coalesce(r.state_values, []) + $state_values "
                )
                
                # # Execute the queries
                # result = session.run(metabolite_query, hmdb_id=hmdb_id)
                # metabolite_node = result.single()[0]
                
                # session.run(disease_query, condition=condition)
                
                session.run(relationship_query, hmdb_id=hmdb_id, internal_id=disease_node._id,
                           state_values=state_values, indication_types=indication_types)

# Example usage:
file_path = DATA_DIR + '\\all_diagnostic_chemicals.tsv'  # Replace with your file path

# Connect to Neo4j
driver = connect_to_db(uri, username, password)

# Process the TSV file and update Neo4j database
process_tsv_file(file_path, driver)

# Close the Neo4j driver
driver.close()
