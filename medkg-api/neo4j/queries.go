package neo4j

import (
	"context"
	"log"
	"strconv"

	"chemplusx.com/medkg-api/models"
	"github.com/google/uuid"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

var blacklistedLabels = []string{"Molecular_function", "Cellular_component", "Modification", "Clinical_variable", "Phenotype", "Experiment", "Experimental_factor", "Units", "Complex", "Food", "Known_variant", "Clinically_relevant_variant", "Publication", "GWAS_study", "User", "Project", "Subject", "Analytical_sample", "Timepoint"}

func GetLabels(driver neo4j.DriverWithContext) ([]string, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			records, err := tx.Run(ctx, "CALL db.labels()", nil)
			if err != nil {
				return nil, err
			}

			var labels []string
			for records.Next(ctx) {
				record := records.Record()
				labels = append(labels, record.Values[0].(string))
			}
			// Remove the blacklisted labels from the response
			for _, label := range blacklistedLabels {
				for i, l := range labels {
					if l == label {
						labels = append(labels[:i], labels[i+1:]...)
						break
					}
				}
			}
			return labels, records.Err()
		},
	)

	if err != nil {
		return nil, err
	}

	return result.([]string), nil
}

func GetEdges(driver neo4j.DriverWithContext) ([]string, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			records, err := tx.Run(ctx, "CALL db.relationshipTypes()", nil)
			if err != nil {
				return nil, err
			}

			var edges []string
			for records.Next(ctx) {
				record := records.Record()
				edges = append(edges, record.Values[0].(string))
			}
			return edges, records.Err()
		},
	)

	if err != nil {
		return nil, err
	}

	return result.([]string), nil
}

func GetLabelDetails(driver neo4j.DriverWithContext, label string) (interface{}, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			records, err := tx.Run(ctx, "MATCH (n:"+label+") WITH DISTINCT keys(n) AS props UNWIND props AS prop RETURN DISTINCT prop", nil)
			if err != nil {
				return nil, err
			}

			var details []string
			for records.Next(ctx) {
				record := records.Record()
				details = append(details, record.Values[0].(string))
			}

			var response map[string]interface{}
			response = make(map[string]interface{})
			response["label"] = label
			response["attributes"] = details
			return response, records.Err()
		},
	)

	if err != nil {
		return nil, err
	}

	return result, nil
}

func GetNodesByRequest(driver neo4j.DriverWithContext, request models.GetNodesRequest) ([]models.Node, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			records, err := tx.Run(ctx, "MATCH (n:"+request.Label+") RETURN n {.*, embedding: null, synonyms_str: null } AS node limit "+strconv.FormatInt(int64(request.Limit), 10), nil)
			if err != nil {
				return nil, err
			}

			var nodes []models.Node
			for records.Next(ctx) {
				record := records.Record()
				node := record.Values[0].(map[string]interface{})
				id, _ := uuid.NewRandom()
				nodes = append(nodes, models.Node{
					ID:         id.String(),
					Properties: node,
				})
			}
			return nodes, records.Err()
		},
	)

	if err != nil {
		return nil, err
	}

	return result.([]models.Node), nil
}

func SearchNodes(driver neo4j.DriverWithContext, term string, limit string) ([]models.Node, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			labels := "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"
			records, err := tx.Run(ctx, "CALL db.index.fulltext.queryNodes('allIndex', $term) YIELD node, score MATCH (node:"+labels+") RETURN elementId(node), labels(node), node {.*, embedding: null, synonyms_str: null, score: score } AS node LIMIT toInteger($limit)", map[string]interface{}{"term": term, "limit": limit})
			if err != nil {
				return nil, err
			}

			var nodes []models.Node
			for records.Next(ctx) {
				record := records.Record()
				id := record.Values[0].(string)
				types := record.Values[1].([]interface{})
				node := record.Values[2].(map[string]interface{})
				nme := "noname"
				if val, ok := node["name"]; ok && val != nil {
					nme = node["name"].(string)
				}
				nodes = append(nodes, models.Node{
					ID:         id,
					Label:      nme,
					Type:       types[0].(string),
					Score:      node["score"].(float64),
					Properties: node,
				})
			}
			return nodes, records.Err()
		},
	)

	if err != nil {
		return nil, err
	}

	return result.([]models.Node), nil
}

func SearchNodesInGraph(driver neo4j.DriverWithContext, term string, limit string, fileName string) ([]models.Node, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			labels := "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"
			records, err := tx.Run(ctx, "CALL db.index.fulltext.queryNodes('allIndex', $term) YIELD node, score MATCH (node:"+labels+") RETURN elementId(node), labels(node), node {id: node.id, name: node.name, description: node.description, function: node.specific_function, score: score } AS node LIMIT toInteger($limit)", map[string]interface{}{"term": term, "limit": limit})
			if err != nil {
				return nil, err
			}

			var nodes []models.Node
			for records.Next(ctx) {
				record := records.Record()
				id := record.Values[0].(string)
				types := record.Values[1].([]interface{})
				node := record.Values[2].(map[string]interface{})
				nme := "noname"
				if val, ok := node["name"]; ok && val != nil {
					nme = node["name"].(string)
				}

				// id := uuid.NewString()

				// if val, ok := node["id"]; ok && val != nil {
				// 	id = node["id"].(string)
				// }
				nodes = append(nodes, models.Node{
					ID:         id,
					Label:      nme,
					Type:       types[0].(string),
					Score:      node["score"].(float64),
					Properties: node,
				})
			}
			return nodes, records.Err()
		},
	)

	if err != nil {
		return nil, err
	}

	return result.([]models.Node), nil
}

func GetNetworkGraphForId(driver neo4j.DriverWithContext, id string, name string, typeN string, limit string, neighbour string) ([]map[string]interface{}, []map[string]interface{}, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			// First level Search

			labels := "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"

			if neighbour != "" {
				labels = neighbour
			}
			query := "MATCH (node:" + typeN + ")-[r*2]-(m:" + labels + ") where elementId(node)='" + id + "'"

			if name != "" {
				query += " and node.name='" + name + "'"
			}

			query += " RETURN node {.*, embedding: null, synonyms_str: null, internal_id: elementId(node)} AS node, r, m {.*, label: labels(m)[0], embedding:null, synonyms_str: null, internal_id: elementId(m)} as m limit " + limit

			log.Println(query)

			// query = "MATCH p=(node:Disease)-[r*2]-(m:Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample) where elementId(node)='4:4b9b25d3-4d29-42f7-a285-9ca6caddc8a1:1694884' and node.name='Parkinson disease' RETURN p limit 10"
			records, _ := tx.Run(ctx, query, nil)

			// Collect All data	for the first level
			var nodes []map[string]interface{}

			var relationships []map[string]interface{}

			exists := make(map[interface{}]bool)
			for records.Next(ctx) {
				record := records.Record()
				node := record.Values[0].(map[string]interface{})
				rel := record.Values[1].(neo4j.Relationship)
				relProps := rel.Props
				relProps["type"] = rel.Type
				relProps["id"] = rel.ElementId

				nme := "noname"
				if val, ok := node["name"]; ok && val != nil {
					nme = node["name"].(string)
				} else if val, ok := node["id"]; ok && val != nil {
					nme = node["id"].(string)
				}
				id1 := "noID"

				if idd, ok := node["id"]; ok {
					id1 = idd.(string)
				} else {
					id1 = node["internal_id"].(string)
				}

				ssource := models.Node{
					ID:          id1,
					Label:       nme,
					Properties:  node,
					DisplayName: nme,
					NodeType:    typeN,
				}

				if _, ok := exists[node["id"]]; !ok {
					nodes = append(nodes, map[string]interface{}{"data": ssource})
					exists[ssource.ID] = true
				}

				nnode := record.Values[2].(map[string]interface{})
				nodeLabel := nnode["label"].(string)

				nme = "noname"
				if val, ok := nnode["name"]; ok && val != nil {
					nme = nnode["name"].(string)
				} else if val, ok := node["id"]; ok && val != nil {
					nme = node["id"].(string)
				}

				id1 = "noID"

				if idd, ok := nnode["id"]; ok {
					id1 = idd.(string)
				} else {
					id1 = nnode["internal_id"].(string)
				}

				target := models.Node{
					ID:          id1,
					Label:       nme,
					Properties:  nnode,
					DisplayName: nme,
					NodeType:    nodeLabel,
				}

				if _, ok := exists[nnode["id"]]; !ok {
					nodes = append(nodes, map[string]interface{}{"data": target})
					exists[target.ID] = true
				}

				relationships = append(relationships, map[string]interface{}{
					"data": models.Relationship{
						ID:       rel.ElementId,
						Label:    relProps["type"].(string),
						Source:   ssource.ID,
						Target:   target.ID,
						EdgeType: rel.Type,
					},
				})
				// Second level Search, by fetching just next neighbors of this node. By node.id

				records1, err := tx.Run(ctx, "MATCH (node:"+nodeLabel+")-[r1]-(m:"+labels+") where elementId(node)=\""+nnode["internal_id"].(string)+"\" RETURN r1, m {.*, label: labels(m)[0], embedding: null, synonyms_str: null, internal_id: elementId(m)} as m limit toInteger($limit)", map[string]interface{}{"limit": 5})

				if err == nil {
					for records1.Next(ctx) {
						record1 := records1.Record()

						rel := record1.Values[0].(neo4j.Relationship)
						relProps := rel.Props
						relProps["type"] = rel.Type
						relProps["id"] = rel.ElementId
						node2 := record1.Values[1].(map[string]interface{})

						nme = "noname"
						if val, ok := node2["name"]; ok && val != nil {
							nme = node2["name"].(string)
						} else if val, ok := node["id"]; ok && val != nil {
							nme = node["id"].(string)
						}

						nodeLabel := nnode["label"].(string)

						id1 = "noID"

						if idd, ok := node2["id"]; ok {
							id1 = idd.(string)
						} else {
							id1 = node2["internal_id"].(string)
						}
						target2 := models.Node{
							ID:          id1,
							Label:       nme,
							Properties:  node2,
							DisplayName: nme,
							NodeType:    nodeLabel,
						}

						if _, ok := exists[node2["id"]]; !ok {
							nodes = append(nodes, map[string]interface{}{"data": target2})
							exists[target2.ID] = true
						}

						relationships = append(relationships, map[string]interface{}{
							"data": models.Relationship{
								ID:       rel.ElementId,
								Label:    relProps["type"].(string),
								Source:   target.ID,
								Target:   target2.ID,
								EdgeType: rel.Type,
							},
						})
					}
				}

			}

			return map[string]interface{}{
				"nodes":         nodes,
				"relationships": relationships,
			}, nil
		},
	)

	if err != nil {
		return nil, nil, err
	}

	return result.(map[string]interface{})["nodes"].([]map[string]interface{}), result.(map[string]interface{})["relationships"].([]map[string]interface{}), nil
}

func GetNetworkGraphForIdAndDepth(driver neo4j.DriverWithContext, id string, name string, typeN string, limit string, neighbour string, depth int) ([]map[string]models.Node, []map[string]interface{}, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	if depth <= 0 {
		depth = 1
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			// First level Search

			labels := "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"

			if neighbour != "" {
				labels = neighbour
			}
			query := "MATCH p=(node:" + typeN + ")-[r*" + strconv.Itoa(depth) + "]-(m:" + labels + ") where elementId(node)='" + id + "'"

			if name != "" {
				query += " and node.name='" + name + "'"
			}

			query += " RETURN p limit " + limit

			log.Println(query)

			// query = "MATCH p=(node:Disease)-[r*2]-(m:Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample) where elementId(node)='4:4b9b25d3-4d29-42f7-a285-9ca6caddc8a1:1694884' and node.name='Parkinson disease' RETURN p limit 10"
			records, _ := tx.Run(ctx, query, nil)

			// Collect All data	for the first level
			var totalNodes []map[string]models.Node
			var relationships []map[string]interface{}

			exists := make(map[interface{}]bool)
			for records.Next(ctx) {
				record := records.Record()
				path := record.Values[0].(neo4j.Path)
				nodes := path.Nodes
				rels := path.Relationships

				for _, node := range nodes {
					nme := "noname"
					if val, ok := node.Props["name"]; ok && val != nil {
						nme = node.Props["name"].(string)
					} else if val, ok := node.Props["id"]; ok && val != nil {
						nme = node.Props["id"].(string)
					}
					id1 := "noID"

					if idd, ok := node.Props["id"]; ok {
						id1 = idd.(string)
					} else {
						id1 = node.ElementId
					}

					source := models.Node{
						ID:          node.ElementId,
						NodeId:      id1,
						Label:       nme,
						Properties:  node.Props,
						DisplayName: nme,
						NodeType:    node.Labels[0],
					}

					if _, ok := exists[source.ID]; !ok {
						totalNodes = append(totalNodes, map[string]models.Node{"data": source})
						exists[source.ID] = true
					}
				}

				for _, rel := range rels {
					relationships = append(relationships, map[string]interface{}{
						"data": models.Relationship{
							ID:         rel.ElementId,
							Label:      rel.Type,
							Source:     rel.StartElementId,
							Target:     rel.EndElementId,
							EdgeType:   rel.Type,
							Properties: rel.Props,
						},
					})
				}

			}

			return map[string]interface{}{
				"nodes":         totalNodes,
				"relationships": relationships,
			}, nil
		},
	)

	if err != nil {
		return nil, nil, err
	}

	return result.(map[string]interface{})["nodes"].([]map[string]models.Node), result.(map[string]interface{})["relationships"].([]map[string]interface{}), nil
}

func SearchForInteraction(driver neo4j.DriverWithContext, request models.InteractionSearchRequest) (map[string]interface{}, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			// labels := "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"
			records, err := tx.Run(ctx, "MATCH p=(node)-[*..]-(dest:"+request.DestinationNodeType+") where elementId(node)=\""+request.SearchTerm+"\"  RETURN p LIMIT toInteger($limit)", map[string]interface{}{"term": request.SearchTerm, "limit": 25})
			if err != nil {
				return nil, err
			}

			var nodesMap map[string]models.Node = make(map[string]models.Node)
			var relMap map[string]models.Relationship = make(map[string]models.Relationship)
			var connectionmap map[string][]models.Relationship = make(map[string][]models.Relationship)
			var visited map[string]bool = make(map[string]bool)
			var e2ePath []string = make([]string, 0)

			for records.Next(ctx) {
				record := records.Record()
				path := record.Values[0].(neo4j.Path)
				nodes := path.Nodes
				rels := path.Relationships

				// Now create distinct path arrays from source node to all possible destination nodes of type request.DestinationNodeType
				// So if there are n nodes and r relationships
				// We need to calculate all possible paths from source (node.ElementId = request.SearchTerm) to destination(node.Node_Type = request.DestinationNodeType), this path can contain multiple nodes in between
				// We need to return all these paths

				for _, rel := range rels {
					if _, ok := relMap[rel.ElementId]; !ok {
						relMap[rel.ElementId] = models.Relationship{
							ID:         rel.ElementId,
							Label:      rel.Type,
							Source:     rel.StartElementId,
							Target:     rel.EndElementId,
							EdgeType:   rel.Type,
							Properties: rel.Props,
						}
					}

					if _, ok := connectionmap[rel.StartElementId]; !ok {
						connectionmap[rel.StartElementId] = []models.Relationship{}
					}

					connectionmap[rel.StartElementId] = append(connectionmap[rel.StartElementId], relMap[rel.ElementId])
				}

				for _, node := range nodes {
					nme := "noname"
					if val, ok := node.Props["name"]; ok && val != nil {
						nme = node.Props["name"].(string)
					} else if val, ok := node.Props["id"]; ok && val != nil {
						nme = node.Props["id"].(string)
					}
					id1 := "noID"

					if idd, ok := node.Props["id"]; ok {
						id1 = idd.(string)
					} else {
						id1 = node.ElementId
					}

					source := models.Node{
						ID:          node.ElementId,
						NodeId:      id1,
						Label:       nme,
						Properties:  node.Props,
						DisplayName: nme,
						NodeType:    node.Labels[0],
					}

					nodesMap[source.ID] = source
				}

				if _, ok := visited[request.SearchTerm]; !ok {
					visited[request.SearchTerm] = true
					totalPath := "||" + request.SearchTerm + "->"
					recurseAndBuildPath(&connectionmap, &nodesMap, request.SearchTerm, &visited, &request.DestinationNodeType, &totalPath, &e2ePath)
				}

				// for _, node := range nodes {
				// 	if _, ok := visited[node.ElementId]; !ok {
				// 		visited[node.ElementId] = true
				// 		totalPath := "||" + node.ElementId + "->"
				// 		recurseAndBuildPath(&connectionmap, &nodesMap, node.ElementId, &visited, &request.DestinationNodeType, &totalPath, &e2ePath)
				// 	}
				// 	// Now we need to find all possible paths from this node to the destination node
				// 	// We can do this by traversing the connectionmap
				// }

			}
			return map[string]interface{}{
				"nodes": nodesMap,
				"rels":  relMap,
				"paths": e2ePath,
			}, nil
		},
	)

	if err != nil {
		return nil, err
	}
	// map[string]models.Node, map[string]models.Relationship, []string
	return result.(map[string]interface{}), nil
}

func SearchForPath(driver neo4j.DriverWithContext, request models.PathSearchRequest) ([]models.Node, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			labels := "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"
			records, err := tx.Run(ctx, "MATCH p=shortestPath((source:"+labels+")-[*..5]-(target:"+labels+")) where elementId(source)=$sourceNodeID and elementId(target)=$targetNodeID RETURN p", map[string]interface{}{"sourceNodeID": request.SourceNodeID, "targetNodeID": request.TargetNodeID})
			if err != nil {
				return nil, err
			}

			var totalNodes []models.Node
			var relationships []map[string]interface{}
			for records.Next(ctx) {
				record := records.Record()
				path := record.Values[0].(neo4j.Path)
				nodes := path.Nodes
				rels := path.Relationships

				for _, node := range nodes {
					nme := "noname"
					if val, ok := node.Props["name"]; ok && val != nil {
						nme = node.Props["name"].(string)
					} else if val, ok := node.Props["id"]; ok && val != nil {
						nme = node.Props["id"].(string)
					}
					id1 := "noID"

					if idd, ok := node.Props["id"]; ok {
						id1 = idd.(string)
					} else {
						id1 = node.ElementId
					}

					source := models.Node{
						ID:          node.ElementId,
						NodeId:      id1,
						Label:       nme,
						Properties:  node.Props,
						DisplayName: nme,
						NodeType:    node.Labels[0],
					}

					totalNodes = append(totalNodes, source)
				}

				for _, rel := range rels {
					relationships = append(relationships, map[string]interface{}{
						"data": models.Relationship{
							ID:         rel.ElementId,
							Label:      rel.Type,
							Source:     rel.StartElementId,
							Target:     rel.EndElementId,
							EdgeType:   rel.Type,
							Properties: rel.Props,
						},
					})
				}

				// record := records.Record()
				// path := record.Values[0].(neo4j.Path)
				// nodes = append(nodes, models.Node{
				// 	ID:         path.,
				// 	Label:      path.Start.Labels[0],
				// 	Properties: path.Start.Props,
				// })
				// for _, node := range path.Nodes {
				// 	nodes = append(nodes, models.Node{
				// 		ID:         node.ElementId,
				// 		Label:      node.Labels[0],
				// 		Properties: node.Props,
				// 	})
				// }
				// nodes = append(nodes, models.Node{
				// 	ID:         path.EndElementId,
				// 	Label:      path.End.Labels[0],
				// 	Properties: path.End.Props,
				// })
			}
			return map[string]interface{}{
				"nodes":         totalNodes,
				"relationships": relationships,
			}, nil
		},
	)

	if err != nil {
		return nil, err
	}

	return result.([]models.Node), nil
}
