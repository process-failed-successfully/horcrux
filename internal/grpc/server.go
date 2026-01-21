package grpc

import (
	"context"
	"log"
	"net"

	"google.golang.org/grpc"
)

type Server struct {
	grpcServer *grpc.Server
	port       string
}

func NewServer(port string) *Server {
	return &Server{
		grpcServer: grpc.NewServer(),
		port:       port,
	}
}

func (s *Server) Start() error {
	lis, err := net.Listen("tcp", ":"+s.port)
	if err != nil {
		return err
	}

	log.Printf("gRPC server listening on port %s", s.port)
	return s.grpcServer.Serve(lis)
}

func (s *Server) Stop() {
	s.grpcServer.GracefulStop()
}
