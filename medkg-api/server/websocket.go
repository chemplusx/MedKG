package server

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"

	"chemplusx.com/medkg-api/models"
	wss "chemplusx.com/medkg-api/ws"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		// Allow all connections by default
		return true
	},
}

// ConnectionManager holds active WebSocket connections and a mutex for thread-safe operations
type ConnectionManager struct {
	connections map[*websocket.Conn]bool
	mu          sync.Mutex
}

// NewConnectionManager initializes a new ConnectionManager
func NewConnectionManager() *ConnectionManager {
	return &ConnectionManager{
		connections: make(map[*websocket.Conn]bool),
	}
}

// AddConnection adds a new WebSocket connection to the manager
func (cm *ConnectionManager) AddConnection(conn *websocket.Conn) {
	cm.mu.Lock()
	cm.connections[conn] = true
	cm.mu.Unlock()
}

// RemoveConnection removes a WebSocket connection from the manager
func (cm *ConnectionManager) RemoveConnection(conn *websocket.Conn) {
	cm.mu.Lock()
	if _, ok := cm.connections[conn]; ok {
		delete(cm.connections, conn)
	}
	cm.mu.Unlock()
}

// Broadcast sends a message to all active WebSocket connections
func (cm *ConnectionManager) Broadcast(message []byte) {
	cm.mu.Lock()
	defer cm.mu.Unlock()
	for conn := range cm.connections {
		if err := conn.WriteMessage(websocket.TextMessage, message); err != nil {
			log.Printf("Error broadcasting message: %v", err)
			cm.RemoveConnection(conn)
			conn.Close()
		}
	}
}

// SendMessage sends a message to a specific WebSocket connection
func (cm *ConnectionManager) SendMessage(conn *websocket.Conn, message []byte) error {
	cm.mu.Lock()
	defer cm.mu.Unlock()
	if _, ok := cm.connections[conn]; ok {
		return conn.WriteMessage(websocket.TextMessage, message)
	}
	return nil
}

var cm = NewConnectionManager()

// HandleWebSocket handles incoming WebSocket connections
func HandleWebSocket(c *gin.Context) {
	ws, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("Error upgrading connection: %v", err)
		return
	}
	defer ws.Close()

	cm.AddConnection(ws)
	defer cm.RemoveConnection(ws)

	log.Println("New WebSocket connection established")

	for {
		_, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("Error reading message: %v", err)
			break
		}
		log.Printf("Received: %s", message)

		var msg models.Message
		err = json.Unmarshal(message, &msg)
		if err != nil {
			log.Printf("Error unmarshalling message: %v", err)
			continue
		}

		wss.HandleMessage(ws, msg)
	}
}
