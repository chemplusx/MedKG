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
output_csv_path = DATA_DIR + '\\drug_interactions.csv'

# Check if the file exists before attempting to parse it
if os.path.exists(file_path):
    try:
        # Load and parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Open a CSV file for writing
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define the CSV writer
            writer = csv.writer(csvfile)
            
            # Write the header row
            headers = [
                'drugbank_id', 'name', 'interaction_drugbank_id', 'interaction_name', 'interaction_description',
                'food_interaction'
            ]
            writer.writerow(headers)
            
            # Iterate over each drug element
            for drug in root.findall('drugbank:drug', NAMESPACE):
                drugbank_id = get_text(drug, 'drugbank-id[@primary="true"]')
                name = get_text(drug, 'name')
                
                # Extract drug interactions
                for interaction in drug.findall('drugbank:drug-interactions/drugbank:drug-interaction', NAMESPACE):
                    interaction_drugbank_id = get_text(interaction, 'drugbank-id')
                    interaction_name = get_text(interaction, 'name')
                    interaction_description = get_text(interaction, 'description')
                    
                    writer.writerow([
                        drugbank_id, name, interaction_drugbank_id, interaction_name, interaction_description, ''
                    ])
                
                # Extract food interactions
                for food_interaction in drug.findall('drugbank:food-interactions/drugbank:food-interaction', NAMESPACE):
                    food_interaction_text = food_interaction.text
                    
                    writer.writerow([
                        drugbank_id, name, '', '', '', food_interaction_text
                    ])

        print(f"Data extraction completed successfully. CSV file saved to: {output_csv_path}")
    except ET.ParseError as e:
        print(f"Error parsing the XML file: {e}")
else:
    print(f"File not found: {file_path}")
