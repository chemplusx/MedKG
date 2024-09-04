package main

import (
	"log"
	"net/http"

	"chemplusx.com/medkg-api/ws/server"
)

func main() {
	http.HandleFunc("/ws", server.HandleConnections)

	log.Println("Starting WebSocket server on :8090")
	err := http.ListenAndServe(":8090", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
