from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
import csv

# Nebula Graph connection configuration
config = Config()
config.max_connection_pool_size = 10
connection_pool = ConnectionPool()
connection_pool.init([('192.168.0.115', 9669)], config)

# Create a session to execute queries
session = connection_pool.get_session('root', 'nebula')
global_dict = {}
with open("D:\workspace\data\PrimeKG_data\dataverse_files\\nodes.csv") as file:
    reader = csv.DictReader(file)
    for row in reader:
        node_index = row['node_index']
        node_id = row['node_id'].replace('"', '\\"')
        node_type = row['node_type'].replace('"', '\\"')
        node_name = row['node_name'].replace('"', '\\"')
        node_source = row['node_source'].replace('"', '\\"')

        global_dict[node_index] = {
            "id": node_id,
            "type": node_type,
            "name": node_name,
            "source": node_source
        }

# Read the CSV data and insert into Nebula Graph
with open('D:\workspace\data\PrimeKG_data\dataverse_files\drug_features.csv', 'r') as file:
    # next(file)  # Skip the header row
    n = 0
    tot = 7959
    reader = csv.DictReader(file)
    for row in reader:
        if n%10000 ==0:
            print("Done by ", (n/tot)*100)
        n+=1
        node_index = row['node_index']
        description = row['description'].replace('"', '\\"')
        half_life = row['half_life'].replace('"', '\\"')
        indication = row['indication'].replace('"', '\\"')
        mechanism_of_action = row['mechanism_of_action'].replace('"', '\\"')
        protein_binding = row['protein_binding'].replace('"', '\\"')
        pharmacodynamics = row['pharmacodynamics'].replace('"', '\\"')
        state = row['state'].replace('"', '\\"')
        atc_1 = row['atc_1'].replace('"', '\\"')
        atc_2 = row['atc_2'].replace('"', '\\"')
        atc_3 = row['atc_3'].replace('"', '\\"')
        atc_4 = row['atc_4'].replace('"', '\\"')
        category = row['category'].replace('"', '\\"')
        group_name = row['group'].replace('"', '\\"')
        pathway = row['pathway'].replace('"', '\\"')
        molecular_weight = row['molecular_weight']
        tpsa = row['tpsa']
        clogp = row['clogp']
        # Insert vertex
        query = f'use prime_kg; upsert vertex on DRUG set id, description, half_life, indication, mechanism_of_action, protein_binding, pharmacodynamics, state, atc_1, atc_2, atc_3, atc_4, category, group, pathway, molecular_weight, tpsa, clogp 
        ) VALUES "{node_index}":({node_index}, "{description}", "{half_life}", "{indication}", "{mechanism_of_action}", "{protein_binding}", "{pharmacodynamics}", "{state}", "{atc_1}", "{atc_2}", "{atc_3}", "{atc_4}", "{category}", "{group_name}", "{pathway}", "{molecular_weight}", "{tpsa}", "{clogp}");'
        result = session.execute(query)
        print("Drug: ", result)

with open('D:\workspace\data\PrimeKG_data\dataverse_files\disease_features.csv', 'r') as file:
    # next(file)  # Skip the header row
    n = 0
    tot = 44395
    reader = csv.DictReader(file)
    for row in reader:
        if n%10000 ==0:
            print("Done by ", (n/tot)*100)
        n+=1
        node_index = int(row['node_index'])
        mondo_id = row['mondo_id'].replace('"', '\\"')
        mondo_name = row['mondo_name'].replace('"', '\\"')
        group_id_bert = row['group_id_bert'].replace('"', '\\"')
        group_name_bert = row['group_name_bert'].replace('"', '\\"')
        mondo_definition = row['mondo_definition'].replace('"', '\\"')
        umls_description = row['umls_description'].replace('"', '\\"')
        orphanet_definition = row['orphanet_definition'].replace('"', '\\"')
        orphanet_prevalence = row['orphanet_prevalence'].replace('"', '\\"')
        orphanet_epidemiology = row['orphanet_epidemiology'].replace('"', '\\"')
        orphanet_clinical_description = row['orphanet_clinical_description'].replace('"', '\\"')
        orphanet_management_and_treatment = row['orphanet_management_and_treatment'].replace('"', '\\"')
        mayo_symptoms = row['mayo_symptoms'].replace('"', '\\"')
        mayo_causes = row['mayo_causes'].replace('"', '\\"')
        mayo_risk_factors = row['mayo_risk_factors'].replace('"', '\\"')
        mayo_complications = row['mayo_complications'].replace('"', '\\"')
        mayo_prevention = row['mayo_prevention'].replace('"', '\\"')
        mayo_see_doc = row['mayo_see_doc'].replace('"', '\\"')
        
        # Insert vertex
        query = f'use prime_kg; INSERT VERTEX DISEASE(id, mondo_name, mondo_definition, umls_description, orphanet_definition, orphanet_prevalence, orphanet_epidemiology, orphanet_clinical_description, orphanet_management_and_treatment, mayo_symptoms, mayo_causes, mayo_risk_factors, mayo_complications, mayo_prevention, mayo_see_doc) VALUES "{node_index}":({node_index}, "{mondo_name}", "{mondo_definition}", "{umls_description}", "{orphanet_definition}", "{orphanet_prevalence}", "{orphanet_epidemiology}", "{orphanet_clinical_description}", "{orphanet_management_and_treatment}", "{mayo_symptoms}", "{mayo_causes}", "{mayo_risk_factors}", "{mayo_complications}", "{mayo_prevention}", "{mayo_see_doc}");'
        session.execute(query)
