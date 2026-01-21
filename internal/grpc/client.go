package grpc

import (
	"context"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// Client is a gRPC client for testing
type Client struct {
	conn   *grpc.ClientConn
	client InternalServiceClient
}

// NewClient creates a new gRPC client
func NewClient(addr string) (*Client, error) {
	conn, err := grpc.Dial(addr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithTimeout(5*time.Second),
		grpc.WithBlock(),
	)
	if err != nil {
		return nil, err
	}
	return &Client{
		conn:   conn,
		client: NewInternalServiceClient(conn),
	}, nil
}

// Echo sends an echo request to the server
func (c *Client) Echo(message string) (*EchoResponse, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return c.client.Echo(ctx, &EchoRequest{
		Message: message,
	})
}

// Close closes the client connection
func (c *Client) Close() error {
	return c.conn.Close()
}
