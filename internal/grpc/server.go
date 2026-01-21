package grpc

import (
	"log"
	"net"

	"google.golang.org/grpc"
)

// Server wraps the gRPC server
type Server struct {
	grpcServer *grpc.Server
	port       string
}

// NewServer creates a new gRPC server instance
func NewServer(port string) *Server {
	return &Server{
		grpcServer: grpc.NewServer(),
		port:       port,
	}
}

// Start starts the gRPC server
func (s *Server) Start() error {
	lis, err := net.Listen("tcp", ":"+s.port)
	if err != nil {
		return err
	}

	log.Printf("gRPC server listening on port %s", s.port)
	return s.grpcServer.Serve(lis)
}

// Stop gracefully stops the gRPC server
func (s *Server) Stop() {
	s.grpcServer.GracefulStop()
}

// RegisterInternalService registers the InternalService with the gRPC server
func (s *Server) RegisterInternalService() {
	RegisterInternalServiceServer(s.grpcServer, &internalServiceServer{})
}
