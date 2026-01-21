package gossip

import (
	"testing"
	"time"
)

func TestFailureDetectorStart(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)
	if err := swim.Start(); err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}
	defer swim.Stop()

	// Wait a bit for failure detector to start
	time.Sleep(100 * time.Millisecond)

	// Check that failure detector is running
	if swim.failureDetector == nil {
		t.Fatal("Failure detector not initialized")
	}
}

func TestFailureDetectorNodeFailure(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)
	if err := swim.Start(); err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}
	defer swim.Stop()

	// Add a test node
	testNode := &Node{
		ID:      "node2",
		Address: "127.0.0.1:8001",
		State:   NodeAlive,
	}
	swim.AddNode(testNode)

	// Wait for failure detection to potentially mark the node as failed
	// Since we're using random failures, we'll wait a bit
	time.Sleep(5 * time.Second)

	// Check if the node was marked as failed or suspected
	node, exists := swim.GetNode("node2")
	if !exists {
		t.Fatal("Test node not found")
	}

	// The node should either be alive (if pings succeeded) or failed (if pings failed)
	if node.State != NodeAlive && node.State != NodeFailed {
		t.Errorf("Unexpected node state: %v", node.State)
	}
}

func TestFailureDetectorMultipleNodes(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)
	if err := swim.Start(); err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}
	defer swim.Stop()

	// Add multiple test nodes
	for i := 2; i <= 5; i++ {
		node := &Node{
			ID:      fmt.Sprintf("node%d", i),
			Address: fmt.Sprintf("127.0.0.1:800%d", i),
			State:   NodeAlive,
		}
		swim.AddNode(node)
	}

	// Wait for failure detection
	time.Sleep(3 * time.Second)

	// Check that all nodes are being monitored
	nodes := swim.GetNodes()
	if len(nodes) != 5 { // 1 self + 4 added
		t.Errorf("Expected 5 nodes, got %d", len(nodes))
	}
}
