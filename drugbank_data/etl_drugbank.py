from neo4j import GraphDatabase
import json
import os

# Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# Function to handle database operations
class Neo4jHandler:
    def __init__(self, uri, username, password):
        self._driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self._driver.close()

    def insert_or_update_drug(self, drug_data):
        with self._driver.session() as session:
            result = session.write_transaction(self._insert_or_update_drug, drug_data)
            return result

    @staticmethod
    def _insert_or_update_drug(tx, drug_data):
        drug_name = drug_data['name']
        # Check if the drug already exists in the database
        result = tx.run("MATCH (d:Drug {name: $drug_name}) RETURN d", drug_name=drug_name)
        
        if result.single():
            # Update existing node with any missing properties
            update_query = (
                "MATCH (d:Drug {name: $drug_name}) "
                "SET d += $properties "
                "RETURN d"
            )
            properties = {k: v for k, v in drug_data.items() if k != 'drugbank_id'}
            tx.run(update_query, drug_name=drug_name, properties=properties)
            return f"Updated drug with drugbank_name: {drug_name}"
        else:
            # Create new node
            create_query = (
                "CREATE (:Drug $properties)"
            )
            tx.run(create_query, properties=drug_data)
            return f"Created new drug with drugbank_name: {drug_name}"

def main():
    # Read JSON data from file
    with open(DATA_DIR + 'drug_data.json', 'r', encoding='utf-8') as file:
        drug_data_list = json.load(file)
    
    # Initialize Neo4j handler
    neo4j_handler = Neo4jHandler(uri, username, password)

    # Process each drug data
    for drug_data in drug_data_list:
        result = neo4j_handler.insert_or_update_drug(drug_data)
        print(result)

    # Close Neo4j connection
    neo4j_handler.close()

if __name__ == "__main__":
    main()
