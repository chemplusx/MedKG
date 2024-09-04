package models

import "encoding/json"

type Message struct {
	Type      string          `json:"type"`
	RequestID string          `json:"request_id,omitempty"`
	Data      json.RawMessage `json:"data,omitempty"`
}

type IdentifyMessage struct {
	ClientID   string            `json:"client_id"`
	Properties map[string]string `json:"properties"`
}

type ResponseMessage struct {
	RequestID string `json:"request_id"`
	Payload   string `json:"payload"`
}

type RequestMessage struct {
	RequestID string `json:"request_id"`
	Query     string `json:"query"`
}
