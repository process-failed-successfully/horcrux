package grpc

import (
	"context"
)

type InternalServiceServer struct {
	UnimplementedInternalServiceServer
}

func (s *InternalServiceServer) Echo(ctx context.Context, req *EchoRequest) (*EchoResponse, error) {
	return &EchoResponse{
		Message: req.GetMessage(),
	}, nil
}
