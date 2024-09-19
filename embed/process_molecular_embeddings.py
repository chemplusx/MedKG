from neo4j import GraphDatabase
from rdkit import Chem

# Assuming you have this function defined
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from mol2vec.features import mol2alt_sentence, mol2sentence, MolSentence, DfVec, sentences2vec

import numpy as np
import pandas as pd
import sys, os

from rdkit import Chem
from rdkit.Chem import PandasTools
# from rdkit.Chem.Draw import IPythonConsole

from mol2vec.features import mol2alt_sentence, mol2sentence, MolSentence, DfVec, sentences2vec
from gensim.models import word2vec


def formula_to_mol(formula):
    # Parse the formula
    elem_dict = {}
    current_element = ''
    current_count = ''
    for char in formula:
        if char.isupper():
            if current_element:
                elem_dict[current_element] = int(current_count) if current_count else 1
            current_element = char
            current_count = ''
        elif char.islower():
            current_element += char
        elif char.isdigit():
            current_count += char
    # Add the last element
    if current_element:
        elem_dict[current_element] = int(current_count) if current_count else 1
    # Create a mol object
    mol = Chem.MolFromSmiles('')
    editable_mol = Chem.EditableMol(mol)
    # Add atoms
    for element, count in elem_dict.items():
        for _ in range(count):
            atom = Chem.Atom(element)
            atom_idx = editable_mol.AddAtom(atom)
    # Get the mol object
    mol = editable_mol.GetMol()
    # Set implicit hydrogens and recalculate valences
    for atom in mol.GetAtoms():
        atom.SetNoImplicit(True)
        atom.UpdatePropertyCache()
    # Try to generate a 3D conformation
    try:
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
    except:
        print("Failed to generate 3D conformation. Returning 2D structure.")
    return mol

model = word2vec.Word2Vec.load('D:\\workspace\\MedKG\\data\\model_300dim.pkl')

def getMolecularEmbeddings(chemicalFormula):
    # Use the function
    mol = formula_to_mol(chemicalFormula)
    
    # Check if the molecule was created successfully
    if mol is not None:
        print("Molecule created successfully")
        print("Molecular Weight:", Descriptors.ExactMolWt(mol))
        t = MolSentence(mol2alt_sentence(mol, 1))
        mv = sentences2vec([t], model, unseen='UNK')
        m2v = DfVec(mv)
        return m2v
    else:
        print("Failed to create molecule")

# Neo4j connection details
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def update_embeddings(tx, label):
    query = (
        f"MATCH (n:{label}) "
        "WHERE (n.chemical_formula) IS NOT NULL "
        "RETURN id(n) AS node_id, n.chemical_formula AS formula"
    )
    results = tx.run(query)
    
    for record in results:
        node_id = record["node_id"]
        formula = record["formula"]
        
        # Convert formula to mol object (you might need to adjust this part)
        try:
            mol = getMolecularEmbeddings(formula)
            
            if mol is not None:
                # Calculate embedding
                embedding = mol.vec[0]
                
                # Update node with new embedding
                update_query = (
                    "MATCH (n) WHERE id(n) = $node_id "
                    "SET n.molecular_embedding = $embedding"
                )
                tx.run(update_query, node_id=node_id, embedding=embedding.tolist())
                print("Updated node with embedding", node_id)
        except Exception as e:
            print("Failed to update node", node_id, e)

def separate_out_chem_data(tx, label):
    query = (
        f"MATCH (n:{label}) "
        "WHERE (n.chemical_data) IS NOT NULL "
        "RETURN id(n) AS node_id, n.chemical_data AS chemdata"
    )
    results = tx.run(query)
    
    for record in results:
        node_id = record["node_id"]
        all_chem_data = record["chemdata"].split(",")
        formula = None
        for cd in all_chem_data:
            if "FORMULA" in cd:
                formula = cd.split(":")[1].strip()
                break
        
        if formula is not None:
            
            # Update node with new embedding
            update_query = (
                "MATCH (n) WHERE id(n) = $node_id "
                "SET n.chemical_formula = $fm"
            )
            tx.run(update_query, node_id=node_id, fm=formula)
        # return

def main():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            # for label in ["Drug", "Compound"]:
            #     session.execute_write(separate_out_chem_data, label)
            for label in ["Drug", "Compound", "Metabolite"]:
                session.execute_write(update_embeddings, label)

if __name__ == "__main__":
    main()