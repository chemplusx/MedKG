package server

import (
	"log"

	"github.com/gin-gonic/gin"

	"chemplusx.com/medkg-api/controllers"
	"chemplusx.com/medkg-api/neo4j"
)

func InitRouter(r *gin.Engine) {
	// Init router
	// openapiSpec, err := controllers.GetOpenAPISpec()
	// if err != nil {
	// 	log.Fatalf("Failed to load OpenAPI spec: %v", err)
	// }

	// router, err := legacy.NewRouter(openapiSpec)
	// if err != nil {
	// 	log.Fatalf("Failed to create OpenAPI router: %v", err)
	// }

	// Serve the OpenAPI specification and Swagger UI
	r.StaticFile("/openapi.yaml", "./static/openapi.yaml")
	r.StaticFile("/", "./static/redoc.html")
	r.StaticFile("/api-docs", "./static/swagger-ui.html")
	r.StaticFile("/visualise", "./static/index.html")
	r.StaticFile("/nono", "./static/nono.html")
	r.StaticFile("/search", "./static/search.html")
	r.Static("/static", "./static/public")
	r.Static("/js", "./static/js")
	r.Static("/images", "./static/images")
	r.Static("/css", "./static/css")

	// Use the custom OpenAPI request validator middleware in Gin
	// r.Use(middlewares.OapiRequestValidatorWithGin(router))
	InitDataEndpoint(r)
}

/*
InitDataEndpoint initializes the data endpoint for the API server.

1: List node labels
2: List Edge (Relationship) collection
3: List label attributes
4: Get Nodes by label
	- limit
5: Search nodes
	- by search term, limit
*/

func InitDataEndpoint(r *gin.Engine) {
	client, err := neo4j.NewClient("bolt://localhost:7690", "neo4j", "password")
	if err != nil {
		log.Fatalf("Failed to create Neo4j client: %v", err)
	}

	r.GET("/ws", HandleWebSocket)

	// Define your API routes
	r.GET("/list/labels", controllers.GetLabelsHandler(client))
	r.GET("/list/relations", controllers.GetEdgesHandler(client))
	r.GET("/list/labels/:label", controllers.GetLabelDetailsHandler(client))
	r.POST("/nodes", controllers.GetNodesByRequestHandler(client))
	r.GET("/nodes/search", controllers.SearchNodesHandler(client))
	r.GET("/nodes/graph", controllers.GetNetworkGraphForIdHandler(client))
	r.GET("/search_in_graph", controllers.SearchNodesInGraphHandler(client))

}
