package models

type Node struct {
	ID          string                 `json:"id"`
	Label       string                 `json:"label"`
	DisplayName string                 `json:"display_name"`
	NodeType    string                 `json:"Node_Type"`
	Type        string                 `json:"type"`
	Score       float64                `json:"score"`
	Properties  map[string]interface{} `json:"properties"`
}

type Relationship struct {
	ID         string                 `json:"id"`
	Label      string                 `json:"label"`
	Properties map[string]interface{} `json:"properties"`
	Source     interface{}            `json:"source"`
	Target     interface{}            `json:"target"`
	EdgeType   string                 `json:"Edge_Type"`
}

// Request schema

type GetNodesRequest struct {
	Limit int    `json:"limit"`
	Label string `json:"label"`
}

type GetEdgesRequest struct {
	Limit int `json:"limit"`
}
