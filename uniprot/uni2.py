from lxml import etree
from typing import Dict, List, Iterator
from dataclasses import dataclass
from datetime import datetime
import json
import os

@dataclass
class UniProtEntry:
    """Class to store parsed UniProt entry data"""
    entry_id: str
    protein_name: str
    gene_name: str
    organism: str
    creation_date: datetime
    modification_date: datetime
    sequence: str
    functions: List[str]
    pathways: List[str]
    keywords: List[str]
    synonyms: List[str]
    subunits: List[str]
    references: List[Dict]
    db_refs: List[Dict]

def iter_xml_entries(filename: str) -> Iterator[UniProtEntry]:
    """
    Iteratively parse large UniProt XML file and yield entries
    """
    # Define namespace
    ns = {'u': 'http://uniprot.org/uniprot'}
    
    # Create a parser that can handle large files
    parser = etree.XMLParser(huge_tree=True, remove_blank_text=True)
    
    # Use iterparse to stream through the file
    for _, elem in etree.iterparse(filename, tag=f'{{{ns["u"]}}}entry'):
        try:
            # Basic entry info
            created = datetime.strptime(elem.get('created', ''), '%Y-%m-%d')
            modified = datetime.strptime(elem.get('modified', ''), '%Y-%m-%d')
            
            # Get primary accession and synonyms
            accessions = elem.findall('.//u:accession', ns)
            entry_id = accessions[0].text if accessions else ''
            synonyms = [acc.text for acc in accessions[1:] if acc.text]
            
            # Get protein name
            protein = elem.find('.//u:protein/u:recommendedName/u:fullName', ns)
            protein_name = protein.text if protein is not None else ''
            
            # Get gene name
            gene = elem.find('.//u:gene/u:name[@type="primary"]', ns)
            gene_name = gene.text if gene is not None else ''
            
            # Get organism
            org = elem.find('.//u:organism/u:name[@type="scientific"]', ns)
            organism = org.text if org is not None else ''
            
            # Get sequence
            seq = elem.find('.//u:sequence', ns)
            sequence = seq.text.replace('\n', '') if seq is not None and seq.text is not None else ''
            
            # Get functions
            functions = []
            for func in elem.findall('.//u:comment[@type="function"]/u:text', ns):
                if func is not None and func.text:
                    functions.append(func.text)
            
            # Get subunits
            subunits = []
            for subunit in elem.findall('.//u:comment[@type="subunit"]/u:text', ns):
                if subunit is not None and subunit.text:
                    subunits.append(subunit.text)
            
            # Get pathways
            pathways = []
            for pathway in elem.findall('.//u:dbReference[@type="Reactome"]', ns):
                pathway_name = pathway.find('./u:property[@type="pathway name"]', ns)
                if pathway_name is not None:
                    pathways.append(pathway_name.get('value'))
            
            # Get references
            references = []
            for ref in elem.findall('.//u:reference', ns):
                citation = ref.find('.//u:citation', ns)
                if citation is not None:
                    ref_data = {
                        'type': citation.get('type', ''),
                        'date': citation.get('date', ''),
                        'authors': [p.get('name') for p in citation.findall('.//u:person', ns)],
                        'title': citation.find('.//u:title', ns).text if citation.find('.//u:title', ns) is not None else '',
                        'journal': citation.get('name', ''),
                        'volume': citation.get('volume', ''),
                        'first_page': citation.get('first', ''),
                        'last_page': citation.get('last', ''),
                        'pubmed_id': '',
                        'doi': ''
                    }
                    
                    # Get PubMed ID and DOI
                    for db_ref in citation.findall('.//u:dbReference', ns):
                        if db_ref.get('type') == 'PubMed':
                            ref_data['pubmed_id'] = db_ref.get('id', '')
                        elif db_ref.get('type') == 'DOI':
                            ref_data['doi'] = db_ref.get('id', '')
                    
                    references.append(ref_data)
            
            # Get database references
            db_refs = []
            for db_ref in elem.findall('.//u:dbReference', ns):
                ref_data = {
                    'type': db_ref.get('type', ''),
                    'id': db_ref.get('id', ''),
                    'properties': {
                        prop.get('type'): prop.get('value')
                        for prop in db_ref.findall('.//u:property', ns)
                    }
                }
                db_refs.append(ref_data)
            
            # Get keywords
            keywords = []
            for keyword in elem.findall('.//u:keyword', ns):
                if keyword is not None and keyword.text:
                    keywords.append(keyword.text)
            
            # Create entry object
            entry = UniProtEntry(
                entry_id=entry_id,
                protein_name=protein_name,
                gene_name=gene_name,
                organism=organism,
                creation_date=created,
                modification_date=modified,
                sequence=sequence,
                functions=functions,
                pathways=pathways,
                keywords=keywords,
                synonyms=synonyms,
                subunits=subunits,
                references=references,
                db_refs=db_refs
            )
            
            yield entry
            
        except Exception as e:
            print(f"Error processing entry {entry_id if 'entry_id' in locals() else 'unknown'}: {str(e)}")
            continue
        
        finally:
            # Clear element to free memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

def process_file_in_chunks(filename: str, chunk_size: int = 20000):
    """Process large XML file in chunks and save to multiple JSON files"""
    base_name = os.path.splitext(filename)[0]
    entries = []
    chunk_num = 1
    
    def save_chunk(chunk_entries, chunk_number):
        output_file = f"{base_name}_chunk{chunk_number}.json"
        print(f"Saving chunk {chunk_number} with {len(chunk_entries)} entries to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(
                [entry.__dict__ for entry in chunk_entries],
                f,
                indent=2,
                default=lambda o: o.__str__() if isinstance(o, datetime) else o
            )
    
    total_entries = 0
    current_chunk = []
    
    print(f"Processing {filename}...")
    for entry in iter_xml_entries(filename):
        current_chunk.append(entry)
        total_entries += 1
        
        if len(current_chunk) >= chunk_size:
            save_chunk(current_chunk, chunk_num)
            chunk_num += 1
            current_chunk = []
        
        if total_entries % 20000 == 0:
            print(f"Processed {total_entries} entries...")
    
    # Save any remaining entries
    if current_chunk:
        save_chunk(current_chunk, chunk_num)
    
    print(f"Finished processing {total_entries} total entries")

def main():
    data_dir = 'H:\\workspace\\MedKG\\data'
    filenames = [
        # 'uniprot_sprot_archaea',
        'uniprot_sprot_bacteria',
        # 'uniprot_sprot_fungi',
        # 'uniprot_sprot_rodents',
        # 'uniprot_sprot_vertebrates',
        # 'uniprot_sprot_human',
        # 'uniprot_sprot_invertebrates',
        # 'uniprot_sprot_mammals',
        # 'uniprot_sprot_viruses'
    ]
    
    for filename in filenames:
        input_file = os.path.join(data_dir, f'{filename}.xml')
        
        if not os.path.exists(input_file):
            print(f"File not found: {input_file}")
            continue
            
        try:
            process_file_in_chunks(input_file)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

if __name__ == "__main__":
    main()