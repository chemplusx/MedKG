"""
--------------------------------------------------------------------------------------------------------
Abbreviations:
TARGETID	TTD Target ID
FORMERID	TTD Former Target ID
UNIPROID	Uniprot ID
TARGNAME	Target Name
GENENAME	Target Gene Name
TARGTYPE	Target Type
SYNONYMS	Synonyms
FUNCTION	Function
PDBSTRUC	PDB Structure
BIOCLASS	BioChemical Class
ECNUMBER	EC Number
SEQUENCE	Sequence
DRUGINFO	TTD Drug ID	Drug Name	Highest Clinical Status
--------------------------------------------------------------------------------------------------------

T47101	TARGETID	T47101
T47101	FORMERID	TTDC00024
T47101	UNIPROID	FGFR1_HUMAN
T47101	TARGNAME	Fibroblast growth factor receptor 1 (FGFR1)
T47101	GENENAME	FGFR1
T47101	TARGTYPE	Successful
T47101	SYNONYMS	c-fgr; bFGF-R-1; bFGF-R; N-sam; HBGFR; Fms-like tyrosine kinase 2; FLT2; FLT-2; FLG; FGFR-1; FGFBR; CEK; CD331 antigen; CD331; Basic fibroblast growth factor receptor 1; BFGFR
T47101	FUNCTION	Required for normal mesoderm patterning and correct axial organization during embryonic development, normal skeletogenesis and normal development of the gonadotropin-releasing hormone (GnRH) neuronal system. Phosphorylates PLCG1, FRS2, GAB1 and SHB. Ligand binding leads to the activation of several signaling cascades. Activation of PLCG1 leads to the production of the cellular signaling molecules diacylglycerol and inositol 1,4,5-trisphosphate. Phosphorylation of FRS2 triggers recruitment of GRB2, GAB1, PIK3R1 and SOS1, and mediates activation of RAS, MAPK1/ERK2, MAPK3/ERK1 and the MAP kinase signaling pathway, as well as of the AKT1 signaling pathway. Promotes phosphorylation of SHC1, STAT1 and PTPN11/SHP2. In the nucleus, enhances RPS6KA1 and CREB1 activity and contributes to the regulation of transcription. FGFR1 signaling is down-regulated by IL17RD/SEF, and by FGFR1 ubiquitination, internalization and degradation. Tyrosine-protein kinase that acts as cell-surface receptor for fibroblast growth factors and plays an essential role in the regulation of embryonic development, cell proliferation, differentiation and migration.
T47101	PDBSTRUC	6MZW; 6MZQ; 6C1O; 6C1C; 6C1B
T47101	BIOCLASS	Kinase
T47101	ECNUMBER	EC 2.7.10.1
T47101	SEQUENCE	MWSWKCLLFWAVLVTATLCTARPSPTLPEQAQPWGAPVEVESFLVHPGDLLQLRCRLRDDVQSINWLRDGVQLAESNRTRITGEEVEVQDSVPADSGLYACVTSSPSGSDTTYFSVNVSDALPSSEDDDDDDDSSSEEKETDNTKPNRMPVAPYWTSPEKMEKKLHAVPAAKTVKFKCPSSGTPNPTLRWLKNGKEFKPDHRIGGYKVRYATWSIIMDSVVPSDKGNYTCIVENEYGSINHTYQLDVVERSPHRPILQAGLPANKTVALGSNVEFMCKVYSDPQPHIQWLKHIEVNGSKIGPDNLPYVQILKTAGVNTTDKEMEVLHLRNVSFEDAGEYTCLAGNSIGLSHHSAWLTVLEALEERPAVMTSPLYLEIIIYCTGAFLISCMVGSVIVYKMKSGTKKSDFHSQMAVHKLAKSIPLRRQVTVSADSSASMNSGVLLVRPSRLSSSGTPMLAGVSEYELPEDPRWELPRDRLVLGKPLGEGCFGQVVLAEAIGLDKDKPNRVTKVAVKMLKSDATEKDLSDLISEMEMMKMIGKHKNIINLLGACTQDGPLYVIVEYASKGNLREYLQARRPPGLEYCYNPSHNPEEQLSSKDLVSCAYQVARGMEYLASKKCIHRDLAARNVLVTEDNVMKIADFGLARDIHHIDYYKKTTNGRLPVKWMAPEALFDRIYTHQSDVWSFGVLLWEIFTLGGSPYPGVPVEELFKLLKEGHRMDKPSNCTNELYMMMRDCWHAVPSQRPTFKQLVEDLDRIVALTSNQEYLDLSMPLDQYSPSFPDTRSSTCSSGEDSVFSHEPLPEEPCLPRHPAQLANGGLKRR
T47101	DRUGINFO	D0O6UY	Pemigatinib	Approved
T47101	DRUGINFO	D09HNV	Intedanib	Approved
T47101	DRUGINFO	D01PZD	Romiplostim	Approved
T47101	DRUGINFO	D07PQJ	ARQ-087	Phase 3
T47101	DRUGINFO	D05PWX	Sulfatinib	Phase 3
T47101	DRUGINFO	D0A1AQ	Rosiglitazone + metformin	Phase 3
T47101	DRUGINFO	D02WVT	E-3810	Phase 3
T47101	DRUGINFO	D0NU0U	AZD4547	Phase 2/3
"""

import os
import json

# Initialize variables to store parsed data
targets = {}
current_target_id = None
current_drug_info = []

# Split data by lines and process each line
# lines = data.strip().split('\n')

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

f = open(DATA_DIR + '\\P1-01-TTD_target_download.txt', 'r', encoding='utf-8')

lines = f.readlines()

for line in lines[32:]:
    # Split line by tabs
    parts = line.split('\t')
    
    if parts[0].startswith('-') or parts[0].startswith('Abbreviations') or parts[0].startswith('TARGETID') or parts[0].startswith('TARGNAME') or parts[0].startswith('INDICATI') or ( len(parts) == 1 and (parts[0] == '' or parts[0] == '\n')):
        # Skip lines with dashes and section headers
        continue
    elif parts[1] == 'TARGETID':
        # New target entry
        if current_target_id:
            targets[current_target_id]['DRUGINFO'] = current_drug_info
            current_drug_info = []

        current_target_id = parts[2]
        targets[current_target_id] = {}
    elif parts[1] == 'DRUGINFO':
        # Handle drug information
        drug_info = {
            'TTD Drug ID': parts[2],
            'Drug Name': parts[3],
            'Highest Clinical Status': parts[4]
        }
        current_drug_info.append(drug_info)
    else:
        # Regular attribute for the current target
        attribute_name = parts[1]
        attribute_value = parts[2]
        if attribute_name == 'DRUGINFO':
            continue  # Skip DRUGINFO lines here (handled separately)
        if attribute_name not in targets[current_target_id]:
            targets[current_target_id][attribute_name] = attribute_value
        else:
            # If attribute already exists, handle as a list (for SYNONYMS and PDBSTRUC)
            if isinstance(targets[current_target_id][attribute_name], list):
                targets[current_target_id][attribute_name].append(attribute_value)
            else:
                targets[current_target_id][attribute_name] = [targets[current_target_id][attribute_name], attribute_value]

f.close()

# Assign drug information to each target

response_dict = {}

# Print out the parsed targets for verification
for target_id, target_info in targets.items():
    print(f"Target ID: {target_id}")
    info = {}
    for key, value in target_info.items():
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], str):
                value_str = ", ".join(value)
            else:
                value_str = value
        else:
            value_str = value
        # print(f"{key}: {value_str}")
        info[key] = value_str
    
    response_dict[target_id] = target_info

f = open(DATA_DIR + '\\P1-01-TTD_target_download.json', 'w', encoding='utf-8')
print("Writing to file...")
json.dump(response_dict, f, indent=4, ensure_ascii=False)
f.close()