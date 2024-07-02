import os
import xml.etree.ElementTree as ET
import csv

# Define the namespace
NAMESPACE = {'drugbank': 'http://www.drugbank.ca'}

# Function to extract text from an element
def get_text(element, tag):
    found = element.find(f'drugbank:{tag}', NAMESPACE)
    return found.text if found is not None else ''

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# Define the path to the XML file
file_path = DATA_DIR + '\\full_database.xml'

# Check if the file exists before attempting to parse it
if os.path.exists(file_path):
    try:
        # Load and parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Open a CSV file for writing
        with open('drug_data.json', 'w', newline='', encoding='utf-8') as f:
            # Define the CSV writer
            # writer = csv.writer(csvfile)
            
            # Write the header row
            headers = [
                'drugbank_id', 'name', 'description', 'cas_number', 'unii', 'state',
                'synthesis_reference', 'indication', 'pharmacodynamics', 'mechanism_of_action', 
                'toxicity', 'metabolism', 'absorption', 'half_life', 'protein_binding', 
                'route_of_elimination', 'volume_of_distribution', 'clearance'
            ]
            # writer.writerow(headers)

            f.write('[')
            
            # Iterate over each drug element
            for drug in root.findall('drugbank:drug', NAMESPACE):
                drugbank_id = get_text(drug, 'drugbank-id[@primary="true"]')
                name = get_text(drug, 'name')
                description = get_text(drug, 'description')
                cas_number = get_text(drug, 'cas-number')
                unii = get_text(drug, 'unii')
                state = get_text(drug, 'state')
                synthesis_reference = get_text(drug, 'synthesis-reference')
                indication = get_text(drug, 'indication')
                pharmacodynamics = get_text(drug, 'pharmacodynamics')
                mechanism_of_action = get_text(drug, 'mechanism-of-action')
                toxicity = get_text(drug, 'toxicity')
                metabolism = get_text(drug, 'metabolism')
                absorption = get_text(drug, 'absorption')
                half_life = get_text(drug, 'half-life')
                protein_binding = get_text(drug, 'protein-binding')
                route_of_elimination = get_text(drug, 'route-of-elimination')
                volume_of_distribution = get_text(drug, 'volume-of-distribution')
                clearance = get_text(drug, 'clearance')
                
                # Write the row to the json file
                json_entry = {
                    'drugbank_id': drugbank_id, 'name': name, 'description': description, 'cas_number': cas_number,
                    'unii': unii, 'state': state, 'synthesis_reference': synthesis_reference, 'indication': indication,
                    'pharmacodynamics': pharmacodynamics, 'mechanism_of_action': mechanism_of_action, 'toxicity': toxicity,
                    'metabolism': metabolism, 'absorption': absorption, 'half_life': half_life,
                    'protein_binding': protein_binding, 'route_of_elimination': route_of_elimination,
                    'volume_of_distribution': volume_of_distribution, 'clearance': clearance
                }
                import json
                json.dump(json_entry, f, indent=4)
                f.write(',\n')


        print("Data extraction completed successfully.")
    except ET.ParseError as e:
        print(f"Error parsing the XML file: {e}")
else:
    print(f"File not found: {file_path}")
