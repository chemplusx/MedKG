package neo4j

import (
	"strings"

	"chemplusx.com/medkg-api/models"
)

func recurseAndBuildPath(connectionmap *map[string][]models.Relationship, nodeMap *map[string]models.Node, nodeId string, visited *map[string]bool, destType *string, totalPath *string, result *[]string) {
	if val, ok := (*nodeMap)[nodeId]; ok && val.NodeType == *destType {
		*result = append(*result, *totalPath)
		return
	}

	for _, rel := range (*connectionmap)[nodeId] {
		// If the target of this relationship is not visited yet
		if _, ok := (*visited)[rel.Target.(string)]; !ok {
			// We need to add this to the path
			(*visited)[rel.Target.(string)] = true
			// Recurse and get the path from this node to the destination
			totalPathForward := *totalPath + "->" + rel.EdgeType + "->" + rel.Target.(string) + "->"
			recurseAndBuildPath(connectionmap, nodeMap, rel.Target.(string), visited, destType, &totalPathForward, result)

		}

		if _, ok := (*visited)[rel.Source.(string)]; !ok {
			// We need to add this to the path
			(*visited)[rel.Source.(string)] = true
			// Recurse and get the path from this node to the destination
			totalPathBackward := *totalPath + "<-" + rel.EdgeType + "<-" + rel.Source.(string) + "->"
			recurseAndBuildPath(connectionmap, nodeMap, rel.Source.(string), visited, destType, &totalPathBackward, result)
		}
	}
}

func checkForSource(nodeProps map[string]interface{}, label string) (string, string) {
	// Check if the node has a source property
	if val1, ok := nodeProps["source"]; ok {
		//Now check if it has a url in it
		if val, ok := nodeProps["description"]; ok {
			if val.(string) != "" {
				// Check if the description has a url, it'll be of type this [url:http\://example.com], but it can have more text before or after this
				// So we need to extract the url from this
				// First we need to find the index of the url
				startIndex := strings.Index(val.(string), "[url:")
				if startIndex != -1 {
					// Now we need to find the index of the closing bracket
					endIndex := strings.Index(val.(string), "]")
					if endIndex != -1 {
						// Now we need to extract the url from the description
						url := val.(string)[startIndex+5 : endIndex]
						url = strings.ReplaceAll(url, "\\", "")
						//now check for the host in this url, that'll be our source
						return val1.(string), url
					}
				}
			}
		}
		return val1.(string), ""
	}

	switch label {
	case "Gene":
		return "GO", "http://geneontology.org/"
	case "Disease":
		return "Disease Ontology", "http://disease-ontology.org/"
	case "Drug":
		return "DrugBank", "https://www.drugbank.ca/"
	case "Pathway":
		return "Reactome", "https://reactome.org/"
	case "Protein":
		return "UniProt", "https://www.uniprot.org/uniprotkb/" + nodeProps["id"].(string)
	case "Transcript":
		return "UniProt", "https://www.uniprot.org/uniprotkb/" + nodeProps["id"].(string)
	case "Compound":
		return "PubChem", "https://pubchem.ncbi.nlm.nih.gov/"
	case "Anatomy":
		return "Uberon", "http://uberon.github.io/"
	case "Cell":
		return "GO", "http://www.obofoundry.org/ontology/cl.html"
	case "Biological Process":
		return "GO", "http://geneontology.org/"
	case "Molecular Function":
		return "GO", "http://geneontology.org/"
	case "Cellular Component":
		return "GO", "http://geneontology.org/"
	case "Phenotype":
		return "HPO", "https://hpo.jax.org/"
	case "Publication":
		return "PubMed", "https://pubmed.ncbi.nlm.nih.gov/"
	}
	return "", ""
	// // Now check for description with any url
	// if val, ok := nodeProps["description"]; ok {
	// 	if val.(string) != "" {
	// 		// Check if the description has a url, it'll be of type this [url:http\://example.com], but it can have more text before or after this
	// 		// So we need to extract the url from this
	// 		// First we need to find the index of the url
	// 		startIndex := strings.Index(val.(string), "[url:")
	// 		if startIndex != -1 {
	// 			// Now we need to find the index of the closing bracket
	// 			endIndex := strings.Index(val.(string), "]")
	// 			if endIndex != -1 {
	// 				// Now we need to extract the url from the description
	// 				url := val.(string)[startIndex+5 : endIndex]
	// 				//now check for the host in this url, that'll be our source
	// 				if strings.Contains(url, "http") {
	// 					temp := strings.Split(url, "/")[2]
	// 					temp = strings.ReplaceAll(temp, "www.", "")
	// 					temp = strings.Split(temp, ".")[0]
	// 					return temp, url
	// 				}
	// 			}
	// 		}
	// 	}
	// }
}
