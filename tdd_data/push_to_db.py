"""
"FORMERID": "TTDC00024",
"UNIPROID": "FGFR1_HUMAN",
"TARGNAME": "Fibroblast growth factor receptor 1 (FGFR1)",
"GENENAME": "FGFR1",
"TARGTYPE": "Successful",
"SYNONYMS": "c-fgr; bFGF-R-1; bFGF-R; N-sam; HBGFR; Fms-like tyrosine kinase 2; FLT2; FLT-2; FLG; FGFR-1; FGFBR; CEK; CD331 antigen; CD331; Basic fibroblast growth factor receptor 1; BFGFR",
"FUNCTION": "Required for normal mesoderm patterning and correct axial organization during embryonic development, normal skeletogenesis and normal development of the gonadotropin-releasing hormone (GnRH) neuronal system. Phosphorylates PLCG1, FRS2, GAB1 and SHB. Ligand binding leads to the activation of several signaling cascades. Activation of PLCG1 leads to the production of the cellular signaling molecules diacylglycerol and inositol 1,4,5-trisphosphate. Phosphorylation of FRS2 triggers recruitment of GRB2, GAB1, PIK3R1 and SOS1, and mediates activation of RAS, MAPK1/ERK2, MAPK3/ERK1 and the MAP kinase signaling pathway, as well as of the AKT1 signaling pathway. Promotes phosphorylation of SHC1, STAT1 and PTPN11/SHP2. In the nucleus, enhances RPS6KA1 and CREB1 activity and contributes to the regulation of transcription. FGFR1 signaling is down-regulated by IL17RD/SEF, and by FGFR1 ubiquitination, internalization and degradation. Tyrosine-protein kinase that acts as cell-surface receptor for fibroblast growth factors and plays an essential role in the regulation of embryonic development, cell proliferation, differentiation and migration.",
"PDBSTRUC": "6MZW; 6MZQ; 6C1O; 6C1C; 6C1B",
"BIOCLASS": "Kinase",
"ECNUMBER": "EC 2.7.10.1",
"SEQUENCE":

"""


from neo4j import GraphDatabase
import json
import os

# Function to connect to Neo4j database
def connect_to_db(uri, username, password):
    return GraphDatabase.driver(uri, auth=(username, password))

# Function to process the data and create/update nodes and relationships in Neo4j
def process_data(tx, data):
    # Create or update relationships for drug information
    for drug_info in data.get('DRUGINFO', []):
        tx.run(
            "MATCH (target:Protein {id: $id}) "
            "MERGE (drug:Drug{name: $drugName}) "
            "MERGE (drug)-[:TARGETS{clinical_status:$clinicalStatus}]->(target)",
            id=data.get('id'),
            drugName=drug_info.get('Drug Name'),
            clinicalStatus=drug_info.get('Highest Clinical Status')
        )

# Neo4j connection parameters
uri = "bolt://localhost:7690"  # Replace with your Neo4j server URI
username = "neo4j"     # Replace with your Neo4j username
password = "password"     # Replace with your Neo4j password


DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# File containing the data
file_path = DATA_DIR + "\\P1-01-TTD_target_download.json"  # Replace with the path to your JSON file

# Read data from JSON file
with open(file_path, 'r') as file:
    data = json.load(file)

# Connect to Neo4j
driverdd = connect_to_db(uri, username, password)

# Process data and create/update nodes and relationships in Neo4j
# with driver.session() as session:

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    for key, values in data.items():
        # Create or update Protein node
        
        res = driver.execute_query(
            "MATCH (node:Protein)"
            "WHERE node.accession = $accession "
            "WITH collect(node) as nodes, count(node) AS nodeCount "
            "call apoc.when(nodeCount > 1, 'unwind nodes as iNode with iNode where iNode.general_function is not null return iNode as vs', 'return nodes as vs', {nodes:nodes, nodeCount:nodeCount} ) "
            "YIELD value "
            "return value.vs",
            accession=values.get('UNIPROID')
        )
        res = res[0][0][0]
        # update the retrieved protein information

        driver.execute_query(
            "MATCH (n:Protein {id: $id}) "
            "SET n.full_name = $targname, "
            "n.type = $targtype, "
            "n.function = $function, "
            "n.structure = $pdbstruc, "
            "n.bioclass = $bioclass, "
            "n.ecnumber = $ecnumber ",
            id=res.get('id'),
            targname=values.get('TARGNAME'),
            targtype=values.get('TARGTYPE'),
            function=values.get('FUNCTION'),
            pdbstruc=values.get('PDBSTRUC'),
            bioclass=values.get('BIOCLASS'),
            ecnumber=values.get('ECNUMBER')
        )

        with driverdd.session() as session:
            cvalues = {
                'id': res.get('id'),
                'DRUGINFO': values.get('DRUGINFO')
            }
            session.write_transaction(process_data, cvalues)

# Close the Neo4j driver
driver.close()
