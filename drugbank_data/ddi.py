from neo4j import GraphDatabase
import csv
import os

class DrugInteractionLoader:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def create_or_update_interaction(self, tx, drug1_id, drug2_id, interaction_desc):
        # Match drugs and either find existing relationship or create new one
        query = """
        MATCH (d1:Drug {drugbank_id: $drug1_id})
        MATCH (d2:Drug {drugbank_id: $drug2_id})
        MATCH (d1)-[r]-(d2)
        SET r.description = CASE
            WHEN r.description IS NULL THEN $interaction_desc
            WHEN NOT r.description CONTAINS $interaction_desc 
            THEN r.description + '; ' + $interaction_desc
            ELSE r.description
        END
        """
        # First try to update existing relationship
        result = tx.run(query, drug1_id=drug1_id, 
                       drug2_id=drug2_id,
                       interaction_desc=interaction_desc)
        
        # If no relationship exists (no records affected), create new one
        if result.consume().counters.properties_set == 0:
            create_query = """
            MATCH (d1:Drug {drugbank_id: $drug1_id})
            MATCH (d2:Drug {drugbank_id: $drug2_id})
            CREATE (d1)-[r:INTERACTS_WITH {description: $interaction_desc}]->(d2)
            """
            tx.run(create_query, drug1_id=drug1_id,
                  drug2_id=drug2_id,
                  interaction_desc=interaction_desc)

    def load_interactions_from_csv(self, file_path):
        count = 0
        with self.driver.session() as session:
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    session.execute_write(
                        self.create_or_update_interaction,
                        row['drugbank_id'],
                        row['interaction_drugbank_id'],
                        row['interaction_description']
                    )
                    count += 1
                    if count % 1000 == 0:
                        print(f"Processed {count} interactions")

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = "H:\\workspace\\MedKG\\data\\" #os.getcwd()

def main():
    # Replace with your Neo4j connection details
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "password"
    
    # CSV file path
    csv_file = DATA_DIR+"\\drug_interactions.csv"
    
    try:
        # Initialize the loader
        loader = DrugInteractionLoader(uri, username, password)
        
        # Load interactions
        print("Starting to load drug interactions...")
        loader.load_interactions_from_csv(csv_file)
        print("Successfully loaded drug interactions!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        # Close the connection
        loader.close()

if __name__ == "__main__":
    main()