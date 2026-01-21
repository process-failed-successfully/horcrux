package main

import (
	"log"

	"github.com/process-failed-successfully/horcrux/internal/grpc"
)

func main() {
	server := grpc.NewServer("50051")
	grpc.RegisterInternalServiceServer(server.grpcServer, &grpc.InternalServiceServer{})

	if err := server.Start(); err != nil {
		log.Fatalf("Failed to start gRPC server: %v", err)
	}
}
