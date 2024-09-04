package ws

import (
	"encoding/json"
	"log"

	"chemplusx.com/medkg-api/models"
	"github.com/gorilla/websocket"
)

func HandleMessage(conn *websocket.Conn, msg models.Message) {
	switch msg.Type {
	case "identify":
		handleIdentify(conn, msg)
	case "response":
		handleResponse(conn, msg)
	default:
		log.Printf("Unknown message type: %s", msg.Type)
	}
}

func handleIdentify(conn *websocket.Conn, msg models.Message) {
	var identifyMsg models.IdentifyMessage
	err := json.Unmarshal(msg.Data, &identifyMsg)
	if err != nil {
		log.Printf("Error unmarshalling identify message: %v", err)
		return
	}

	log.Printf("Client identified: %s with properties: %v", identifyMsg.ClientID, identifyMsg.Properties)

	// You can store client identity and properties in ConnectionManager or elsewhere

	response := models.Message{
		Type: "identify_ack",
		Data: []byte(`{"status":"success"}`),
	}
	sendMessage(conn, response)
}

func handleResponse(conn *websocket.Conn, msg models.Message) {
	var responseMsg models.ResponseMessage
	err := json.Unmarshal(msg.Data, &responseMsg)
	if err != nil {
		log.Printf("Error unmarshalling response message: %v", err)
		return
	}

	log.Printf("Received response for request_id %s: %s", responseMsg.RequestID, responseMsg.Payload)

	// Handle the response, possibly mapping it back to the original request

	response := models.Message{
		Type: "response_ack",
		Data: []byte(`{"status":"received"}`),
	}
	sendMessage(conn, response)
}

func sendMessage(conn *websocket.Conn, msg models.Message) {
	message, err := json.Marshal(msg)
	if err != nil {
		log.Printf("Error marshalling message: %v", err)
		return
	}

	err = conn.WriteMessage(websocket.TextMessage, message)
	if err != nil {
		log.Printf("Error sending message: %v", err)
	}
}
