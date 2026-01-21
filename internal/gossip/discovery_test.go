package gossip

import (
	"net/http"
	"testing"
	"time"
)

func TestDiscoveryServiceStartStop(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
			BindAddr:  "127.0.0.1:9000",
		},
	}

	swim := NewSWIM(config)
	if err := swim.Start(); err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}
	defer swim.Stop()

	// Wait a bit to ensure discovery service started
	time.Sleep(100 * time.Millisecond)
}

func TestDiscoveryServiceNodeDiscovery(t *testing.T) {
	// Create first node
	config1 := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
			BindAddr:  "127.0.0.1:9001",
		},
	}

	swim1 := NewSWIM(config1)
	if err := swim1.Start(); err != nil {
		t.Fatalf("Failed to start SWIM1: %v", err)
	}
	defer swim1.Stop()

	// Create second node that discovers from first
	config2 := Config{
		NodeID:      "node2",
		BindAddr:    "127.0.0.1:8001",
		AdvertiseAddr: "127.0.0.1:8001",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{"127.0.0.1:8000"},
			BindAddr:  "127.0.0.1:9002",
		},
	}

	swim2 := NewSWIM(config2)
	if err := swim2.Start(); err != nil {
		t.Fatalf("Failed to start SWIM2: %v", err)
	}
	defer swim2.Stop()

	// Wait for discovery
	time.Sleep(2 * time.Second)

	// Check that node2 discovered node1
	nodes := swim2.GetNodes()
	if len(nodes) < 2 {
		t.Errorf("Expected at least 2 nodes, got %d", len(nodes))
	}
}

func TestDiscoveryServiceHandleDiscovery(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
			BindAddr:  "127.0.0.1:9003",
		},
	}

	swim := NewSWIM(config)
	if err := swim.Start(); err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}
	defer swim.Stop()

	// Wait a bit to ensure discovery service started
	time.Sleep(100 * time.Millisecond)
}

func TestDiscoveryServiceHandleNodesRequest(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
			BindAddr:  "127.0.0.1:9004",
		},
	}

	swim := NewSWIM(config)
	if err := swim.Start(); err != nil {
		t.Fatalf("Failed to start SWIM: %v", err)
	}
	defer swim.Stop()

	// Wait a bit to ensure discovery service started
	time.Sleep(100 * time.Millisecond)

	// Try to get nodes from discovery endpoint
	resp, err := http.Get("http://127.0.0.1:9004/nodes")
	if err != nil {
		t.Fatalf("Failed to get nodes: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}
}
