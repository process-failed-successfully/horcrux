package gossip

import (
	"context"
	"testing"
	"time"
)

func TestFailureDetector(t *testing.T) {
	t.Run("TestFailureDetectorInitialization", func(t *testing.T) {
		config := Config{
			NodeID:            "node1",
			BindAddr:          ":8080",
			SeedNodes:         []string{"localhost:8081"},
			ProbeInterval:     1 * time.Second,
			SuspicionMultiplier: 3,
		}

		swim := NewSWIM(context.Background())
		swim.config = config

		fd := NewFailureDetector(swim)

		if fd == nil {
			t.Fatal("FailureDetector instance is nil")
		}
	})

	t.Run("TestFailureDetectorStartAndStop", func(t *testing.T) {
		config := Config{
			NodeID:            "node1",
			BindAddr:          ":8080",
			SeedNodes:         []string{"localhost:8081"},
			ProbeInterval:     1 * time.Second,
			SuspicionMultiplier: 3,
		}

		swim := NewSWIM(context.Background())
		swim.config = config

		fd := NewFailureDetector(swim)
		fd.Start()

		// Let it run for a short time
		time.Sleep(100 * time.Millisecond)

		// Stop the failure detector
		swim.Stop()
	})

	t.Run("TestNodeFailureDetection", func(t *testing.T) {
		config := Config{
			NodeID:            "node1",
			BindAddr:          ":8080",
			SeedNodes:         []string{"localhost:8081"},
			ProbeInterval:     1 * time.Second,
			SuspicionMultiplier: 3,
		}

		swim := NewSWIM(context.Background())
		swim.config = config

		// Add a node
		node := &Node{
			ID:    "node2",
			Addr:  "localhost:8081",
			State: NodeAlive,
		}
		swim.AddNode(node)

		fd := NewFailureDetector(swim)
		fd.Start()

		// Let it run for a short time
		time.Sleep(100 * time.Millisecond)

		// Check if the node is still alive
		retrievedNode := swim.GetNode("node2")
		if retrievedNode == nil {
			t.Fatal("Node not found")
		}

		// Stop the failure detector
		swim.Stop()
	})
}
