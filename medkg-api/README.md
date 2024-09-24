# My API Server

This is a Go-based API server following the OpenAPI specification to interact with a Neo4j database.

## Setup

1. Install dependencies:

   ```bash
   go mod tidy
   ```

2. Start the server:

    ```bash
    go run cmd/main.go
    ```

3. The API will be available at `http://localhost:8080`


## Endpoints

* `GET /nodes`: Retreive all nodes
* `POST /nodes/{label}`: Create a new node with specific label


### Explanation

- **`api/openapi.yaml`**: Defines the OpenAPI spec for the API endpoints.
- **`cmd/main.go`**: The entry point of the application, initializing the server and routes.
- **`controllers/neo4j_controller.go`**: Contains the handlers for the API endpoints.
- **`models/neo4j_model.go`**: Defines the structure of the data models.
- **`neo4j/client.go`**: Establishes a connection with the Neo4j database.
- **`neo4j/queries.go`**: Handles database queries for retrieving and creating nodes.

