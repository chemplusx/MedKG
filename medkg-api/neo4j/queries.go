package neo4j

import (
	"context"
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
			records, err := tx.Run(ctx, "CALL db.index.fulltext.queryNodes('allIndex', $term) YIELD node, score MATCH (node:"+labels+") RETURN elementId(node), labels(node), node {id: node.id, name: node.name, score: score } AS node LIMIT toInteger($limit)", map[string]interface{}{"term": term, "limit": limit})
			if err != nil {
				return nil, err
			}

			var nodes []models.Node
			for records.Next(ctx) {
				record := records.Record()
				// id := record.Values[0].(string)
				types := record.Values[1].([]interface{})
				node := record.Values[2].(map[string]interface{})
				nme := "noname"
				if val, ok := node["name"]; ok && val != nil {
					nme = node["name"].(string)
				}

				id := uuid.NewString()

				if val, ok := node["id"]; ok && val != nil {
					id = node["id"].(string)
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

func GetNetworkGraphForId(driver neo4j.DriverWithContext, id string, name string, typeN string, limit string) ([]map[string]interface{}, []map[string]interface{}, error) {
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

			query := "MATCH (node:" + typeN + ")-[r]-(m:" + labels + ") where elementId(node)='" + id + "'"

			if name != "" {
				query += " and node.name='" + name + "'"
			}

			query += " RETURN node {.*, embedding: null, synonyms_str: null} AS node, r, m {.*, label: labels(m)[0], embedding:null, synonyms_str: null} as m limit " + limit

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

				ssource := models.Node{
					ID:          node["id"].(string),
					Label:       nme,
					Properties:  node,
					DisplayName: nme,
					NodeType:    typeN,
				}

				if _, ok := exists[node["id"]]; !ok {
					nodes = append(nodes, map[string]interface{}{"data": ssource})
					exists[node["id"]] = true
				}

				nnode := record.Values[2].(map[string]interface{})
				nodeLabel := nnode["label"].(string)

				nme = "noname"
				if val, ok := nnode["name"]; ok && val != nil {
					nme = nnode["name"].(string)
				} else if val, ok := node["id"]; ok && val != nil {
					nme = node["id"].(string)
				}

				target := models.Node{
					ID:          nnode["id"].(string),
					Label:       nme,
					Properties:  nnode,
					DisplayName: nme,
					NodeType:    nodeLabel,
				}

				if _, ok := exists[nnode["id"]]; !ok {
					nodes = append(nodes, map[string]interface{}{"data": target})
					exists[nnode["id"]] = true
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

				records1, err := tx.Run(ctx, "MATCH (node:"+nodeLabel+"{id:'"+nnode["id"].(string)+"'})-[r1]-(m:"+labels+") RETURN r1, m {.*, label: labels(m)[0], embedding: null, synonyms_str: null} as m limit toInteger($limit)", map[string]interface{}{"limit": 5})

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

						target2 := models.Node{
							ID:          node2["id"].(string),
							Label:       nme,
							Properties:  node2,
							DisplayName: nme,
							NodeType:    nodeLabel,
						}

						if _, ok := exists[node2["id"]]; !ok {
							nodes = append(nodes, map[string]interface{}{"data": target2})
							exists[node2["id"]] = true
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

			// if typeN == "" {
			// 	labels = "Disease|Tissue|Biological_process|Chromosome|Gene|Transcript|Protein|Amino_acid_sequence|Peptide|Modified_protein|Drug|Functional_region|Metabolite|Protein_structure|Pathway|Biological_sample"
			// } else {
			// 	labels = typeN
			// }
			// // records, err := tx.Run(ctx, "CALL db.index.fulltext.queryNodes('allIndex', $term) YIELD node, score MATCH (node:"+labels+")-[r1]->(n2)-[r2]->(n3)-[r3]->(m:"+labels+") RETURN node {.*, embedding: null, synonyms_str: null, score: score } AS node, r1, n2 {.*, embedding: null, synonyms_str: null } as n2, r2, n3 {.*, embedding: null, synonyms_str: null } as n3, r3, m {.*, embedding: null, synonyms_str: null } as m limit toInteger($limit)", map[string]interface{}{"term": term, "limit": limit})

			// records, err := tx.Run(ctx, "MATCH (node:"+labels+")-[r1]->(n2)-[r3]->(m) where node.id='"+id+"' and node.name='"+name+"' RETURN node {.*, embedding: null, synonyms_str: null} AS node, r1, n2 {.*, embedding: null, synonyms_str: null } as n2, r3, m {.*, embedding: null, synonyms_str: null } as m limit toInteger($limit)", map[string]interface{}{"limit": limit})

			// log.Println("MATCH (node:"+labels+")-[r1]->(n2)-[r3]->(m) where node.id='"+id+"' and node.name='"+name+"' RETURN node {.*, embedding: null, synonyms_str: null} AS node, r1, n2 {.*, embedding: null, synonyms_str: null } as n2, r3, m {.*, embedding: null, synonyms_str: null } as m limit toInteger($limit)", map[string]interface{}{"limit": limit})
			// if err != nil {
			// 	log.Println(err)
			// 	return nil, err
			// }

			// var nodes []map[string]interface{}

			// var relationships []map[string]interface{}
			// exists := make(map[interface{}]bool)
			// for records.Next(ctx) {
			// 	record := records.Record()
			// 	node := record.Values[0].(map[string]interface{})
			// 	rel := record.Values[1].(neo4j.Relationship)
			// 	relProps := rel.Props
			// 	relProps["type"] = rel.Type
			// 	relProps["id"] = rel.ElementId

			// 	// 1 id, _ := uuid.NewRandom()
			// 	nme := "noname"
			// 	if val, ok := node["name"]; ok && val != nil {
			// 		nme = node["name"].(string)
			// 	}
			// 	source := models.Node{
			// 		ID:    node["id"].(string),
			// 		Label: nme,
			// 		// Score:      node["score"].(float64),
			// 		Properties: node,
			// 	}

			// 	if _, ok := exists[node["id"]]; !ok {
			// 		nodes = append(nodes, map[string]interface{}{
			// 			"data": source})
			// 		exists[node["id"]] = true
			// 	}

			// 	// 2
			// 	node1 := record.Values[2].(map[string]interface{})
			// 	nme = "noname"
			// 	if val, ok := node1["name"]; ok && val != nil {
			// 		nme = node1["name"].(string)
			// 	}
			// 	target := models.Node{
			// 		ID:         node1["id"].(string),
			// 		Label:      nme,
			// 		Properties: node1,
			// 	}

			// 	if _, ok := exists[node1["id"]]; !ok {
			// 		nodes = append(nodes, map[string]interface{}{
			// 			"data": target})
			// 		exists[node1["id"]] = true
			// 	}

			// 	relationships = append(relationships, map[string]interface{}{
			// 		"data": models.Relationship{
			// 			ID:         rel.ElementId,
			// 			Label:      relProps["type"].(string),
			// 			Properties: relProps,
			// 			Source:     source.ID,
			// 			Target:     target.ID,
			// 		},
			// 	})

			// 	// source = target

			// 	// 3
			// 	// node = record.Values[4].(map[string]interface{})
			// 	// rel = record.Values[3].(neo4j.Relationship)
			// 	// relProps = rel.Props
			// 	// relProps["type"] = rel.Type
			// 	// relProps["id"] = rel.ElementId
			// 	// nme = "noname"
			// 	// if val, ok := node["name"]; ok && val != nil {
			// 	// 	nme = node["name"].(string)
			// 	// }
			// 	// target = models.Node{
			// 	// 	ID:         node["id"].(string),
			// 	// 	Label:      nme,
			// 	// 	Score:      node["score"].(float64),
			// 	// 	Properties: node,
			// 	// }

			// 	// if _, ok := exists[node["id"]]; !ok {
			// 	// 	nodes = append(nodes, map[string]interface{}{
			// 	// 		"data": source})
			// 	// 	exists[node["id"]] = true
			// 	// }

			// 	// relationships = append(relationships, map[string]interface{}{
			// 	// 	"data": models.Relationship{
			// 	// 		ID:         rel.ElementId,
			// 	// 		Label:      relProps["type"].(string),
			// 	// 		Properties: relProps,
			// 	// 		Source:     source.ID,
			// 	// 		Target:     target.ID,
			// 	// 	},
			// 	// })

			// 	// source = target

			// 	// id, _ = uuid.NewRandom()
			// 	m := record.Values[4].(map[string]interface{})
			// 	rel2 := record.Values[3].(neo4j.Relationship)
			// 	relProps2 := rel.Props
			// 	relProps2["type"] = rel.Type
			// 	relProps2["id"] = rel.ElementId
			// 	nme = "noname"
			// 	if val, ok := m["name"]; ok && val != nil {
			// 		nme = m["name"].(string)
			// 	}
			// 	target1 := models.Node{
			// 		ID:         m["id"].(string),
			// 		Label:      nme,
			// 		Properties: m,
			// 	}
			// 	if _, ok := exists[m["id"]]; !ok {
			// 		nodes = append(nodes, map[string]interface{}{
			// 			"data": target1})
			// 		exists[m["id"]] = true
			// 	}

			// 	relationships = append(relationships, map[string]interface{}{
			// 		"data": models.Relationship{
			// 			ID:         rel2.ElementId,
			// 			Label:      relProps2["type"].(string),
			// 			Properties: relProps2,
			// 			Source:     target.ID,
			// 			Target:     target1.ID,
			// 		},
			// 	})
			// }

			// return nodes, relationships, records.Err()
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

// (driver neo4j.DriverWithContext) ([]models.Node, error) {
// 	ctx := context.Background()

// 	err := driver.VerifyConnectivity(ctx)
// 	if err != nil {
// 		panic(err)
// 	}

// 	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
// 	defer session.Close(ctx)
// 	result, err := session.ExecuteRead(ctx,
// 		func(tx neo4j.ManagedTransaction) (interface{}, error) {
// 			records, err := tx.Run(ctx, "MATCH (n) RETURN n {.*, embedding: null, synonyms_str: null } AS node limit 10", nil)
// 			if err != nil {
// 				return nil, err
// 			}

// 			var nodes []models.Node
// 			for records.Next(ctx) {
// 				record := records.Record()
// 				node := record.Values[0].(map[string]interface{})
// 				id, _ := uuid.NewRandom()
// 				nodes = append(nodes, models.Node{
// 					ID:         id.String(),
// 					Properties: node,
// 				})
// 			}
// 			return nodes, records.Err()
// 		},
// 	)

// 	if err != nil {
// 		return nil, err
// 	}

// 	return result.([]models.Node), nil
// }

// func CreateNode(driver neo4j.DriverWithContext, label string, properties map[string]interface{}) (*models.Node, error) {
// 	ctx := context.Background()
// 	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
// 	defer session.Close(ctx)

// 	query := "CREATE (n:" + label + " $props) RETURN n"
// 	result, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (interface{}, error) {
// 		records, err := tx.Run(ctx, query, map[string]interface{}{"props": properties})
// 		if err != nil {
// 			return nil, err
// 		}

// 		if records.Next(ctx) {
// 			record := records.Record()
// 			node := record.Values[0].(neo4j.Node)
// 			return &models.Node{
// 				ID:         node.ElementId,
// 				Properties: node.Props,
// 			}, nil
// 		}

// 		return nil, records.Err()
// 	})

// 	if err != nil {
// 		return nil, err
// 	}

// 	return result.(*models.Node), nil
// }
