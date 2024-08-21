package controllers

// func GetOpenAPISpec() (*openapi3.T, error) {
// 	spec, err := openapi3.NewLoader().LoadFromFile("api/openapi.yaml")
// 	if err != nil {
// 		return nil, err
// 	}
// 	return spec, nil
// }

// func GetNodesHandler(client neo4j.DriverWithContext, request models.GetNodesRequest) gin.HandlerFunc {
// 	return func(c *gin.Context) {

// 		nodes, err := ni.GetNodes(client)
// 		if err != nil {
// 			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
// 			return
// 		}
// 		c.JSON(http.StatusOK, nodes)
// 	}
// }

// func CreateNodeHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
// 	return func(c *gin.Context) {
// 		label := c.Param("label")
// 		var node neo4j.Node
// 		if err := c.BindJSON(&node); err != nil {
// 			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
// 			return
// 		}

// 		createdNode, err := ni.CreateNode(client, label, node.GetProperties())
// 		if err != nil {
// 			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
// 			return
// 		}
// 		c.JSON(http.StatusCreated, createdNode)
// 	}
// }
