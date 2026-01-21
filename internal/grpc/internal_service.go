package grpc

import (
	"context"
)

// InternalServiceServer implements the InternalService service
type InternalServiceServer struct {
	UnimplementedInternalServiceServer
}

// Echo implements the Echo RPC method
func (s *InternalServiceServer) Echo(ctx context.Context, req *EchoRequest) (*EchoResponse, error) {
	return &EchoResponse{
		Message: req.GetMessage(),
	}, nil
}
