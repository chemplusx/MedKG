import xml.etree.ElementTree as ET
import os

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# Path to the XML file
xml_file = DATA_DIR + '\\hmdb_metabolites.xml'

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

NAMESPACE = {'hmdb': 'http://www.hmdb.ca'}

for metabolite in root.findall('hmdb:metabolite', NAMESPACE):
    # Extracting specific elements
    version = metabolite.find('hmdb:version', NAMESPACE).text
    creation_date = metabolite.find('hmdb:creation_date', NAMESPACE).text
    update_date = metabolite.find('hmdb:update_date', NAMESPACE).text
    accession = metabolite.find('hmdb:accession', NAMESPACE).text
    status = metabolite.find('hmdb:status', NAMESPACE).text
    secondary_accessions = [acc.text for acc in metabolite.find('hmdb:secondary_accessions', NAMESPACE).findall('hmdb:accession', NAMESPACE)]
    name = metabolite.find('hmdb:name', NAMESPACE).text
    description = metabolite.find('hmdb:description', NAMESPACE).text

    # Extract synonyms
    synonyms = [syn.text for syn in metabolite.find('hmdb:synonyms', NAMESPACE).findall('hmdb:synonym', NAMESPACE)]

    # Extract chemical formula and IUPAC names
    chemical_formula = metabolite.find('hmdb:chemical_formula', NAMESPACE).text
    iupac_names = [name.text for name in metabolite.find('hmdb:iupac_names', NAMESPACE).findall('hmdb:name', NAMESPACE)]

    # Extract taxonomy
    taxonomy = {
        'kingdom': metabolite.find('hmdb:taxonomy/hmdb:kingdom', NAMESPACE).text,
        'class': metabolite.find('hmdb:taxonomy/hmdb:class', NAMESPACE ).text,
        'order': metabolite.find('hmdb:taxonomy/hmdb:order', NAMESPACE).text,
        'family': metabolite.find('hmdb:taxonomy/hmdb:family', NAMESPACE).text,
        'genus': metabolite.find('hmdb:taxonomy/hmdb:genus', NAMESPACE).text,
        'species': metabolite.find('hmdb:taxonomy/hmdb:species', NAMESPACE).text
    }

    # Extract disease interactions
    disease_interactions = [disease.text for disease in metabolite.find('hmdb:disease_interactions', NAMESPACE).findall('hmdb:disease', NAMESPACE)]

    # Extract drug interactions
    drug_interactions = {
        interaction.find('hmdb:drug', NAMESPACE).text: interaction.find('hmdb:description', NAMESPACE).text
        for interaction in metabolite.find('hmdb:drug_interactions', NAMESPACE).findall('hmdb:interaction', NAMESPACE)
    }

    # Print or process the extracted data as needed

    # Print or process the extracted data as needed
    print(f"Version: {version}")
    print(f"Creation Date: {creation_date}")
    print(f"Update Date: {update_date}")
    print(f"Accession: {accession}")
    print(f"Status: {status}")
    print(f"Secondary Accessions: {secondary_accessions}")
    print(f"Name: {name}")
    print(f"Description: {description}")
    print(f"Synonyms: {synonyms}")
    print(f"Chemical Formula: {chemical_formula}")
    print(f"IUPAC Names: {iupac_names}")
    print(f"Taxonomy: {taxonomy}")
    print(f"Disease Interactions: {disease_interactions}")
    print(f"Drug Interactions: {drug_interactions}")
