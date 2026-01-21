package grpc

import (
	"context"
	"net"
	"testing"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"
)

func TestEchoErrorHandling(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	lis := bufconn.Listen(1024 * 1024)
	s := grpc.NewServer()
	RegisterInternalServiceServer(s, &internalServiceServer{})
	go func() {
		if err := s.Serve(lis); err != nil {
			t.Errorf("Server failed: %v", err)
		}
	}()
	defer s.Stop()

	conn, err := grpc.DialContext(ctx, "bufnet",
		grpc.WithContextDialer(func(context.Context, string) (net.Conn, error) {
			return lis.Dial()
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		t.Fatalf("Failed to dial bufnet: %v", err)
	}
	defer conn.Close()

	client := NewInternalServiceClient(conn)

	// Test with empty message (should still work since proto3 doesn't enforce required)
	// Let's test the server doesn't crash with various inputs
	testCases := []struct {
		name     string
		message  string
		wantErr  bool
		wantCode codes.Code
	}{
		{
			name:     "empty message",
			message:  "",
			wantErr:  false, // proto3 treats empty as valid
			wantCode: codes.OK,
		},
		{
			name:     "normal message",
			message:  "test",
			wantErr:  false,
			wantCode: codes.OK,
		},
		{
			name:     "very long message",
			message:  string(make([]byte, 10000)),
			wantErr:  false,
			wantCode: codes.OK,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			response, err := client.Echo(ctx, &EchoRequest{
				Message: tc.message,
			})

			if tc.wantErr {
				if err == nil {
					t.Errorf("Expected error but got none")
				} else {
					st, ok := status.FromError(err)
					if !ok {
						t.Errorf("Expected gRPC status error, got: %v", err)
					}
					if st.Code() != tc.wantCode {
						t.Errorf("Expected error code %v, got %v", tc.wantCode, st.Code())
					}
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v", err)
				} else if response.Message != tc.message {
					t.Errorf("Expected message '%s', got '%s'", tc.message, response.Message)
				}
			}
		})
	}
}
