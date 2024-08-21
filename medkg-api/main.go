package main

import (
	"chemplusx.com/medkg-api/server"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	server.InitRouter(r)
	err := r.SetTrustedProxies([]string{"192.168.1.0/24", "10.0.0.0/16"})
	if err != nil {
		panic("Invalid trusted proxies")
	}

	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	// Load the OpenAPI specification

	// Create a router from the OpenAPI spec
	// router, err := legacy.NewRouter(openapiSpec)
	// if err != nil {
	// 	log.Fatalf("Failed to create OpenAPI router: %v", err)
	// }

	// // Serve the OpenAPI specification and Swagger UI
	// r.StaticFile("/openapi.yaml", "./api/openapi.yaml")
	// r.StaticFile("/", "./api/redoc.html")
	// r.StaticFile("/api-docs", "./api/swagger-ui.html")

	// // Use the custom OpenAPI request validator middleware in Gin
	// r.Use(middlewares.OapiRequestValidatorWithGin(router))

	// // Define your API routes
	// r.GET("/nodes", controllers.GetNodesHandler(client))
	// r.POST("/nodes/:label", controllers.CreateNodeHandler(client))

	// Start the server
	r.Run(":8080")
}
