# from nebula3.gclient.net import ConnectionPool
# from nebula3.Config import Config
import csv

# # Nebula Graph connection configuration
# config = Config()
# config.max_connection_pool_size = 10
# connection_pool = ConnectionPool()
# connection_pool.init([('192.168.0.115', 9669)], config)

# # Create a session to execute queries
# session = connection_pool.get_session('root', 'nebula')

# Define the schema

# Execute the schema creation query
# result = session.execute("USE prime_kg_1; CREATE TAG IF NOT EXISTS protein(id string, name string, source string);")
# # print("Schema 1: ", result)
# result = session.execute("""CREATE TAG IF NOT EXISTS disease(id string, name string, mondo_name string, mondo_definition string, umls_description string, orphanet_definition string,orphanet_prevalence string, orphanet_epidemiology string, orphanet_clinical_description string, orphanet_management_and_treatment string, mayo_symptoms string, mayo_causes string, mayo_risk_factors string, mayo_complications string, mayo_prevention string, mayo_see_doc  string, source string);""")
# # print("Schema 2: ", result)
# result = session.execute("""CREATE TAG IF NOT EXISTS drug(id string, name string, description string, half_life string, indication string, mechanism_of_action string, protein_binding string, pharmacodynamics string, state string, atc_1 string, atc_2 string, atc_3 string, atc_4 string, category string, group string, pathway string, molecular_weight string, tpsa string, clogp string, source string);""")
# # print("Schema 3: ", result)
# result = session.execute("CREATE EDGE IF NOT EXISTS interaction(relation string, display_relation string);")

# CREATE TAG INDEX IF NOT EXISTS disease_index ON disease(name(256));
# CREATE TAG INDEX IF NOT EXISTS drug_index ON drug(name(256));
# CREATE TAG INDEX IF NOT EXISTS protein_index ON protein(name(256));
# print("Schema 4: ", result)


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
        # next(file)  # Skip the header row
        n = 0
        tot = 1048576
        reader = csv.DictReader(file)
        protein = []
        drug = []
        disease = []
        edge = []
        for row in reader:
            # if n == 5:
            #     vertex_query = f'INSERT VERTEX protein(id, name, source) values {", ".join(protein)};'
            #     print(vertex_query, session.execute(vertex_query))
            #     break
            # if n < 321000:
            #     n+=1
            #     continue
            if n%1000 ==0:
                print("Done: ", (n/(7*1048576))*100)
                # if len(protein) >0:
                #     vertex_query = f'INSERT VERTEX protein(id, name, source) values {", ".join(protein)};'
                #     session.execute(vertex_query)
                #     protein = []
                # if len(drug) >0:
                #     vertex_query = f'INSERT VERTEX drug(id, name, source) values {", ".join(drug)};'
                #     session.execute(vertex_query)
                #     drug = []
                # if len(disease) >0:
                #     vertex_query = f'INSERT VERTEX disease(id, name, source) values {", ".join(disease)};'
                #     session.execute(vertex_query)
                #     disease = []
                # if len(edge) >0:
                #     vertex_query = f'INSERT EDGE interaction(relation, display_relation) values {", ".join(edge)};'
                #     session.execute(vertex_query)
                #     edge = []
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
                # Insert vertices
                # result = session.execute(f"USE prime_kg; INSERT VERTEX Protein(id, name, source) VALUES '{x_id}':({int(x_id)}, \"{x_name}\", \"{x_source}\");")
                # prop_str = f'"{x_id}", "{x_name}", "{x_source}"'
                # protein.append(f'"{x_name}": ({prop_str})')
                node1['type'] = 'protein'
                
            elif x_type == "drug":
                # result = session.execute(f"USE prime_kg; INSERT VERTEX DRUG(id, name, source) VALUES '{x_id}':({x_id}, \"{x_name}\", \"{x_source}\");")
                # prop_str = f'"{x_id}", "{x_name}", "{x_source}"'
                # drug.append(f'"{x_name}": ({prop_str})')
                node1['type'] = 'drug'
            elif x_type == "disease":
                # result = session.execute(f"USE prime_kg; INSERT VERTEX DISEASE(id, name, source) VALUES '{x_id}':({int(x_id)}, \"{x_name}\", \"{x_source}\");")
                # prop_str = f'"{x_id}", "{x_name}", "{x_source}"'
                # disease.append(f'"{x_name}": ({prop_str})')
                node1['type'] = 'disease'
            
            node1['name'] = x_name
            node1['source'] = x_source

            # print("First -> ", result)
            if y_type == "gene/protein":
                # Insert vertices
                # result = session.execute(f"USE prime_kg; INSERT VERTEX Protein(id, name, source) VALUES '{y_id}':({int(y_id)}, \"{y_name}\", \"{y_source}\");")
                # prop_str = f'"{y_id}", "{y_name}", "{y_source}"'
                # protein.append(f'"{y_name}": ({prop_str})')
                node2['type'] = 'protein'

            elif y_type == "drug":
                # result = session.execute(f"USE prime_kg; INSERT VERTEX DRUG(id, name, source) VALUES '{y_id}':({y_id}, \"{y_name}\", \"{y_source}\");")
                # prop_str = f'"{y_id}", "{y_name}", "{y_source}"'
                # drug.append(f'"{y_name}": ({prop_str})')
                node2['type'] = 'drug'
            elif y_type == "disease":
                # result = session.execute(f"USE prime_kg; INSERT VERTEX DISEASE(id, name, source) VALUES '{y_id}':({int(y_id)}, \"{y_name}\", \"{y_source}\");")
                # prop_str = f'"{y_id}", "{y_name}", "{y_source}"'
                # disease.append(f'"{y_name}": ({prop_str})')
                node2['type'] = 'disease'
            
            node2['name'] = y_name
            node2['source'] = y_source

            # print("Second -> ", result)
            # Insert edge
            # query = f"USE prime_kg; INSERT EDGE Interaction(relation, display_relation) VALUES '{x_id}'->'{y_id}':(\"{relation}\", \"{display_relation}\");"
            # prop_str = f'"{x_name}"->"{y_name}":(\"{relation}\", \"{display_relation}\")'
            # edge.append(prop_str)
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
            # result = session.execute(query)
            # print("Three -> ", result, query)

# Close the session
# session.release()