package neo4j

import (
	"context"
	"strconv"

	"chemplusx.com/medkg-api/models"
	"github.com/google/uuid"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j/dbtype"
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
			records, err := tx.Run(ctx, "CALL db.index.fulltext.queryNodes('nodeIndex', $term) YIELD node RETURN node {.*, embedding: null, synonyms_str: null } AS node LIMIT toInteger($limit)", map[string]interface{}{"term": term, "limit": limit})
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

func GetNetworkGraphForSearchTerm(driver neo4j.DriverWithContext, term string, limit string) ([]models.Node, []models.Relationship, error) {
	ctx := context.Background()

	err := driver.VerifyConnectivity(ctx)
	if err != nil {
		panic(err)
	}

	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)
	result, err := session.ExecuteRead(ctx,
		func(tx neo4j.ManagedTransaction) (interface{}, error) {
			records, err := tx.Run(ctx, "CALL db.index.fulltext.queryNodes('allIndex', $term) YIELD node RETURN node {.*, embedding: null, synonyms_str: null } AS node LIMIT toInteger($limit)", map[string]interface{}{"term": term, "limit": limit})
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

			records, err = tx.Run(ctx, "CALL db.index.fulltext.queryNodes('allIndex', $term) YIELD node MATCH (node)-[r]->(m) RETURN node {.*, embedding: null, synonyms_str: null } AS node, r, m limit 100", map[string]interface{}{"term": term})
			if err != nil {
				return nil, err
			}

			var relationships []models.Relationship
			for records.Next(ctx) {
				record := records.Record()
				node := record.Values[0].(map[string]interface{})
				rel := record.Values[1].(neo4j.Relationship)
				relProps := rel.Props
				relProps["type"] = rel.Type
				relProps["id"] = rel.ElementId
				m := record.Values[2].(dbtype.Node)
				relationships = append(relationships, models.Relationship{
					ID:         rel.ElementId,
					Properties: relProps,
					Source:     node,
					Target:     m,
				})
			}

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

	return result.(map[string]interface{})["nodes"].([]models.Node), result.(map[string]interface{})["relationships"].([]models.Relationship), nil
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
