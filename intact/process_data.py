import xml.etree.ElementTree as ET
from py2neo import Graph, Node, Relationship

# Connect to your Neo4j database
# graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Parse the XML
tree = ET.parse('D:\\workspace\\MedKG\\data\\1312256.xml')
root = tree.getroot()

# Define namespace
namespace = "{http://psi.hupo.org/mi/mif}"

def get_text(element, tag, ns):
    el = element.find(f'{ns}{tag}')
    return el.text if el is not None else None

# Iterate over entries and extract data
for entry in root.findall(f'.//{namespace}entry'):
    source = entry.find(f'{namespace}source')
    experiment_list = entry.find(f'{namespace}experimentList')
    interactor_list = entry.find(f'{namespace}interactorList')
    interaction_list = entry.find(f'{namespace}interactionList')

    # Extract source data
    short_label = source.find(f'{namespace}names/{namespace}shortLabel').text
    primary_ref = source.find(f'{namespace}xref/{namespace}primaryRef').attrib['id']

    # Create a node for the source in Neo4j
    source_node = Node("Source", label=short_label, primaryRef=primary_ref)
    # graph.create(source_node)

    # Extract experiments
    for experiment in experiment_list.findall(f'{namespace}experimentDescription'):
        experiment_id = experiment.attrib['id']
        short_label = get_text(experiment, 'names/shortLabel', namespace)
        full_name = get_text(experiment, 'names/fullName', namespace)
        pubmed_id = experiment.find(f'{namespace}bibref/{namespace}xref/{namespace}primaryRef').attrib['id']
        
        # Extract hostOrganismList
        host_organism = experiment.find(f'{namespace}hostOrganismList/{namespace}hostOrganism')
        host_organism_name = get_text(host_organism, 'names/fullName', namespace) if host_organism else None

        # Extract interactionDetectionMethod
        interaction_method = experiment.find(f'{namespace}interactionDetectionMethod')
        interaction_method_name = get_text(interaction_method, 'names/fullName', namespace) if interaction_method else None

        # Extract participantIdentificationMethod
        participant_method = experiment.find(f'{namespace}participantIdentificationMethod')
        participant_method_name = get_text(participant_method, 'names/fullName', namespace) if participant_method else None

        # Extract attributes (dataset, definition, exp-modification)
        attributes = experiment.find(f'{namespace}attributeList')
        dataset = definition = exp_modification = None

        if attributes:
            for attribute in attributes.findall(f'{namespace}attribute'):
                name = attribute.attrib.get('name')
                if name == "dataset":
                    dataset = attribute.text
                elif name == "definition":
                    definition = attribute.text
                elif name == "exp-modification":
                    exp_modification = attribute.text
        
        # Create an experiment node in Neo4j
        experiment_node = Node(
            "Experiment",
            id=experiment_id,
            label=short_label,
            fullName=full_name,
            pubmed=pubmed_id,
            hostOrganism=host_organism_name,
            interactionMethod=interaction_method_name,
            participantMethod=participant_method_name,
            dataset=dataset,
            definition=definition,
            expModification=exp_modification
        )
        graph.create(experiment_node)

        # Create relationship between source and experiment
        rel = Relationship(source_node, "CONDUCTED", experiment_node)
        graph.create(rel)

    

    # Extract interactors
    for interactor in interactor_list.findall(f'{namespace}interactor'):
        interactor_id = interactor.attrib['id']
        interactor_name = interactor.find(f'{namespace}names/{namespace}shortLabel').text
        full_name = interactor.find(f'{namespace}names/{namespace}fullName').text
        sequence = interactor.find(f'{namespace}sequence').text

        # Create an interactor node in Neo4j
        interactor_node = Node("Interactor", id=interactor_id, name=interactor_name, fullName=full_name, sequence=sequence)
        # graph.create(interactor_node)

    # Extract interactions
    for interaction in interaction_list.findall(f'{namespace}interaction'):
        interaction_id = interaction.attrib['id']
        interaction_label = interaction.find(f'{namespace}names/{namespace}shortLabel').text

        # Create an interaction node in Neo4j
        interaction_node = Node("Interaction", id=interaction_id, label=interaction_label)
        # graph.create(interaction_node)

        # Link participants (interactors) to the interaction
        for participant in interaction.findall(f'{namespace}participantList/{namespace}participant'):
            interactor_ref = participant.find(f'{namespace}interactorRef').text
            # interactor_node = graph.nodes.match("Interactor", id=interactor_ref).first()

            # Create relationship between interaction and interactor
            rel = Relationship(interaction_node, "PARTICIPATES_IN", interactor_node)
            # graph.create(rel)

