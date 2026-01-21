package grpc

import (
	"context"
)

// internalServiceServer implements the InternalServiceServer interface
type internalServiceServer struct {
	UnimplementedInternalServiceServer
}

// Echo implements the Echo RPC method
func (s *internalServiceServer) Echo(ctx context.Context, req *EchoRequest) (*EchoResponse, error) {
	return &EchoResponse{
		Message: req.GetMessage(),
	}, nil
}
