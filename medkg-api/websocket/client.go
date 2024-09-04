//go:build client
// +build client

package main

import (
	"log"

	"github.com/gorilla/websocket"
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
	ws, err := Connect("ws://localhost:8080/ws")
	if err != nil {
		log.Fatalf("Failed to connect to WebSocket server: %v", err)
	}
	defer ws.Close()

	// Start listening for incoming messages
	go Listen(ws)

	// Send a message to the server
	message := []byte("Hello, Server!")
	err = SendMessage(ws, message)
	if err != nil {
		log.Fatalf("Failed to send message: %v", err)
	}

	// Block the main thread to keep the client running
	select {}
}
