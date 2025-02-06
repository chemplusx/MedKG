import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UniProtEntry:
    """Class to store parsed UniProt entry data"""
    entry_id: str  # accession number
    protein_name: str
    gene_name: str
    organism: str
    creation_date: datetime
    modification_date: datetime
    sequence: str
    functions: List[str]
    subunits: List[str]
    pathways: List[str]
    keywords: List[str]
    synonyms: List[str]

def parse_uniprot_xml(xml_content: str) -> List[UniProtEntry]:
    """
    Parse UniProt XML content and return a list of UniProtEntry objects
    
    Args:
        xml_content: String containing UniProt XML data
        
    Returns:
        List of UniProtEntry objects containing parsed data
    """
    # Parse XML and get root
    root = ET.fromstring(xml_content)
    
    # Handle namespace if present
    ns = {'': root.nsmap[None]} if hasattr(root, 'nsmap') else {'': 'http://uniprot.org/uniprot'}
    
    entries = []
    
    # Process each entry
    for entry in root.findall('.//entry', ns):
        # Get basic entry information
        dataset = entry.get('dataset')
        created = datetime.strptime(entry.get('created', ''), '%Y-%m-%d')
        modified = datetime.strptime(entry.get('modified', ''), '%Y-%m-%d')
        
        # Get primary accession
        accession = entry.find('.//accession', ns)
        entry_id = accession.text if accession is not None else ''

        synonyms = []
        for syn in entry.findall('.//accession', ns):
            if syn.text:
                synonyms.append(syn.text)
        
        # Get protein name
        protein_name = ''
        protein = entry.find('.//protein/recommendedName/fullName', ns)
        if protein is not None:
            protein_name = protein.text
            
        # Get gene name
        gene_name = ''
        gene = entry.find('.//gene/name[@type="primary"]', ns)
        if gene is not None:
            gene_name = gene.text
            
        # Get organism
        organism = ''
        org = entry.find('.//organism/name[@type="scientific"]', ns)
        if org is not None:
            organism = org.text
            
        # Get sequence
        sequence = ''
        seq = entry.find('.//sequence', ns)
        if seq is not None:
            sequence = seq.text
            
        # Get functions
        functions = []
        for func in entry.findall('.//comment[@type="function"]/text', ns):
            if func.text:
                functions.append(func.text)
        
        subunits =[]
        for subunit in entry.findall('.//comment[@type="subunit"]/text', ns):
            if subunit.text:
                subunits.append(subunit.text)
        # Get pathways
        pathways = []
        for pathway in entry.findall('.//dbReference[@type="Reactome"]', ns):
            pathway_name = pathway.find('./property[@type="pathway name"]', ns)
            if pathway_name is not None:
                pathways.append(pathway_name.get('value'))
                
        # Get keywords
        keywords = []
        for keyword in entry.findall('.//keyword', ns):
            if keyword.text:
                keywords.append(keyword.text)
        
        # Create UniProtEntry object
        entry_obj = UniProtEntry(
            entry_id=entry_id,
            protein_name=protein_name,
            gene_name=gene_name,
            organism=organism,
            creation_date=created,
            modification_date=modified,
            sequence=sequence,
            functions=functions,
            subunits=subunits,
            pathways=pathways,
            keywords=keywords,
            synonyms=synonyms
        )
        
        entries.append(entry_obj)
    
    return entries

# Example usage:
def main():
    # Read XML file
    import json
    def datetime_converter(o):
        if isinstance(o, datetime):
            return o.__str__()
    for filename in ['uniprot_sprot_archaea','uniprot_sprot_bacteria','uniprot_sprot_fungi','uniprot_sprot_rodents','uniprot_sprot_vertebrates','uniprot_sprot_human', 'uniprot_sprot_invertebrates', 'uniprot_sprot_mammals', 'uniprot_sprot_viruses']:
        with open(f'H:\\workspace\\MedKG\\data\\{filename}.xml', 'r') as f:
            xml_content = f.read()
            entries = parse_uniprot_xml(xml_content)
            print("Total entries:", len(entries))
            with open(f"H:\\workspace\\MedKG\\data\\{filename}.json", "w") as f:
                json.dump([entry.__dict__ for entry in entries], f, indent=4, default=datetime_converter)
    
    # Print information for each entry
    # for entry in entries:
    #     print(f"\nEntry ID: {entry.entry_id}")
    #     print(f"Protein Name: {entry.protein_name}")
    #     print(f"Gene Name: {entry.gene_name}")
    #     print(f"Organism: {entry.organism}")
    #     print(f"Created: {entry.creation_date}")
    #     print(f"Modified: {entry.modification_date}")
    #     print(f"Sequence length: {len(entry.sequence)}")
    #     print("\nFunctions:")
    #     for func in entry.functions:
    #         print(f"- {func[:100]}...")
    #     print("\nPathways:")
    #     for pathway in entry.pathways:
    #         print(f"- {pathway}")
    #     print("\nKeywords:")
    #     print(", ".join(entry.keywords))
    #     print("-" * 80)
    
    # Dump into a json file
    
    

if __name__ == "__main__":
    main()