"""
--------------------------------------------------------------------------------------------------------
Abbreviations:
TARGETID    TTD Target ID
TARGNAME    Target Name
INDICATI    Clinical Status    Disease Entry [ICD-11]
--------------------------------------------------------------------------------------------------------
T00043    TARGETID    T00043
T00043    TARGNAME    HUMAN cyclin G-associated kinase (GAK)
T00043    INDICATI    Phase 3    COVID-19    [ICD-11: 1D6Y]
T00043    INDICATI    Approved    Rheumatoid arthritis    [ICD-11: FA20]

T00099    TARGETID    T00099
T00099    TARGNAME    HUMAN calpain-1/calpain small subunit 1 heterodimer (CAPN1/CAPNS1)
T00099    INDICATI    Phase 2    COVID-19    [ICD-11: 1D6Y]

T00158    TARGETID    T00158
T00158    TARGNAME    HUMAN glycosylation of host receptor (GHR)
T00158    INDICATI    Phase 3    COVID-19    [ICD-11: 1D6Y]
T00158    INDICATI    Approved    Malaria    [ICD-11: 1F40-1F45]
"""

import os
import json


DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

f = open(DATA_DIR + '\\P1-06-Target_disease.txt', 'r', encoding='utf-8')

entries = {}
current_entry_indications = {}
current_target_id = None

lines = f.readlines()
for line in lines[22:]:

    parts = line.split('\t')
    
    if parts[0].startswith('-') or parts[0].startswith('Abbreviations') or parts[0].startswith('TARGETID') or parts[0].startswith('TARGNAME') or parts[0].startswith('INDICATI') or ( len(parts) == 1 and (parts[0] == '' or parts[0] == '\n')):
        # Skip lines with dashes and section headers
        continue
    elif parts[1] == 'TARGETID':
        # New target entry
        if current_target_id:
            entries[current_target_id]["INDICATI"] = current_entry_indications
            current_entry_indications = []

        current_target_id = parts[2].replace('\n', '')
        current_entry = parts[2].replace('\n', '')
        entries[current_target_id] = {}
    elif parts[1] == 'TARGNAME':
        # Handle drug information
        entries[current_target_id]["TARGNAME"] = parts[2].replace('\n', '')
    elif parts[1] == 'INDICATI':
        clinical_status = parts[2].replace('\n', '')
        disease_entry = parts[3].replace('\n', '')
        
        # Extracting Disease entry, ICD-11, and Clinical status
        # disease_entry = ''
        icd_11 = ''
        
        for part in parts[2:]:
            if part.startswith('[ICD-11'):
                icd_11 = part.split(':')[1].strip().replace(']\n', '')
        
        disease_entry = disease_entry.strip()
        
        if current_entry_indications:
            current_entry_indications.append({
                'Disease entry': disease_entry,
                'ICD-11': icd_11,
                'Clinical status': clinical_status
            })
        else:
            current_entry_indications = [{
                'Disease entry': disease_entry,
                'ICD-11': icd_11,
                'Clinical status': clinical_status
            }]


# Optionally, write the parsed data to a JSON file
with open(DATA_DIR + '\\P1-06-Target_disease.json', 'w') as json_file:
    json.dump(entries, json_file, indent=4)