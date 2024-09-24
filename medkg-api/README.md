# MedKG App Server

MedKG App Server is a powerful and user-friendly application for interacting with and visualizing medical knowledge graphs stored in a Neo4j database. Built with Go, it provides a web interface and API for efficient data exploration and analysis.

## Features

- **Web Interface**: Access the application through a browser at `localhost:5000`
- **API Documentation**: Available at `/api-docs` and `/swagger` endpoints
- **Global Search**: Quickly find entities across the entire knowledge graph
- **Interaction Search**: Explore relationships between specific entities
- **Path Search**: Discover connections between different nodes in the graph
- **Network Graph Visualization**: Visualize data in an interactive network graph
- **Direct Database Interaction**: Perform operations directly on the underlying Neo4j database

## Prerequisites

Before you begin, ensure you have the following installed:
- Go (version 1.15 or later)
- Neo4j database (version 4.0 or later)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/chemplusx/MedKG.git
   cd MedKG/medkg-api
   ```

2. Install dependencies:
   ```
   go mod tidy
   ```

3. Configure the application:
   - Edit the configuration file (e.g., `config.yaml`) to set up your Neo4j database connection details and other settings.

## Usage

### Running the Server

You can run the server in two ways:

1. For development:
   ```
   go run main.go
   ```

2. For production:
   ```
   go build main.go
   ./main
   ```

Once the server is running, access the web interface by navigating to `http://localhost:5000` in your web browser.

### API Documentation

- Swagger UI: `http://localhost:5000/swagger`
- API Docs: `http://localhost:5000/api-docs`

## Web Interface Guide

1. **Global Search**: Use the search bar at the top to find entities across the entire knowledge graph.

2. **Interaction Search**: Navigate to the Interaction Search tab to explore relationships between specific entities.

3. **Path Search**: Use the Path Search feature to discover connections between different nodes in the graph.

4. **Network Graph**: 
   - Click on the Visualize button to see your search results in a network graph format.
   - Interact with nodes to expand relationships.
   - Zoom in/out and drag nodes to customize your view.

5. **Database Operations**: Authorized users can perform direct operations on the Neo4j database through the provided interface.

## API Usage

The MedKG App Server provides a RESTful API for programmatic access to the knowledge graph. Refer to the Swagger documentation (`/swagger`) for detailed endpoint information and example requests.

## Contributing

Contributions to the MedKG App Server are welcome! Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started.

## License

[Specify your license here]

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository or contact our support team at [your-support-email@example.com].

## Acknowledgements

- Neo4j team for their graph database technology
- Go community for the excellent networking and web service libraries

Thank you for using MedKG App Server! We hope this tool enhances your medical knowledge graph exploration and analysis.
