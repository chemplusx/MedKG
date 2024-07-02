import os
import xml.etree.ElementTree as ET
import csv



DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# Define the namespace
NAMESPACE = {'drugbank': 'http://www.drugbank.ca'}

# Function to extract text from an element
def get_text(element, tag):
    found = element.find(f'drugbank:{tag}', NAMESPACE)
    return found.text if found is not None else ''


# Define the path to the XML file
file_path = DATA_DIR + '\\full_database.xml'

# Define the path for the output CSV file
output_csv_path = DATA_DIR + '\\drug_interactions.json'

# Check if the file exists before attempting to parse it
if os.path.exists(file_path):
    try:
        # Load and parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Open a CSV file for writing
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write('[')
            # Iterate over each drug element
            for drug in root.findall('drugbank:drug', NAMESPACE):
                drugbank_id = get_text(drug, 'drugbank-id[@primary="true"]')
                name = get_text(drug, 'name')
                targets = []
                enzymes = []
                carriers = []
                transporters = []
                # Extract drug interactions
                for interaction in drug.findall('drugbank:targets/drugbank:target', NAMESPACE):
                    target_name = get_text(interaction, 'name')
                    actions = interaction.find(f'drugbank:actions', NAMESPACE)
                    action = get_text(actions, 'action')
                    for pp in interaction.findall(f'drugbank:polypeptide', NAMESPACE):
                        polypeptide_id = pp.get('id')
                        general_function = get_text(pp,'general-function')
                        specific_function = get_text(pp,'specific-function')
                        gene_name = get_text(pp,'gene-name')
                        organism = get_text(pp,'organism')
                        known_action = get_text(pp,'known-action')
                        molecular_weight = get_text(pp,'molecular-weight')
                        isoelectric_point = get_text(pp,'theoretical-pi')
                        uniprot_accession = None
                        for external_identifier in pp.findall('drugbank:external-identifiers/drugbank:external-identifier', NAMESPACE):
                            resource = get_text(external_identifier, 'resource')
                            identifier = get_text(external_identifier, 'identifier')
                            if resource == 'UniProt Accession':
                                uniprot_accession = identifier

                        targets.append({
                            "target_name": target_name,
                            "action": action,
                            "general_function": general_function,
                            "specific_function": specific_function,
                            "polypeptide_id": polypeptide_id,
                            "gene_name": gene_name,
                            "organism": organism,
                            "known_action": known_action,
                            "uniprot_accession": uniprot_accession,
                            "Molecular_Weight": molecular_weight,
                            "Isoelectric_Point": isoelectric_point
                        })
                    
                
                for interaction in drug.findall('drugbank:carriers/drugbank:carrier', NAMESPACE):
                    target_name = get_text(interaction, 'name')
                    actions = interaction.find(f'drugbank:actions', NAMESPACE)
                    action = get_text(actions, 'action')
                    for pp in interaction.findall(f'drugbank:polypeptide', NAMESPACE):
                        polypeptide_id = pp.get('id')
                        general_function = get_text(pp,'general-function')
                        specific_function = get_text(pp,'specific-function')
                        gene_name = get_text(pp,'gene-name')
                        organism = get_text(pp,'organism')
                        known_action = get_text(pp,'known-action')
                        molecular_weight = get_text(pp,'molecular-weight')
                        isoelectric_point = get_text(pp,'theoretical-pi')
                        uniprot_accession = None
                        for external_identifier in pp.findall('drugbank:external-identifiers/drugbank:external-identifier', NAMESPACE):
                            resource = get_text(external_identifier, 'resource')
                            identifier = get_text(external_identifier, 'identifier')
                            if resource == 'UniProt Accession':
                                uniprot_accession = identifier

                        carriers.append({
                            "target_name": target_name,
                            "action": action,
                            "general_function": general_function,
                            "specific_function": specific_function,
                            "polypeptide_id": polypeptide_id,
                            "gene_name": gene_name,
                            "organism": organism,
                            "known_action": known_action,
                            "uniprot_accession": uniprot_accession,
                            "Molecular_Weight": molecular_weight,
                            "Isoelectric_Point": isoelectric_point
                        })

                for interaction in drug.findall('drugbank:transporters/drugbank:transporter', NAMESPACE):
                    target_name = get_text(interaction, 'name')
                    actions = interaction.find(f'drugbank:actions', NAMESPACE)
                    action = get_text(actions, 'action')
                    for pp in interaction.findall(f'drugbank:polypeptide', NAMESPACE):
                        polypeptide_id = pp.get('id')
                        general_function = get_text(pp,'general-function')
                        specific_function = get_text(pp,'specific-function')
                        gene_name = get_text(pp,'gene-name')
                        organism = get_text(pp,'organism')
                        known_action = get_text(pp,'known-action')
                        molecular_weight = get_text(pp,'molecular-weight')
                        isoelectric_point = get_text(pp,'theoretical-pi')
                        uniprot_accession = None
                        for external_identifier in pp.findall('drugbank:external-identifiers/drugbank:external-identifier', NAMESPACE):
                            resource = get_text(external_identifier, 'resource')
                            identifier = get_text(external_identifier, 'identifier')
                            if resource == 'UniProt Accession':
                                uniprot_accession = identifier

                        transporters.append({
                            "target_name": target_name,
                            "action": action,
                            "general_function": general_function,
                            "specific_function": specific_function,
                            "polypeptide_id": polypeptide_id,
                            "gene_name": gene_name,
                            "organism": organism,
                            "known_action": known_action,
                            "uniprot_accession": uniprot_accession,
                            "Molecular_Weight": molecular_weight,
                            "Isoelectric_Point": isoelectric_point
                        })
                
                for interaction in drug.findall('drugbank:enzymes/drugbank:enzyme', NAMESPACE):
                    target_name = get_text(interaction, 'name')
                    actions = interaction.find(f'drugbank:actions', NAMESPACE)
                    action = get_text(actions, 'action')
                    for pp in interaction.findall(f'drugbank:polypeptide', NAMESPACE):
                        polypeptide_id = pp.get('id')
                        general_function = get_text(pp,'general-function')
                        specific_function = get_text(pp,'specific-function')
                        gene_name = get_text(pp,'gene-name')
                        organism = get_text(pp,'organism')
                        known_action = get_text(pp,'known-action')
                        molecular_weight = get_text(pp,'molecular-weight')
                        isoelectric_point = get_text(pp,'theoretical-pi')
                        uniprot_accession = None
                        for external_identifier in pp.findall('drugbank:external-identifiers/drugbank:external-identifier', NAMESPACE):
                            resource = get_text(external_identifier, 'resource')
                            identifier = get_text(external_identifier, 'identifier')
                            if resource == 'UniProt Accession':
                                uniprot_accession = identifier

                        enzymes.append({
                            "target_name": target_name,
                            "action": action,
                            "general_function": general_function,
                            "specific_function": specific_function,
                            "polypeptide_id": polypeptide_id,
                            "gene_name": gene_name,
                            "organism": organism,
                            "known_action": known_action,
                            "uniprot_accession": uniprot_accession,
                            "Molecular_Weight": molecular_weight,
                            "Isoelectric_Point": isoelectric_point
                        })
                    
                
                # Extract food interactions
                for food_interaction in drug.findall('drugbank:food-interactions/drugbank:food-interaction', NAMESPACE):
                    food_interaction_text = food_interaction.text

                import json
                json.dump( {
                    "drugbank_id": drugbank_id,
                    "drug_name": name,
                    "targets": targets,
                    "enzymes": enzymes,
                    "carriers": carriers,
                    "transporters": transporters
                }, f, indent=4)
                f.write(',\n')

        print(f"Data extraction completed successfully. CSV file saved to: {output_csv_path}")
    except ET.ParseError as e:
        print(f"Error parsing the XML file: {e}")
else:
    print(f"File not found: {file_path}")
