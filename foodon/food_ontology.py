import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from neo4j import GraphDatabase

def download_owl(url, file_path):
    response = requests.get(url)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f"OWL file downloaded and saved as {file_path}")

def parse_owl(file_path):
    g = Graph()
    g.parse(file_path, format="xml")
    print(f"Parsed {len(g)} triples from the OWL file.")
    return g

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.mapVal = {}

    def close(self):
        self.driver.close()

    def create_constraints(self):
        # with self.driver.session() as session:
        #     session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Food) REQUIRE n.uri IS UNIQUE")
        print("Created constraints in Neo4j.")

    def insert_data(self, graph):
        with self.driver.session() as session:
            # Insert all entities (classes, properties, individuals)
            entities=[]
            for s, p, o in graph.triples((None, RDF.type, None)):
                if isinstance(o, (URIRef, Literal)) and o in [OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, OWL.NamedIndividual]:
                    if "FOODON_" in str(s):
                        entity = {
                            "uri": str(s),
                            "label": str(graph.value(s, RDFS.label)) if graph.value(s, RDFS.label) else None,
                            "type": str(o).split("#")[-1] if isinstance(o, URIRef) else str(o),
                            "definition": str(graph.value(s, URIRef("http://purl.obolibrary.org/obo/IAO_0000115"))) if graph.value(s, URIRef("http://purl.obolibrary.org/obo/IAO_0000115")) else None
                        }
                        entities.append(entity)
                    else:
                        self.mapVal


            print("""
                UNWIND $entities AS entity
                MERGE (e:OntologyEntity {uri: entity.uri})
                SET e.label = entity.label,
                    e.type = entity.type,
                    e.definition = entity.definition
            """, entities=entities)

            # Insert relationships
            relationships = []
            for s, p, o in graph.triples((None, None, None)):
                if isinstance(s, URIRef) and isinstance(o, URIRef) and p != RDF.type:
                    relationship = {
                        "subject": str(s),
                        "type": str(p).split("/")[-1].split("#")[-1],
                        "object": str(o)
                    }
                    relationships.append(relationship)


            print("""
                UNWIND $relationships AS rel
                MATCH (s:OntologyEntity {uri: rel.subject})
                MATCH (o:OntologyEntity {uri: rel.object})
                CALL apoc.merge.relationship(s, rel.type, {}, {}, o)
                YIELD relationship
                RETURN count(*)
            """, relationships=relationships)

            # Insert data properties
            data_properties = []
            for s, p, o in graph.triples((None, None, None)):
                if isinstance(s, URIRef) and isinstance(o, Literal):
                    data_property = {
                        "subject": str(s),
                        "predicate": str(p).split("/")[-1].split("#")[-1],
                        "object": str(o)
                    }
                    data_properties.append(data_property)

            print("""
                UNWIND $dataProperties AS prop
                MATCH (e:OntologyEntity {uri: prop.subject})
                SET e[prop.predicate] = prop.object
            """, dataProperties=data_properties)

        print("Inserted data into Neo4j.")

if __name__ == "__main__":
    owl_url = "https://raw.githubusercontent.com/FoodOntology/foodon/master/foodon.owl"
    owl_file = "D:\\workspace\\MedKG\\data\\foodon.xml"
    neo4j_uri = "bolt://localhost:7687"  # Update with your Neo4j URI
    neo4j_user = "neo4j"  # Update with your Neo4j username
    neo4j_password = "password"  # Update with your Neo4j password

    # Download and parse OWL
    # download_owl(owl_url, owl_file)
    graph = parse_owl(owl_file)

    # Insert data into Neo4j
    connection = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
    connection.create_constraints()
    connection.insert_data(graph)
    connection.close()

    print("Process completed successfully.")
