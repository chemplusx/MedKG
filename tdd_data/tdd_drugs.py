"""
_______________________________________________________________________		

Abbreviations:
DRUG__ID	DRUG ID
TRADNAME	Trade Name
DRUGCOMP	Company
THERCLAS	Therapeutic Class
DRUGTYPE	Drug Type
DRUGINCH	InChI
DRUGINKE	InChIKey
DRUGSMIL	Canonical SMILES
HIGHSTAT	Highest status
COMPCLAS	Compound Class
_______________________________________________________________________		

D00UZR	DRUG__ID	D00UZR
D00UZR	TRADNAME	Ibrance
D00UZR	DRUGCOMP	Onyx Pharmaceuticals; Pfizer
D00UZR	THERCLAS	Anticancer Agents
D00UZR	DRUGTYPE	Small molecular drug
D00UZR	DRUGINCH	1S/C24H29N7O2/c1-15-19-14-27-24(28-20-8-7-18(13-26-20)30-11-9-25-10-12-30)29-22(19)31(17-5-3-4-6-17)23(33)21(15)16(2)32/h7-8,13-14,17,25H,3-6,9-12H2,1-2H3,(H,26,27,28,29)
D00UZR	DRUGINKE	AHJRHEGDXFFMBM-UHFFFAOYSA-N
D00UZR	DRUGSMIL	CC1=C(C(=O)N(C2=NC(=NC=C12)NC3=NC=C(C=C3)N4CCNCC4)C5CCCC5)C(=O)C
D00UZR	HIGHSTAT	Approved

D07NVU	DRUG__ID	D07NVU
D07NVU	TRADNAME	Rydapt
D07NVU	DRUGCOMP	Novartis
D07NVU	THERCLAS	Anticancer Agents
D07NVU	DRUGTYPE	Small molecular drug
D07NVU	DRUGINCH	1S/C35H30N4O4/c1-35-32(42-3)25(37(2)34(41)19-11-5-4-6-12-19)17-26(43-35)38-23-15-9-7-13-20(23)28-29-22(18-36-33(29)40)27-21-14-8-10-16-24(21)39(35)31(27)30(28)38/h4-16,25-26,32H,17-18H2,1-3H3,(H,36,40)/t25-,26-,32-,35+/m1/s1
D07NVU	DRUGINKE	BMGQWWVMWDBQGC-IIFHNQTCSA-N
D07NVU	DRUGSMIL	CC12C(C(CC(O1)N3C4=CC=CC=C4C5=C6C(=C7C8=CC=CC=C8N2C7=C53)CNC6=O)N(C)C(=O)C9=CC=CC=C9)OC
D07NVU	HIGHSTAT	Approved
"""

import os

# Initialize variables to store parsed data
parsed_drugs = []
current_drug_id = None
current_drug_info = {}

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

synonyms = {}

def read_synonyms():
    """
    --------------------------------------------------------------------------------------------------------
    Abbreviation Index:

    TTDDRUID	TTD Drug ID
    DRUGNAME	Drug Name
    SYNONYMS	Synonyms
    --------------------------------------------------------------------------------------------------------


    D00AAN	TTDDRUID	D00AAN
    D00AAN	DRUGNAME	8-O-(4-chlorobenzenesulfonyl)manzamine F
    D00AAN	SYNONYMS	CHEMBL400717

    D00AAU	TTDDRUID	D00AAU
    D00AAU	DRUGNAME	3-[1-ethyl-2-(3-hydroxyphenyl)butyl]phenol
    D00AAU	SYNONYMS	Metahexes trol
    D00AAU	SYNONYMS	3,3'-Hexestrol
    D00AAU	SYNONYMS	Metahexestrol
    D00AAU	SYNONYMS	3,3'-Hes
    D00AAU	SYNONYMS	68266-24-0
    D00AAU	SYNONYMS	meso-3,4-Bis(3'-hydroxyphenyl)hexane
    D00AAU	SYNONYMS	BRN 3971661
    D00AAU	SYNONYMS	NSC-297,170
    D00AAU	SYNONYMS	meso-3,3'-(1,2-Diethylethylene)diphenol
    D00AAU	SYNONYMS	NSC-297170
    D00AAU	SYNONYMS	(R*,S*)-3,3'-(1,2-Diethyl-1,2-ethanediyl)bisphenol
    D00AAU	SYNONYMS	Phenol, 3,3'-(1,2-diethyl-1,2-ethanediyl)bis-, (R*,S*)-
    D00AAU	SYNONYMS	Phenol, 3,3'-((1R,2S)-1,2-diethyl-1,2-ethanediyl)bis-, rel-
    D00AAU	SYNONYMS	UNII-DSF584X94B
    D00AAU	SYNONYMS	DSF584X94B
    D00AAU	SYNONYMS	NSC 297170
    D00AAU	SYNONYMS	3-[4-(3-hydroxyphenyl)hexan-3-yl]phenol
    D00AAU	SYNONYMS	AC1L2OPY
    D00AAU	SYNONYMS	1,2-Diethyl-1,2-bis(3'-hydroxyphenyl)ethane
    D00AAU	SYNONYMS	AC1Q79WV
    D00AAU	SYNONYMS	CHEMBL18268
    D00AAU	SYNONYMS	SCHEMBL5014485
    """

    
    f = open(DATA_DIR + '\\P1-04-Drug_synonyms.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    current_drug_id = None
    current_synonyms = []
    for line in lines[28:]:
        # Split line by tabs
        parts = line.split('\t')
        
        if parts[0].startswith('-') or parts[0].startswith('Abbreviation Index') or parts[0].startswith('TTDDRUID') or parts[0].startswith('DRUGNAME') or parts[0].startswith('SYNONYMS') or ( len(parts) == 1 and (parts[0] == '' or parts[0] == '\n')):
            # Skip lines with dashes and section headers
            continue
        elif parts[1] == 'TTDDRUID':
            # New target entry
            if current_drug_id:
                synonyms[current_drug_id] = current_synonyms
                current_synonyms = []
            current_drug_id = parts[2].replace('\n', '')
        elif parts[1] == 'SYNONYMS':
            # Handle drug information
            current_synonyms.append(parts[2].replace('\n', ''))

read_synonyms()


f = open(DATA_DIR + '\\P1-02-TTD_drug_download.txt', 'r', encoding='utf-8')

lines = f.readlines()

for line in lines[28:]:
    if line.startswith('_') or line.strip() == '':
        continue  # Skip separator lines and empty lines
    
    # Split line by tabs
    parts = line.split('\t')
    
    if parts[1] == 'DRUG__ID':
        # New drug entry
        if current_drug_id:
            current_drug_info['SYNONYMS'] = synonyms[current_drug_id] if current_drug_id in synonyms else []
            parsed_drugs.append(current_drug_info)
        current_drug_id = parts[2].replace('\n', '')
        current_drug_info = {'DRUG__ID': current_drug_id}
    else:
        # Regular attribute for the current drug
        attribute_name = parts[1].replace('\n', '')
        attribute_value = parts[2].replace('\n', '')
        current_drug_info[attribute_name] = attribute_value

# Append the last drug entry
if current_drug_info:
    parsed_drugs.append(current_drug_info)

# Print out the parsed drugs for verification
for drug in parsed_drugs:
    print(drug)
    print()

# Optionally, write the parsed data to a JSON file
import json

with open(DATA_DIR + '\\P1-02-TTD_drug_download.json', 'w') as json_file:
    json.dump(parsed_drugs, json_file, indent=4)
