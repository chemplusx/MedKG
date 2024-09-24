from neo4j import GraphDatabase, basic_auth
import json
import os

# Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

# Function to handle database operations
class Neo4jHandler:
    def __init__(self, uri, username, password):
        self._driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))
    
    def close(self):
        self._driver.close()
    
    def create_or_update_drug_and_protein(self, data):
        with self._driver.session() as session:
            for entry in data:

                drug_name = entry['drug_name']
                drugbank_id = entry['drugbank_id']
                for target in entry['targets']:
                    target_name = target['target_name']
                    polypeptide_id = target['polypeptide_id']
                    specific_function = target['specific_function']
                    general_function = target['general_function']
                    organism = target['organism']
                    accession = target['uniprot_accession']
                    molecular_weight = target['Molecular_Weight']
                    isoelectric_point = target['Isoelectric_Point']
                    action = target['action']
                    
                    # Cypher query to merge (create or update) Drug node
                    drug_query = (
                        "MERGE (d:Drug {name: $drug_name}) "
                        " ON MATCH SET d.drugbank_id = $drugbank_id "
                        "ON CREATE SET d.name = $drug_name, d.drugbank_id = $drugbank_id "
                        "RETURN d"
                    )
                    
                    # Cypher query to merge (create or update) Protein node
                    protein_query = (
                        "MERGE (p:Protein {id: $polypeptide_id}) "
                        " ON MATCH SET p.full_name = $target_name, "
                        "    p.name = $gene_name, "
                        "    p.organism = $organism, "
                        "    p.general_function = $general_function, "
                        "    p.specific_function = $specific_function, "
                        "    p.molecular_weight = $molecular_weight, "
                        "    p.isoelectric_point = $isoelectric_point, "
                        "    p.accession = $accession "
                        " ON CREATE SET p.id = $polypeptide_id, p.name = $gene_name, p.full_name = $target_name, p.general_function = $general_function, p.specific_function = $specific_function, "
                        "    p.organism = $organism, p.Molecular_Weight = $molecular_weight, p.Isoelectric_Point = $isoelectric_point, p.accession = $accession "
                        " RETURN p"
                    )
                    
                    # Cypher query to create relationship between Drug and Protein
                    relationship_query = (
                        "MATCH (d:Drug {name: $drug_name}), (p:Protein {id: $polypeptide_id}) "
                        "MERGE (d)-[r:TARGETS]->(p) "
                        "ON CREATE SET r.action = $action "
                        "RETURN r"
                    )
                    
                    # Execute the queries in a transaction
                    session.write_transaction(self._merge_node, drug_query, {'drug_name': drug_name, 'drugbank_id': drugbank_id})
                    session.write_transaction(self._merge_node, protein_query, {
                        'polypeptide_id': polypeptide_id,
                        'target_name': target_name,
                        'gene_name': target['gene_name'],
                        'organism': organism,
                        'general_function': general_function,
                        'specific_function': specific_function,
                        'molecular_weight': molecular_weight,
                        'isoelectric_point': isoelectric_point,
                        'accession': accession
                    })
                    session.write_transaction(self._create_relationship, relationship_query, {
                        'drug_name': drug_name,
                        'polypeptide_id': polypeptide_id,
                        'action': target['action']
                    })

                for target in entry['enzymes']:
                    target_name = target['target_name']
                    polypeptide_id = target['polypeptide_id']
                    specific_function = target['specific_function']
                    general_function = target['general_function']
                    organism = target['organism']
                    accession = target['uniprot_accession']
                    molecular_weight = target['Molecular_Weight']
                    isoelectric_point = target['Isoelectric_Point']
                    action = target['action']
                    
                    # Cypher query to merge (create or update) Drug node
                    drug_query = (
                        "MERGE (d:Drug {name: $drug_name}) "
                        " ON MATCH SET d.drugbank_id = $drugbank_id "
                        "ON CREATE SET d.name = $drug_name, d.drugbank_id = $drugbank_id "
                        "RETURN d"
                    )
                    
                    # Cypher query to merge (create or update) Protein node
                    protein_query = (
                        "MERGE (p:Protein {id: $polypeptide_id}) "
                        " ON MATCH SET p.full_name = $target_name, "
                        "    p.name = $gene_name, "
                        "    p.organism = $organism, "
                        "    p.general_function = $general_function, "
                        "    p.specific_function = $specific_function, "
                        "    p.molecular_weight = $molecular_weight, "
                        "    p.isoelectric_point = $isoelectric_point, "
                        "    p.accession = $accession "
                        " ON CREATE SET p.id = $polypeptide_id, p.name = $gene_name, p.full_name = $target_name, p.general_function = $general_function, p.specific_function = $specific_function, "
                        "    p.organism = $organism, p.Molecular_Weight = $molecular_weight, p.Isoelectric_Point = $isoelectric_point, p.accession = $accession "
                        " RETURN p"
                    )
                    
                    # Cypher query to create relationship between Drug and Protein
                    relationship_query = (
                        "MATCH (d:Drug {name: $drug_name}), (p:Protein {id: $polypeptide_id}) "
                        "MERGE (d)-[r:HAS_ENZYME]->(p) "
                        "ON CREATE SET r.action = $action "
                        "RETURN r"
                    )
                    
                    # Execute the queries in a transaction
                    session.write_transaction(self._merge_node, drug_query, {'drug_name': drug_name, 'drugbank_id': drugbank_id})
                    session.write_transaction(self._merge_node, protein_query, {
                        'polypeptide_id': polypeptide_id,
                        'target_name': target_name,
                        'gene_name': target['gene_name'],
                        'organism': organism,
                        'general_function': general_function,
                        'specific_function': specific_function,
                        'molecular_weight': molecular_weight,
                        'isoelectric_point': isoelectric_point,
                        'accession': accession
                    })
                    session.write_transaction(self._create_relationship, relationship_query, {
                        'drug_name': drug_name,
                        'polypeptide_id': polypeptide_id,
                        'action': target['action']
                    })

                for target in entry['carriers']:
                    target_name = target['target_name']
                    polypeptide_id = target['polypeptide_id']
                    specific_function = target['specific_function']
                    general_function = target['general_function']
                    organism = target['organism']
                    accession = target['uniprot_accession']
                    molecular_weight = target['Molecular_Weight']
                    isoelectric_point = target['Isoelectric_Point']
                    action = target['action']
                    
                    # Cypher query to merge (create or update) Drug node
                    drug_query = (
                        "MERGE (d:Drug {name: $drug_name}) "
                        " ON MATCH SET d.drugbank_id = $drugbank_id "
                        "ON CREATE SET d.name = $drug_name, d.drugbank_id = $drugbank_id "
                        "RETURN d"
                    )
                    
                    # Cypher query to merge (create or update) Protein node
                    protein_query = (
                        "MERGE (p:Protein {id: $polypeptide_id}) "
                        " ON MATCH SET p.full_name = $target_name, "
                        "    p.name = $gene_name, "
                        "    p.organism = $organism, "
                        "    p.general_function = $general_function, "
                        "    p.specific_function = $specific_function, "
                        "    p.molecular_weight = $molecular_weight, "
                        "    p.isoelectric_point = $isoelectric_point, "
                        "    p.accession = $accession "
                        " ON CREATE SET p.id = $polypeptide_id, p.name = $gene_name, p.full_name = $target_name, p.general_function = $general_function, p.specific_function = $specific_function, "
                        "    p.organism = $organism, p.Molecular_Weight = $molecular_weight, p.Isoelectric_Point = $isoelectric_point, p.accession = $accession "
                        " RETURN p"
                    )
                    
                    # Cypher query to create relationship between Drug and Protein
                    relationship_query = (
                        "MATCH (d:Drug {name: $drug_name}), (p:Protein {id: $polypeptide_id}) "
                        "MERGE (d)-[r:HAS_CARRIER]->(p) "
                        "ON CREATE SET r.action = $action "
                        "RETURN r"
                    )
                    
                    # Execute the queries in a transaction
                    session.write_transaction(self._merge_node, drug_query, {'drug_name': drug_name, 'drugbank_id': drugbank_id})
                    session.write_transaction(self._merge_node, protein_query, {
                        'polypeptide_id': polypeptide_id,
                        'target_name': target_name,
                        'gene_name': target['gene_name'],
                        'organism': organism,
                        'general_function': general_function,
                        'specific_function': specific_function,
                        'molecular_weight': molecular_weight,
                        'isoelectric_point': isoelectric_point,
                        'accession': accession
                    })
                    session.write_transaction(self._create_relationship, relationship_query, {
                        'drug_name': drug_name,
                        'polypeptide_id': polypeptide_id,
                        'action': target['action']
                    })

                for target in entry['transporters']:
                    target_name = target['target_name']
                    polypeptide_id = target['polypeptide_id']
                    specific_function = target['specific_function']
                    general_function = target['general_function']
                    organism = target['organism']
                    accession = target['uniprot_accession']
                    molecular_weight = target['Molecular_Weight']
                    isoelectric_point = target['Isoelectric_Point']
                    action = target['action']
                    
                    # Cypher query to merge (create or update) Drug node
                    drug_query = (
                        "MERGE (d:Drug {name: $drug_name}) "
                        " ON MATCH SET d.drugbank_id = $drugbank_id "
                        "ON CREATE SET d.name = $drug_name, d.drugbank_id = $drugbank_id "
                        "RETURN d"
                    )
                    
                    # Cypher query to merge (create or update) Protein node
                    protein_query = (
                        "MERGE (p:Protein {id: $polypeptide_id}) "
                        " ON MATCH SET p.full_name = $target_name, "
                        "    p.name = $gene_name, "
                        "    p.organism = $organism, "
                        "    p.general_function = $general_function, "
                        "    p.specific_function = $specific_function, "
                        "    p.molecular_weight = $molecular_weight, "
                        "    p.isoelectric_point = $isoelectric_point, "
                        "    p.accession = $accession "
                        " ON CREATE SET p.id = $polypeptide_id, p.name = $gene_name, p.full_name = $target_name, p.general_function = $general_function, p.specific_function = $specific_function, "
                        "    p.organism = $organism, p.Molecular_Weight = $molecular_weight, p.Isoelectric_Point = $isoelectric_point, p.accession = $accession "
                        " RETURN p"
                    )
                    
                    # Cypher query to create relationship between Drug and Protein
                    relationship_query = (
                        "MATCH (d:Drug {name: $drug_name}), (p:Protein {id: $polypeptide_id}) "
                        "MERGE (d)-[r:HAS_TRANSPORTER]->(p) "
                        "ON CREATE SET r.action = $action "
                        "RETURN r"
                    )
                    
                    # Execute the queries in a transaction
                    session.write_transaction(self._merge_node, drug_query, {'drug_name': drug_name, 'drugbank_id': drugbank_id})
                    session.write_transaction(self._merge_node, protein_query, {
                        'polypeptide_id': polypeptide_id,
                        'target_name': target_name,
                        'gene_name': target['gene_name'],
                        'organism': organism,
                        'general_function': general_function,
                        'specific_function': specific_function,
                        'molecular_weight': molecular_weight,
                        'isoelectric_point': isoelectric_point,
                        'accession': accession
                    })
                    session.write_transaction(self._create_relationship, relationship_query, {
                        'drug_name': drug_name,
                        'polypeptide_id': polypeptide_id,
                        'action': target['action']
                    })
    
    @staticmethod
    def _merge_node(tx, query, params):
        result = tx.run(query, params)
        return result.single()[0]
    
    @staticmethod
    def _create_relationship(tx, query, params):
        tx.run(query, params)

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# Read JSON data from file
with open(DATA_DIR + '\\drug_interactions.json', 'r') as file:
    data = json.load(file)

# Initialize Neo4jHandler and process data
neo4j_handler = Neo4jHandler(uri, username, password)
neo4j_handler.create_or_update_drug_and_protein(data)
neo4j_handler.close()
