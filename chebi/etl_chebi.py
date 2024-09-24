# Install necessary packages
# !pip install mysql-connector-python neo4j

#CHEBI data is stored in MySQL database. We will transfer this data to Neo4j for better visualization and querying.
# Make sure to update the database connection details before running the script.

import mysql.connector
from neo4j import GraphDatabase
from py2neo import Graph, Node, NodeMatcher
import os

# MySQL connection details
mysql_config = {
    'user': '***',
    'password': '***',
    'host': 'localhost',
    'database': 'chebi'
}

# Neo4j connection details
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password"

# Function to fetch data from MySQL
def fetch_data_from_mysql():
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor(dictionary=True)
    
    # Query to fetch compounds
    cursor.execute("SELECT * FROM compounds")
    compounds = cursor.fetchall()
    
    # Query to fetch relations
    cursor.execute("SELECT * FROM relation")
    relations = cursor.fetchall()

    cursor.execute("select * from chemical_data")
    data = cursor.fetchall()
    mapped_chemical_data = {}
    for d in data:
        if d['compound_id'] not in mapped_chemical_data:
            mapped_chemical_data[d['compound_id']] = [{
                d['type']: d['chemical_data'],
                'source': d['source']
            }]
        else:
            mapped_chemical_data[d['compound_id']].append({
                d['type']: d['chemical_data'],
                'source': d['source']
            })
            
            # [d.type] = d.chemical_data
            # mapped_chemical_data[d.compound_id]['source'] = d.source
    
    cursor.close()
    connection.close()
    
    return compounds, relations, mapped_chemical_data

null_entries = {}

def pretty_flatten(data):
    flattened_text = []
    for i, item in enumerate(data):
        # flattened_text.append(f"Item {i + 1}:\n")
        for key, value in item.items():
            flattened_text.append(f"  {key}: {value}")
        # flattened_text.append("\n")  # Add a new line between items

    return ",\n".join(flattened_text).strip()

# Function to insert data into Neo4j
def insert_data_into_neo4j(compounds, relations, chem_data):
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        # Insert compounds as nodes or update existing drugs
        for compound in compounds:
            if compound['id'] < 128119 or compound.get('name') is None or compound.get('name') == '':  # Skip compounds with missing names
                print("Skipping compound with missing name.", compound['id'])
                null_entries[compound['id']] = True
                continue
            # Check if a drug with the same name exists (case-insensitive)
            drug_query = """
            MATCH (d:Drug)
            WHERE toLower(d.name) = toLower($name)
            RETURN d
            """
            drug_result = session.run(drug_query, name=compound['name']).single()
            
            if drug_result:
                # If a drug with the same name exists, add the Compound label and update fields
                update_query = """
                MATCH (d:Drug)
                WHERE toLower(d.name) = toLower($name)
                SET d:Compound,
                    d.chebi_accession = $chebi_accession,
                    d.chebi_definition = $chebi_definition
                """
                if chem_data.get(compound['id']):
                    # convert the chem_data array to prettyfied string
                    compound['chemical_data'] = pretty_flatten(chem_data[compound['id']])
                    update_query += ", d.chemical_data = $chemical_data"
                session.run(update_query,
                            name=compound['name'],
                            chebi_accession=compound.get('chebi_accession'),
                            chebi_definition=compound.get('definition'),
                            chemical_data=compound.get('chemical_data'))
                print(f"Updated drug '{compound['name']}' with Compound label and additional fields.")
            else:
                # If no matching drug exists, create a new Compound node
                query = "MERGE (c:Compound {id: $id, name: $name, chebi_accession: $chebi_accession, chebi_definition: $chebi_definition"
                if chem_data.get(compound['id']):
                    # convert the chem_data array to prettyfied string
                    compound['chemical_data'] = pretty_flatten(chem_data[compound['id']])
                    query += ", chemical_data: $chemical_data"
                query += "})"
                session.run(query,
                            id=compound['id'],
                            name=compound['name'],
                            chebi_accession=compound.get('chebi_accession'),
                            chebi_definition=compound.get('definition'),
                            chemical_data=compound.get('chemical_data'))
        
        # Insert relations as relationships
        for relation in relations:
            if relation['init_id'] in null_entries or relation['final_id'] in null_entries:
                print("Skipping relation with missing compound.", relation['init_id'], relation['final_id'])
                continue
            query = "MATCH (c1:Compound {id: $source_id}) MATCH (c2:Compound {id: $target_id}) MERGE (c1)-[r:"+ relation['type'].upper()() +" {type: $relation_type}]->(c2)"
            
            session.run(query, source_id=relation['init_id'], 
                        target_id=relation['final_id'], 
                        relation_type=relation['type'])
    
    driver.close()

# Main function
def main():
    compounds, relations, chem_data = fetch_data_from_mysql()
    insert_data_into_neo4j(compounds, relations, chem_data)
    print("Data transfer from MySQL to Neo4j completed successfully!")

if __name__ == "__main__":
    main()

