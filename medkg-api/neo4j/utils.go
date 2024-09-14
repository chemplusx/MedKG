package neo4j

import (
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
