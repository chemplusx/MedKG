"""
--------------------------------------------------------------------------------------------------------
Abbreviations:
TTDDRUID    TTD Drug ID
DRUGNAME    Drug Name
INDICATI    Indication    Disease entry    ICD-11    Clinical status
--------------------------------------------------------------------------------------------------------

TTDDRUID    DZB84T      
DRUGNAME    Maralixibat      
INDICATI    Pruritus    ICD-11: EC90    Approved
INDICATI    Progressive familial intrahepatic cholestasis    ICD-11: 5C58.03    Phase 3
INDICATI    Alagille syndrome    ICD-11: LB20.0Y    Phase 2

TTDDRUID    DZA90G      
DRUGNAME    BNT162b2      
INDICATI    Coronavirus Disease 2019 (COVID-19)    ICD-11: 1D6Y    Approved

TTDDRUID    DZ8DF0      
DRUGNAME    Nedosiran      
INDICATI    Primary hyperoxaluria type 1    ICD-11: 5C51.20    Approved
INDICATI    Hyperoxaluria    ICD-11: 5C51.2    Phase 2
"""

import json
import os

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

f = open(DATA_DIR + '\\P1-05-Drug_disease.txt', 'r', encoding='utf-8')

lines = f.readlines()


entries = []
current_entry = {}

for line in lines[22:]:
    if line.startswith('TTDDRUID'):
        if current_entry:
            entries.append(current_entry)
            current_entry = {}
        current_entry[line.split()[0]] = line.split()[1]
    elif line.startswith('DRUGNAME'):
        current_entry[line.split()[0]] = line.split()[1]
    elif line.startswith('INDICATI'):
        parts = line.split('\t')
        indication_key = parts[0].replace('\n', '')
        disease_entry = parts[1].replace('\n', '')
        
        # Extracting Disease entry, ICD-11, and Clinical status
        # disease_entry = ''
        icd_11 = ''
        clinical_status = ''
        
        for part in parts[2:]:
            if part.startswith('ICD-11'):
                icd_11 = part.split(':')[1].strip().replace('\n', '')
            elif part.replace('\n', '') in ['Approved', 'Phase 2', 'Phase 3']:  # Assuming Clinical status is the last part
                clinical_status = part.strip().replace('\n', '')
        
        disease_entry = disease_entry.strip()
        
        if indication_key in current_entry:
            current_entry[indication_key].append({
                'Disease entry': disease_entry,
                'ICD-11': icd_11,
                'Clinical status': clinical_status
            })
        else:
            current_entry[indication_key] = [{
                'Disease entry': disease_entry,
                'ICD-11': icd_11,
                'Clinical status': clinical_status
            }]

# Append the last entry
if current_entry:
    entries.append(current_entry)

# Displaying the parsed data
for entry in entries:
    print(entry)
    print('---')

f.close()

with open(DATA_DIR + '\\P1-05-Drug_disease.json', 'w', encoding='utf-8') as f:
    json.dump(entries, f, indent=4)