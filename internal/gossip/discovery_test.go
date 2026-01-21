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
		},
	}

	swim := NewSWIM(config)
	discovery := NewDiscoveryService(swim, config.DiscoveryConfig)

	// Test Start
	err := discovery.Start()
	if err != nil {
		t.Fatalf("Failed to start discovery service: %v", err)
	}

	// Give server time to start
	time.Sleep(100 * time.Millisecond)

	// Test that server is responding
	resp, err := http.Get("http://localhost:8080/discover")
	if err != nil {
		t.Fatalf("Failed to connect to discovery server: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	// Test Stop
	err = discovery.Stop()
	if err != nil {
		t.Fatalf("Failed to stop discovery service: %v", err)
	}
}

func TestDiscoveryServiceNodeDiscovery(t *testing.T) {
	// Create first node
	config1 := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
			DiscoveryPort: 8081,
		},
	}

	swim1 := NewSWIM(config1)
	discovery1 := NewDiscoveryService(swim1, config1.DiscoveryConfig)

	// Create second node with first node as seed
	config2 := Config{
		NodeID:      "node2",
		BindAddr:    "127.0.0.1:8001",
		AdvertiseAddr: "127.0.0.1:8001",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{"127.0.0.1:8081"},
			DiscoveryPort: 8082,
		},
	}

	swim2 := NewSWIM(config2)
	discovery2 := NewDiscoveryService(swim2, config2.DiscoveryConfig)

	// Start both nodes
	if err := discovery1.Start(); err != nil {
		t.Fatalf("Failed to start discovery1: %v", err)
	}
	if err := discovery2.Start(); err != nil {
		t.Fatalf("Failed to start discovery2: %v", err)
	}

	// Give time for discovery
	time.Sleep(2 * time.Second)

	// Check that node2 discovered node1
	nodes2 := swim2.GetNodes()
	foundNode1 := false
	for _, node := range nodes2 {
		if node.ID == "node1" {
			foundNode1 = true
			break
		}
	}

	if !foundNode1 {
		t.Fatal("Node2 did not discover node1")
	}

	// Cleanup
	discovery1.Stop()
	discovery2.Stop()
}

func TestDiscoveryServiceHandleDiscovery(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)
	discovery := NewDiscoveryService(swim, config.DiscoveryConfig)

	// Start discovery service
	if err := discovery.Start(); err != nil {
		t.Fatalf("Failed to start discovery service: %v", err)
	}
	defer discovery.Stop()

	// Give server time to start
	time.Sleep(100 * time.Millisecond)

	// Test discovery endpoint
	resp, err := http.Get("http://localhost:8080/discover")
	if err != nil {
		t.Fatalf("Failed to connect to discovery server: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}
}

func TestDiscoveryServiceHandleNodesRequest(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)
	discovery := NewDiscoveryService(swim, config.DiscoveryConfig)

	// Start discovery service
	if err := discovery.Start(); err != nil {
		t.Fatalf("Failed to start discovery service: %v", err)
	}
	defer discovery.Stop()

	// Give server time to start
	time.Sleep(100 * time.Millisecond)

	// Test nodes endpoint
	resp, err := http.Get("http://localhost:8080/nodes")
	if err != nil {
		t.Fatalf("Failed to connect to discovery server: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}
}
