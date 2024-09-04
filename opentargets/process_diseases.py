"""
Directory: F:\json\diseases

filenames: part-00000-*.json (multiple files)

Sample data in file

{"id":"DOID_7551","code":"http://purl.obolibrary.org/obo/DOID_7551","dbXRefs":["ICD9:098.89","MeSH:D006069","NCIt:C92950","DOID:7551","ICD9:098","ICD9:098.32","SCTID:15628003","Orphanet:100642","SNOMEDCT:187361005","SNOMEDCT:186943001","MESH:D006069","MONDO:0004277","SNOMEDCT:15628003","ICD9CM:098","UMLS:C0018081","ICD9:098.2","UMLS:C0153203","NCIT:C92950"],"description":"A primary bacterial infectious disease that is a sexually transmitted infection, located_in uterus, located_in fallopian tube, located_in urethra, located_in mouth, located_in throat, located_in eye or located_in anus, has_material_basis_in Neisseria gonorrhoeae, which is transmitted_by contact with the penis, vagina, mouth, or anus or transmitted_by congenitally from mother to baby during delivery. The infection has_symptom burning sensation during urination, has_symptom discharge from the penis, has_symptom increased vaginal discharge, or has_symptom vaginal bleeding between periods.","name":"gonorrhea","parents":["EFO_0003955","MONDO_0000314"],"synonyms":{"hasExactSynonym":["chronic gonococcal infectious disease of upper genitourinary tract","gonorrhea","chronic gonococcal infectious disease of lower genitourinary tract.","GC","Neisseria gonorrhoeae infection","chronic gonococcal infectious disease of lower genitourinary tract"],"hasRelatedSynonym":["acrodermatitis, infantile lichenoid","Gianotti Crosti syndrome","infections, Neisseria gonorrhoeae","PAC","papular acrodermatitis of childhood","PAS","Crosti-gianotti syndrome","acrodermatitis, papular infantile"]},"ancestors":["EFO_0000512","OTAR_0000017","EFO_0003955","EFO_0009555","EFO_0000771","MONDO_0000314","EFO_0005741","EFO_0009549","MONDO_0021681"],"descendants":["MONDO_0021160","MONDO_0004853","MONDO_0021161","MONDO_0001640","MONDO_0001575","MONDO_0004774","MONDO_0004852","MONDO_0001720","MONDO_0002029","MONDO_0001777","MONDO_0021157","MONDO_0020971","MONDO_0021159","MONDO_0015455","MONDO_0041903","MONDO_0001080","MONDO_0001837","MONDO_0001838","MONDO_0001719"],"children":["MONDO_0001640","MONDO_0001719","MONDO_0004853","MONDO_0015455","MONDO_0020971","MONDO_0021157","MONDO_0021159","MONDO_0021160","MONDO_0021161","MONDO_0041903"],"therapeuticAreas":["OTAR_0000017","EFO_0005741"],"ontology":{"isTherapeuticArea":false,"leaf":false,"sources":{"url":"http://purl.obolibrary.org/obo/DOID_7551","name":"DOID_7551"}}}
{"id":"EFO_0004254","code":"http://www.ebi.ac.uk/efo/EFO_0004254","dbXRefs":["NCIt:C34645","NCIT:C34645","MeSH:D015433","MONDO:0005376","UMLS:C0017665","SNOMEDCT:77182004","ICD9:583.1","SCTID:77182004","MESH:D015433","DOID:10976","ICD9:582.1"],"description":"A slowly progressive inflammation of the glomeruli characterized by immune complex deposits at the glomerular basement membrane, resulting in a thickened membrane, and nephrotic syndrome.","name":"membranous glomerulonephritis","parents":["MONDO_0002462"],"synonyms":{"hasExactSynonym":["membranous glomerulonephropathy","membranous glomerulonephritis","Heymann nephritis","nephropathy (idiopathic membranous)","membranous Glomerulonephropathy","membranous nephropathy","idiopathic membranous nephropathy","glomerulonephritis, membranous"]},"ancestors":["EFO_1002050","EFO_0009690","EFO_0003086","MONDO_0002462","EFO_1002049"],"descendants":["MONDO_0013860"],"children":["MONDO_0013860"],"therapeuticAreas":["EFO_0009690"],"ontology":{"isTherapeuticArea":false,"leaf":false,"sources":{"url":"http://www.ebi.ac.uk/efo/EFO_0004254","name":"EFO_0004254"}}}
"""


"""
Read all the files in the source folder and then process them to get the required data
Then need to write the data into the neo4j database
"""

import json
import os
from py2neo import Graph, Node, NodeMatcher

# Connect to Neo4j
graph = Graph("bolt://localhost:7690", auth=("neo4j", "password"))

# Path to the file containing the JSON data
directory_path = 'F:\json\diseases'

# Create a NodeMatcher object for querying the database
matcher = NodeMatcher(graph)
newlist = []
for filename in os.listdir(directory_path):
    if filename.endswith(".json"):  # Ensure you're only processing JSON files
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r') as file:
            for line in file:
                data = json.loads(line.strip())
                
                # Check if the Disease node already exists
                disease_node = matcher.match("Disease", name=data.get("name")).first()
                
                if not disease_node:
                    # If the node does not exist, create a new one
                    disease_node = Node("Disease", id=data.get("id"))

                    # Update the properties
                    disease_node["code"] = data.get("code")
                    disease_node["description"] = data.get("description")
                    disease_node["name"] = data.get("name")

                    # Update synonyms as properties
                    if "synonyms" in data:
                        disease_node["hasExactSynonym"] = data["synonyms"].get("hasExactSynonym", [])
                        disease_node["hasRelatedSynonym"] = data["synonyms"].get("hasRelatedSynonym", [])

                    # Update ancestors, descendants, children, and therapeuticAreas as list properties
                    if "ancestors" in data:
                        disease_node["ancestors"] = data["ancestors"]
                    if "descendants" in data:
                        disease_node["descendants"] = data["descendants"]
                    if "children" in data:
                        disease_node["children"] = data["children"]
                
                    if "therapeuticAreas" in data:
                        disease_node["therapeuticAreas"] = data["therapeuticAreas"]

                    # Add ontology properties
                    if "ontology" in data:
                        disease_node["ontology"] = str(data["ontology"])

                    print(disease_node)
                    newlist.append(data.get("name"))
                    graph.merge(disease_node, "Disease", "id")
                # Merge the node to avoid duplicates
                # graph.merge(disease_node, "Disease", "id")

json.dump(newlist, open('disease_names.json', 'w'), indent=4)

