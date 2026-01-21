package grpc

import (
	"context"

	"github.com/process-failed-successfully/horcrux/internal/grpc"
)

type InternalServiceServer struct {
	grpc.UnimplementedInternalServiceServer
}

func (s *InternalServiceServer) Echo(ctx context.Context, req *grpc.EchoRequest) (*grpc.EchoResponse, error) {
	return &grpc.EchoResponse{
		Message: req.Message,
	}, nil
}
