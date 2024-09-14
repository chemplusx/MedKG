package controllers

import (
	"log"
	"net/http"

	"chemplusx.com/medkg-api/models"
	ni "chemplusx.com/medkg-api/neo4j"

	"github.com/gin-gonic/gin"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func GetLabelsHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		labels, err := ni.GetLabels(client)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, labels)
	}
}

func GetEdgesHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		edges, err := ni.GetEdges(client)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, edges)
	}
}

func GetLabelDetailsHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		label := c.Param("label")
		details, err := ni.GetLabelDetails(client, label)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, details)
	}
}

func GetNodesByRequestHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		var request models.GetNodesRequest
		if err := c.BindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		nodes, err := ni.GetNodesByRequest(client, request)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		response := map[string]interface{}{
			"nodes": nodes,
		}
		c.JSON(http.StatusOK, response)
	}
}

func SearchNodesHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		log.Println("SearchNodesHandler")
		term := c.Query("term")
		limit := c.DefaultQuery("limit", "10")
		nodes, err := ni.SearchNodes(client, term, limit)
		if err != nil {
			log.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, nodes)
	}
}

func SearchNodesInGraphHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		log.Println("SearchNodesInGraphHandler")
		term := c.Query("term")
		limit := c.DefaultQuery("limit", "10")
		file := c.DefaultQuery("file", "graph.json")
		nodes, err := ni.SearchNodesInGraph(client, term, limit, file)
		if err != nil {
			log.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, nodes)
	}
}

func GetNetworkGraphForIdHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		id := c.Query("id")
		name := c.Query("name")
		typeN := c.Query("type")
		limit := c.DefaultQuery("limit", "10")
		neighbour := c.DefaultQuery("neighbour", "")
		// nodes, relationships, err := ni.GetNetworkGraphForId(client, id, name, typeN, limit, neighbour)
		nodes, relationships, err := ni.GetNetworkGraphForIdAndDepth(client, id, name, typeN, limit, neighbour, 2)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		response := map[string]interface{}{
			"nodes": nodes,
			"edges": relationships,
		}
		c.JSON(http.StatusOK, response)
	}
}

func GlobalSearchHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the post request body

		var reqBody map[string]interface{}

		if err := c.ShouldBindJSON(&reqBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		term, ok := reqBody["searchTerm"].(string)

		if !ok {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		nodes, err := ni.SearchNodesInGraph(client, term, "25", "")
		if err != nil {
			log.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, nodes)
	}
}

func InteractionSearchHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the post request body

		reqBody := models.InteractionSearchRequest{}
		if err := c.BindJSON(&reqBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		nodes, err := ni.SearchForInteraction(client, reqBody)
		if err != nil {
			log.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, nodes)
	}
}

func PathSearchHandler(client neo4j.DriverWithContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the post request body

		reqBody := models.PathSearchRequest{}
		if err := c.BindJSON(&reqBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		nodes, err := ni.SearchForPath(client, reqBody)
		if err != nil {
			log.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, nodes)
	}
}
