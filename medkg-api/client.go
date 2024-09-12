//go:build client
// +build client

package main

import (
	"encoding/json"
	"log"
	"net/url"
	"os"
	"os/signal"
	"strconv"
	"time"

	"chemplusx.com/medkg-api/models"
	"chemplusx.com/medkg-api/neo4j"
	"github.com/gorilla/websocket"
	n4 "github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// Connect establishes a connection to the WebSocket server
func Connect(url string) (*websocket.Conn, error) {
	ws, _, err := websocket.DefaultDialer.Dial(url, nil)
	if err != nil {
		return nil, err
	}
	log.Printf("Connected to %s", url)
	return ws, nil
}

// SendMessage sends a message to the WebSocket server
func SendMessage(ws *websocket.Conn, message []byte) error {
	err := ws.WriteMessage(websocket.TextMessage, message)
	if err != nil {
		return err
	}
	log.Printf("Sent: %s", message)
	return nil
}

// Listen listens for incoming messages from the WebSocket server
func Listen(ws *websocket.Conn) {
	for {
		_, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("Error reading message: %v", err)
			break
		}
		log.Printf("Received: %s", message)
	}
}

func main() {
	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	u := url.URL{Scheme: "ws", Host: "13.233.109.233:8080", Path: "/ws"}
	log.Printf("Connecting to %s", u.String())

	conn, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		log.Fatal("Error connecting to WebSocket server:", err)
	}
	defer conn.Close()

	done := make(chan struct{})
	client, err := neo4j.NewClient("bolt://localhost:7687", "neo4j", "password")
	if err != nil {
		log.Fatalf("Failed to create Neo4j client: %v", err)
	}
	go func() {
		defer close(done)
		for {
			_, message, err := conn.ReadMessage()
			if err != nil {
				log.Println("Error reading message:", err)
				return
			}

			log.Printf("Received: %s", message)

			var msg models.Message
			err = json.Unmarshal(message, &msg)
			if err != nil {
				log.Printf("Error unmarshalling message: %v", err)
				continue
			}

			handleServerRequest(conn, msg, client)
		}
	}()

	// Send an identify message
	identifyMsg := models.IdentifyMessage{
		ClientID: "client123",
		Properties: map[string]string{
			"version":  "1.0.0",
			"platform": "golang",
		},
	}
	sendMessage(conn, "identify", "", identifyMsg)

	// Simulate a delay before sending a response message
	// time.Sleep(2 * time.Second)

	// // Send a response message
	// responseMsg := models.ResponseMessage{
	// 	RequestID: "req123",
	// 	Payload:   "Here is the requested data",
	// }
	// sendMessage(conn, "response", "req123", responseMsg)

	for {
		select {
		case <-done:
			return
		case <-interrupt:
			log.Println("Interrupt received, closing connection")
			err := conn.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
			if err != nil {
				log.Println("Error during closing handshake:", err)
				return
			}
			select {
			case <-done:
			case <-time.After(time.Second):
			}
			return
		}
	}
}

func handleServerRequest(conn *websocket.Conn, msg models.Message, client n4.DriverWithContext) {
	switch msg.Type {
	case "getLabels":
		respData, err := neo4j.GetLabels(client)
		if err != nil {
			log.Printf("Error getting labels: %v", err)
			sendMessage(conn, "error", msg.RequestID, err.Error())
			return
		}
		sendMessage(conn, "response", msg.RequestID, respData)
	case "getEdges":
		respData, err := neo4j.GetEdges(client)
		if err != nil {
			log.Printf("Error getting edges: %v", err)
			sendMessage(conn, "error", msg.RequestID, err.Error())
			return
		}
		sendMessage(conn, "response", msg.RequestID, respData)
	case "getLabelDetails":
		var requestMsg map[string]interface{}
		err := json.Unmarshal(msg.Data, &requestMsg)
		if err != nil {
			log.Printf("Error unmarshalling request message: %v", err)
			return
		}
		respData, err := neo4j.GetLabelDetails(client, requestMsg["label"].(string))
		if err != nil {
			log.Printf("Error getting label details: %v", err)
			sendMessage(conn, "error", msg.RequestID, err.Error())
			return
		}

		sendMessage(conn, "response", msg.RequestID, respData)
	case "searchNodes":
		var requestMsg map[string]interface{}
		err := json.Unmarshal(msg.Data, &requestMsg)
		if err != nil {
			log.Printf("Error unmarshalling request message: %v", err)
			return
		}
		limit, _ := requestMsg["limit"].(float64)
		respData, err := neo4j.SearchNodes(client, requestMsg["term"].(string), strconv.Itoa(int(limit)))
		if err != nil {
			log.Printf("Error searching nodes: %v", err)
			sendMessage(conn, "error", msg.RequestID, err.Error())
			return
		}
		sendMessage(conn, "response", msg.RequestID, respData)

		// Simulate processing the request and generating a response
		// responsePayload := "Processed query: " + msg

		// // Create a response message
		// responseMsg := models.Message{
		// 	Type:      "response",
		// 	RequestID: msg.RequestID,
		// 	Data:   responsePayload,
		// }

		// Send the response back to the server
		// sendMessage(conn, "response", requestMsg.RequestID, responseMsg)
	case "identify_ack":
		log.Println("Server acknowledged client identification")
	case "response_ack":
		log.Println("Server acknowledged response")
	default:
		log.Printf("Unknown message type: %s", msg.Type)
	}
}

func sendMessage(conn *websocket.Conn, messageType, requestID string, data interface{}) {
	msgData, err := json.Marshal(data)
	if err != nil {
		log.Printf("Error marshalling %s message: %v", messageType, err)
		return
	}

	message := models.Message{
		Type:      messageType,
		RequestID: requestID,
		Data:      msgData,
	}

	msgJSON, err := json.Marshal(message)
	if err != nil {
		log.Printf("Error marshalling message: %v", err)
		return
	}

	err = conn.WriteMessage(websocket.TextMessage, msgJSON)
	if err != nil {
		log.Printf("Error sending %s message: %v", messageType, err)
	}
}
