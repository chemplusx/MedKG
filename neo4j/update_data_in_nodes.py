import csv
from neo4j import GraphDatabase, RoutingControl
URI = "neo4j://192.168.0.115:7687"
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

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Read the CSV data and insert into Nebula Graph
    # with open('D:\workspace\data\PrimeKG_data\dataverse_files\drug_features.csv', 'r') as file:
    #     # next(file)  # Skip the header row
    #     n = 0
    #     tot = 7959
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         if n%10000 ==0:
    #             print("Done by ", (n/tot)*100)
    #         n+=1
    #         node_index = row['node_index']
    #         name = global_dict.get(node_index, {}).get("name", None)
    #         if not name:
    #             continue
    #         description = row['description'].replace('"', '\\"')
    #         half_life = row['half_life'].replace('"', '\\"')
    #         indication = row['indication'].replace('"', '\\"')
    #         mechanism_of_action = row['mechanism_of_action'].replace('"', '\\"')
    #         protein_binding = row['protein_binding'].replace('"', '\\"')
    #         pharmacodynamics = row['pharmacodynamics'].replace('"', '\\"')
    #         state = row['state'].replace('"', '\\"')
    #         atc_1 = row['atc_1'].replace('"', '\\"')
    #         atc_2 = row['atc_2'].replace('"', '\\"')
    #         atc_3 = row['atc_3'].replace('"', '\\"')
    #         atc_4 = row['atc_4'].replace('"', '\\"')
    #         category = row['category'].replace('"', '\\"')
    #         group_name = row['group'].replace('"', '\\"')
    #         pathway = row['pathway'].replace('"', '\\"')
    #         molecular_weight = row['molecular_weight']
    #         tpsa = row['tpsa']
    #         clogp = row['clogp']
    #         # Insert vertex
    #         # query = f'use prime_kg; upsert vertex on DRUG set id, description, half_life, indication, mechanism_of_action, protein_binding, pharmacodynamics, state, atc_1, atc_2, atc_3, atc_4,
    #         #   category, group, pathway, molecular_weight, tpsa, clogp 
    #         # ) VALUES "{node_index}":({node_index}, "{description}", "{half_life}", "{indication}", "{mechanism_of_action}", "{protein_binding}", "{pharmacodynamics}", "{state}", "{atc_1}", 
    #         # "{atc_2}", "{atc_3}", "{atc_4}", "{category}", "{group_name}", "{pathway}", "{molecular_weight}", "{tpsa}", "{clogp}");'
    #         # result = session.execute(query)
    #         # print("Drug: ", result)
    #         try:
    #             # resp = driver.execute_query(
    #             #     "MATCH (n:protein {name: 'PHYHIP'}) "
    #             #     "return n"
    #             # )
    #             resp = driver.execute_query(
    #                 "MATCH (n:drug {name: $name}) "
    #                 "SET n.description = $description "
    #                 "SET n.half_life = $half_life "
    #                 "SET n.indication = $indication "
    #                 "SET n.mechanism_of_action = $mechanism_of_action "
    #                 "SET n.protein_binding = $protein_binding "
    #                 "SET n.pharmacodynamics = $pharmacodynamics "
    #                 "SET n.state = $state "
    #                 "SET n.atc_1 = $atc_1 "
    #                 "SET n.atc_2 = $atc_2 "
    #                 "SET n.atc_3 = $atc_3 "
    #                 "SET n.atc_4 = $atc_4 "
    #                 "SET n.category = $category "
    #                 "SET n.group = $group_name "
    #                 "SET n.pathway = $pathway "
    #                 "SET n.molecular_weight = $molecular_weight "
    #                 "SET n.tpsa = $tpsa "
    #                 "SET n.clogp = $clogp "
    #                 "RETURN n.description;",
    #                 name=name, description=description, half_life=half_life, indication=indication, mechanism_of_action=mechanism_of_action, protein_binding=protein_binding, pharmacodynamics=pharmacodynamics,
    #                 state=state, atc_1=atc_1, atc_2=atc_2, atc_3=atc_3, atc_4=atc_4, category=category, group_name=group_name, pathway=pathway, molecular_weight=molecular_weight, tpsa=tpsa, clogp=clogp, database_="neo4j",
    #             ) 
    #             print("After rr: ", resp)
    #         except Exception as ex:
    #             print("Fata bhai kuch to -> ", ex)





    # with open('D:\workspace\data\PrimeKG_data\dataverse_files\disease_features.csv', 'r') as file:
    #     # next(file)  # Skip the header row
    #     n = 0
    #     tot = 44395
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         if n%10000 ==0:
    #             print("Done by ", (n/tot)*100)
    #         n+=1
    #         node_index = int(row['node_index'])
    #         name = global_dict.get(str(node_index), {}).get("name", None)
    #         if not name:
    #             continue
    #         mondo_id = row['mondo_id'].replace('"', '\\"')
    #         mondo_name = row['mondo_name'].replace('"', '\\"')
    #         group_id_bert = row['group_id_bert'].replace('"', '\\"')
    #         group_name_bert = row['group_name_bert'].replace('"', '\\"')
    #         mondo_definition = row['mondo_definition'].replace('"', '\\"')
    #         umls_description = row['umls_description'].replace('"', '\\"')
    #         orphanet_definition = row['orphanet_definition'].replace('"', '\\"')
    #         orphanet_prevalence = row['orphanet_prevalence'].replace('"', '\\"')
    #         orphanet_epidemiology = row['orphanet_epidemiology'].replace('"', '\\"')
    #         orphanet_clinical_description = row['orphanet_clinical_description'].replace('"', '\\"')
    #         orphanet_management_and_treatment = row['orphanet_management_and_treatment'].replace('"', '\\"')
    #         mayo_symptoms = row['mayo_symptoms'].replace('"', '\\"')
    #         mayo_causes = row['mayo_causes'].replace('"', '\\"')
    #         mayo_risk_factors = row['mayo_risk_factors'].replace('"', '\\"')
    #         mayo_complications = row['mayo_complications'].replace('"', '\\"')
    #         mayo_prevention = row['mayo_prevention'].replace('"', '\\"')
    #         mayo_see_doc = row['mayo_see_doc'].replace('"', '\\"')
            
    #         # Insert vertex
    #         # query = f'use prime_kg; INSERT VERTEX DISEASE(id, mondo_name, mondo_definition, umls_description, orphanet_definition, 
    #         # orphanet_prevalence, orphanet_epidemiology, orphanet_clinical_description, orphanet_management_and_treatment, mayo_symptoms,
    #         #   mayo_causes, mayo_risk_factors, mayo_complications, mayo_prevention, mayo_see_doc) VALUES 
    #         #   "{node_index}":({node_index}, "{mondo_name}", "{mondo_definition}", "{umls_description}", "{orphanet_definition}", 
    #         #   "{orphanet_prevalence}", "{orphanet_epidemiology}", "{orphanet_clinical_description}", "{orphanet_management_and_treatment}", 
    #         #   "{mayo_symptoms}", "{mayo_causes}", "{mayo_risk_factors}", "{mayo_complications}", "{mayo_prevention}", "{mayo_see_doc}");'
    #         # session.execute(query)

    #         try:
    #             resp = driver.execute_query(
    #                 "MATCH (n:disease {name: $name}) "
    #                 "SET n.mondo_name = $mondo_name "
    #                 "SET n.mondo_definition = $mondo_definition "
    #                 "SET n.umls_description = $umls_description "
    #                 "SET n.orphanet_definition = $orphanet_definition "
    #                 "SET n.orphanet_prevalence = $orphanet_prevalence "
    #                 "SET n.orphanet_epidemiology = $orphanet_epidemiology "
    #                 "SET n.orphanet_clinical_description = $orphanet_clinical_description "
    #                 "SET n.orphanet_management_and_treatment = $orphanet_management_and_treatment "
    #                 "SET n.mayo_symptoms = $mayo_symptoms "
    #                 "SET n.mayo_causes = $mayo_causes "
    #                 "SET n.mayo_risk_factors = $mayo_risk_factors "
    #                 "SET n.mayo_complications = $mayo_complications "
    #                 "SET n.mayo_prevention = $mayo_prevention "
    #                 "SET n.mayo_see_doc = $mayo_see_doc "
    #                 "RETURN n.description;",
    #                 name=name, mondo_name=mondo_name, mondo_definition=mondo_definition, umls_description=umls_description, orphanet_definition=orphanet_definition, 
    #                 orphanet_prevalence=orphanet_prevalence, orphanet_epidemiology=orphanet_epidemiology, orphanet_clinical_description=orphanet_clinical_description, 
    #                 orphanet_management_and_treatment=orphanet_management_and_treatment, mayo_symptoms=mayo_symptoms, mayo_causes=mayo_causes, mayo_risk_factors=mayo_risk_factors, 
    #                 mayo_complications=mayo_complications, mayo_prevention=mayo_prevention, mayo_see_doc=mayo_see_doc, database_="neo4j",
    #             ) 
    #             # print("After rr: ", resp)
    #         except Exception as ex:
    #             print("Fata bhai kuch to -> ", ex)

    with open('D:\workspace\data\PrimeKG_data\dataverse_files\gene_features.csv', 'r') as file:
        # next(file)  # Skip the header row
        n = 0
        tot = 44395
        reader = csv.DictReader(file)
        for row in reader:
            if n%10000 ==0:
                print("Done by ", (n/tot)*100)
            n+=1
            initial_alias = row['initial_alias']
            converted_alias = row['converted_alias'].replace('"', '\\"')
            name = row['name'].replace('"', '\\"')
            description = row['description'].replace('"', '\\"')
            
            # Insert vertex
            # query = f'use prime_kg; INSERT VERTEX DISEASE(id, mondo_name, mondo_definition, umls_description, orphanet_definition, 
            # orphanet_prevalence, orphanet_epidemiology, orphanet_clinical_description, orphanet_management_and_treatment, mayo_symptoms,
            #   mayo_causes, mayo_risk_factors, mayo_complications, mayo_prevention, mayo_see_doc) VALUES 
            #   "{node_index}":({node_index}, "{mondo_name}", "{mondo_definition}", "{umls_description}", "{orphanet_definition}", 
            #   "{orphanet_prevalence}", "{orphanet_epidemiology}", "{orphanet_clinical_description}", "{orphanet_management_and_treatment}", 
            #   "{mayo_symptoms}", "{mayo_causes}", "{mayo_risk_factors}", "{mayo_complications}", "{mayo_prevention}", "{mayo_see_doc}");'
            # session.execute(query)

            try:
                resp = driver.execute_query(
                    "MATCH (n:protein {name: $name}) "
                    "SET n.description = $description "
                    "RETURN n.description;",
                    name=name, description=description, database_="neo4j",
                ) 
                # print("After rr: ", resp)
            except Exception as ex:
                print("Fata bhai kuch to -> ", ex)