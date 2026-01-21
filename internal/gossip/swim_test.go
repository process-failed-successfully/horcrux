package gossip

import (
	"testing"
	"time"
)

func TestNewSWIM(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
	}

	swim := NewSWIM(config)

	if swim == nil {
		t.Fatal("NewSWIM returned nil")
	}

	if len(swim.GetNodes()) != 1 {
		t.Fatalf("Expected 1 node (self), got %d", len(swim.GetNodes()))
	}

	node := swim.GetNodes()[0]
	if node.ID != config.NodeID {
		t.Errorf("Expected node ID %s, got %s", config.NodeID, node.ID)
	}
}

func TestSWIMStartStop(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
	}

	swim := NewSWIM(config)

	// Test Start
	err := swim.Start()
	if err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}

	// Test Stop
	err = swim.Stop()
	if err != nil {
		t.Fatalf("Failed to stop SWIM: %v", err)
	}

	// Test double stop
	err = swim.Stop()
	if err != nil {
		t.Fatalf("Second stop should not fail: %v", err)
	}
}

func TestSWIMAddNode(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
	}

	swim := NewSWIM(config)

	// Add a new node
	newNode := &Node{
		ID:      "node2",
		Address: "127.0.0.1:8001",
		State:   NodeAlive,
	}

	swim.AddNode(newNode)

	nodes := swim.GetNodes()
	if len(nodes) != 2 {
		t.Fatalf("Expected 2 nodes, got %d", len(nodes))
	}

	// Verify the new node is in the list
	found := false
	for _, node := range nodes {
		if node.ID == "node2" {
			found = true
			break
		}
	}

	if !found {
		t.Fatal("Added node not found in node list")
	}
}

func TestSWIMDefaultConfig(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
	}

	swim := NewSWIM(config)

	// Verify default values are set
	if swim.config.GossipInterval != 1*time.Second {
		t.Errorf("Expected default GossipInterval of 1s, got %v", swim.config.GossipInterval)
	}

	if swim.config.ProbeInterval != 1*time.Second {
		t.Errorf("Expected default ProbeInterval of 1s, got %v", swim.config.ProbeInterval)
	}

	if swim.config.SuspicionMultiplier != 3 {
		t.Errorf("Expected default SuspicionMultiplier of 3, got %d", swim.config.SuspicionMultiplier)
	}
}
