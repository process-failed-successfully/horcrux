package gossip

import (
	"context"
	"testing"
	"time"
)

func TestFailureDetector(t *testing.T) {
	t.Run("TestFailureDetectorCreation", func(t *testing.T) {
		swim := NewSWIM(context.Background(), Config{
			NodeID:        "test-node",
			BindAddr:      "127.0.0.1:8000",
			AdvertiseAddr: "127.0.0.1:8000",
		})
		fd := NewFailureDetector(swim)

		if fd == nil {
			t.Fatal("Failed to create failure detector")
		}
	})

	t.Run("TestFailureDetectorStartStop", func(t *testing.T) {
		swim := NewSWIM(context.Background(), Config{
			NodeID:        "test-node",
			BindAddr:      "127.0.0.1:8000",
			AdvertiseAddr: "127.0.0.1:8000",
			ProbeInterval: 100 * time.Millisecond,
		})
		fd := NewFailureDetector(swim)

		fd.Start()
		time.Sleep(200 * time.Millisecond)
		fd.Stop()

		// Test passes if no panic occurs
	})

	t.Run("TestFailureDetectorWithMultipleNodes", func(t *testing.T) {
		swim := NewSWIM(context.Background(), Config{
			NodeID:        "test-node",
			BindAddr:      "127.0.0.1:8000",
			AdvertiseAddr: "127.0.0.1:8000",
			ProbeInterval: 100 * time.Millisecond,
		})

		// Add some test nodes
		swim.AddNode(&Node{
			ID:    "node2",
			Addr:  "127.0.0.1:8001",
			State: NodeAlive,
		})

		swim.AddNode(&Node{
			ID:    "node3",
			Addr:  "127.0.0.1:8002",
			State: NodeAlive,
		})

		fd := NewFailureDetector(swim)
		fd.Start()
		time.Sleep(200 * time.Millisecond)
		fd.Stop()

		// Verify nodes are still there
		nodes := swim.GetNodes()
		if len(nodes) != 3 {
			t.Errorf("Expected 3 nodes, got %d", len(nodes))
		}
	})
}
