package models

type Node struct {
	ID         string                 `json:"id"`
	Properties map[string]interface{} `json:"properties"`
}

type Relationship struct {
	ID         string                 `json:"id"`
	Properties map[string]interface{} `json:"properties"`
	Source     interface{}            `json:"source"`
	Target     interface{}            `json:"target"`
}

// Request schema

type GetNodesRequest struct {
	Limit int    `json:"limit"`
	Label string `json:"label"`
}

type GetEdgesRequest struct {
	Limit int `json:"limit"`
}
