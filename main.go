package main

import (
    "log"
    "net/http"
    "github.com/gin-gonic/gin"
    "github.com/process-failed-successfully/horcrux/internal/coordinator"
    "github.com/process-failed-successfully/horcrux/internal/peer"
    "github.com/process-failed-successfully/horcrux/internal/gossip"
)

func main() {
    // Initialize Gin router
    r := gin.Default()

    // Initialize Coordinator
    coord := coordinator.NewCoordinator()
    coord.RegisterRoutes(r)

    // Initialize Peer
    p := peer.NewPeer()
    p.RegisterRoutes(r)

    // Initialize Gossip
    g := gossip.NewGossip()
    g.RegisterRoutes(r)

    // Start server
    log.Println("Starting horcrux-node service on :8080")
    if err := http.ListenAndServe(":8080", r); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}
