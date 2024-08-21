package controllers

import (
	"io/ioutil"
	"log"

	"github.com/getkin/kin-openapi/openapi3"
)

func GetOpenAPISpec() (*openapi3.T, error) {
	specBytes, err := ioutil.ReadFile("api/openapi.yaml")
	if err != nil {
		log.Fatalf("Failed to read OpenAPI spec: %v", err)
	}

	loader := openapi3.NewLoader()
	spec, err := loader.LoadFromData(specBytes)
	if err != nil {
		return nil, err
	}

	return spec, nil
}
