from neo4j import GraphDatabase
import json
from typing import List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProteinDataImporter:
    def __init__(self, uri: str, username: str, password: str):
        """Initialize the Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()

    def import_protein_data(self, data: List[Dict[str, Any]]):
        """Import protein data into Neo4j."""
        with self.driver.session() as session:
            for entry in data:
                try:
                    # Preprocess dates
                    entry = self._preprocess_dates(entry)
                    
                    # Execute the import queries
                    self._process_entry(session, entry)
                    logger.info(f"Processed protein entry: {entry['entry_id']}")
                
                except Exception as e:
                    logger.error(f"Error processing entry {entry.get('entry_id', 'unknown')}: {str(e)}")

    def _process_entry(self, session, entry):
        """Process a single protein entry through all the necessary queries."""
        # Execute queries in sequence
        if len(entry.get('functions', [])) > 1:
            entry['specific_function'] = entry['functions'][0]
            entry['general_functions'] = '.'.join(entry['functions'][1:])
        elif len(entry.get('functions', [])) == 1:
            entry['specific_function'] = entry['functions'][0]
            entry['general_functions'] = entry['functions'][0]
        else:
            entry['specific_function'] = ''
            entry['general_functions'] = ''
        session.execute_write(self._merge_protein_node, entry)
        session.execute_write(self._create_pathways, entry)
        session.execute_write(self._create_references, entry)

    @staticmethod
    def _preprocess_dates(entry: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess date fields to ensure Neo4j compatibility."""
        date_fields = ['creation_date', 'modification_date']
        for field in date_fields:
            if entry.get(field):
                try:
                    date_obj = datetime.strptime(entry[field], '%Y-%m-%d %H:%M:%S')
                    entry[field] = date_obj.strftime('%Y-%m-%dT%H:%M:%S')
                except (ValueError, TypeError):
                    logger.warning(f"Invalid date format in {field} for entry {entry.get('entry_id')}")
                    entry[field] = None
        return entry

    @staticmethod
    def _merge_protein_node(tx, entry):
        """Create or update the main protein node."""
        query = """
        MERGE (protein:Protein {id: $entry.entry_id})
        ON CREATE SET 
            protein.name = $entry.protein_name,
            protein.gene_name = $entry.gene_name,
            protein.organism = $entry.organism,
            protein.general_function = $entry.general_functions,
            protein.specific_function = $entry.specific_function,
            protein.source = "UniProt",
            protein.sequence = $entry.sequence,
            protein.synonyms = $entry.synonyms,
            protein.keywords = $entry.keywords
        ON MATCH SET 
            protein.name = $entry.protein_name,
            protein.gene_name = $entry.gene_name,
            protein.organism = $entry.organism,
            protein.general_function = $entry.general_functions,
            protein.specific_function = $entry.specific_function,
            protein.source = "UniProt",
            protein.sequence = $entry.sequence,
            protein.keywords = $entry.keywords
        """
        return tx.run(query, entry=entry)


    @staticmethod
    def _create_pathways(tx, entry):
        """Create pathway nodes and relationships."""
        query = """
        MERGE (protein:Protein {id: $entry.entry_id})
        WITH protein
        UNWIND $entry.pathways AS pathway
        WITH protein, pathway
        WHERE pathway <> ''
        MATCH (p:Pathway {name: pathway})
        WITH protein, p
        WHERE NOT (protein)-[:ANNOTATED_IN_PATHWAY]->(p)
        CREATE (protein)-[:ANNOTATED_IN_PATHWAY]->(p)
        """
        return tx.run(query, entry=entry)


    @staticmethod
    def _create_references(tx, entry):
        """Handle publication nodes, their relationships, and author updates."""
        query = """
        MATCH (protein:Protein {id: $entry.entry_id})
        UNWIND $entry.references AS ref
        WITH protein, ref
        WHERE ref.pubmed_id IS NOT NULL AND ref.pubmed_id <> ''
        
        // Match or create the Publication node and update its properties
        MERGE (p:Publication {id: ref.pubmed_id})
        ON CREATE SET 
            p.title = ref.title,
            p.journal = ref.journal,
            p.volume = ref.volume,
            p.first_page = ref.first_page,
            p.last_page = ref.last_page,
            p.date = ref.date,
            p.type = ref.type,
            p.doi = COALESCE(ref.doi, '')
        ON MATCH SET 
            p.title = ref.title

        // Check if relationship exists between protein and publication
        WITH protein, p
        OPTIONAL MATCH (protein)-[existing]->(p)
        WITH protein, p, existing
        WHERE existing IS NULL
        MERGE (protein)-[:CITED_IN]->(p)
        """
        
        # Execute main query for publications with PubMed IDs
        tx.run(query, entry=entry)


def main():
    # Neo4j connection parameters
    URI = "neo4j://localhost:7687"  # Update with your Neo4j URI
    USERNAME = "neo4j"              # Update with your username
    PASSWORD = "password"      # Update with your password

    # Initialize importer
    importer = ProteinDataImporter(URI, USERNAME, PASSWORD)

    try:
        # Read JSON data from file
        with open('H:\\workspace\\MedKG\\data\\uniprot_sprot_human.json', 'r') as f:
            data = json.load(f)

        # Import data
        importer.import_protein_data(data)
        logger.info("Data import completed successfully")

    except Exception as e:
        logger.error(f"Error during import: {str(e)}")

    finally:
        importer.close()

if __name__ == "__main__":
    main()