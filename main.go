package main

import (
	"log"

	"github.com/process-failed-successfully/horcrux/internal/grpc"
)

func main() {
	server := grpc.NewServer("50051")
	server.RegisterInternalService()

	if err := server.Start(); err != nil {
		log.Fatalf("Failed to start gRPC server: %v", err)
	}
}
