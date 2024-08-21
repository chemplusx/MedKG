package middlewares

import (
	"net/http"

	"github.com/getkin/kin-openapi/openapi3filter"
	"github.com/getkin/kin-openapi/routers"
	"github.com/gin-gonic/gin"
)

func OapiRequestValidatorWithGin(router routers.Router) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Find the route
		route, pathParams, err := router.FindRoute(c.Request)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid path or method"})
			c.Abort()
			return
		}

		// Create the request validation input
		requestValidationInput := &openapi3filter.RequestValidationInput{
			Request:    c.Request,
			PathParams: pathParams,
			Route:      route,
		}

		// Validate the request against the OpenAPI spec
		if err := openapi3filter.ValidateRequest(c.Request.Context(), requestValidationInput); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			c.Abort()
			return
		}

		// Continue to the next handler if validation passes
		c.Next()
	}
}
