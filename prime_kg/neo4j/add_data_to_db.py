import csv

from neo4j import GraphDatabase, RoutingControl
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def add_interaction(driver, node1, node2, interaction, detail):
    try:
        resp = driver.execute_query(
            "MERGE (a:type1 {name: $name, source: $source}) ".replace('type1', node1['type']) +
            "MERGE (b:type2 {name: $name2, source: $source2}) ".replace('type2', node2['type']) +
            "MERGE (a)-[:interaction {type: $detail}]->(b)".replace('interaction', interaction),
            name=node1['name'], name2=node2['name'], source=node1['source'], source2=node2['source'], detail=detail, database_="neo4j",
        )
        # print("After rr: ", resp)
    except Exception as ex:
        print("Exception while adding data into db ", ex)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Read the CSV data and insert into Nebula Graph
    with open('D:\workspace\data\PrimeKG_data\dataverse_files\kg_giant.csv', 'r') as file:
        n = 0
        tot = 1048576
        reader = csv.DictReader(file)
        protein = []
        drug = []
        disease = []
        edge = []
        for row in reader:
            if n%1000 ==0:
                print("Done: ", (n/(7*1048576))*100)

            n+=1
            relation = row['relation']
            display_relation = row['display_relation']
            x_id = row['x_id']
            x_type = row['x_type']
            x_name = row['x_name']
            x_source = row['x_source']
            y_id =row['y_id']
            y_type = row['y_type']
            y_name =row['y_name']
            y_source = row['y_source']
            
            node1 = {}
            node2 = {}
            if x_type == "gene/protein":
                node1['type'] = 'protein'
                
            elif x_type == "drug":
                node1['type'] = 'drug'
            elif x_type == "disease":
                node1['type'] = 'disease'
            
            node1['name'] = x_name
            node1['source'] = x_source

            if y_type == "gene/protein":
                node2['type'] = 'protein'

            elif y_type == "drug":
                node2['type'] = 'drug'
            elif y_type == "disease":
                node2['type'] = 'disease'
            
            node2['name'] = y_name
            node2['source'] = y_source

            if display_relation == 'ppi':
                add_interaction(driver, node1, node2, 'INTERACTS_WITH','has a protein-protein interaction with')
            elif display_relation == 'carrier':
                add_interaction(driver, node1, node2, 'CARRIER_OF', 'is a carrier of')
            elif display_relation == 'contraindication':
                add_interaction(driver, node1, node2, 'IS_A_CONTRAINDICATION_FOR', 'should not be used in the case of')
            elif display_relation == 'enzyme':
                add_interaction(driver, node1, node2, 'ENZYME_FOR', 'Acts as an enzyme for')
            elif display_relation == 'indication':
                add_interaction(driver, node1, node2, 'IS_AN_INDICATION_FOR','should be used in the case of')
            elif display_relation == 'off-label use':
                add_interaction(driver, node1, node2, 'AN_OFF_LABEL_USE_FOR', 'Can be used as an off-label drug for')
            elif display_relation == 'synergistic interaction':
                add_interaction(driver, node1, node2, 'HAS_A_SYNERGISTIC_INTERACTION_WITH', 'has a protein-protein interaction with')
            elif display_relation == 'target':
                add_interaction(driver, node1, node2, 'HAS_TARGET', 'Works on the target')
            elif display_relation == 'transporter':
                add_interaction(driver, node1, node2, 'TRANSPORTS', 'Is a transporter of')
