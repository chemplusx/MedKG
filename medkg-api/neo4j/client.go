package neo4j

import (
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func NewClient(uri, username, password string) (neo4j.DriverWithContext, error) {
	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
	if err != nil {
		return nil, err
	}
	return driver, nil
}
