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
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)
	nodes := swim.GetNodes()

	if len(nodes) != 1 {
		t.Errorf("Expected 1 node (self), got %d", len(nodes))
	}

	if nodes[0].ID != config.NodeID {
		t.Errorf("Expected self node ID %s, got %s", config.NodeID, nodes[0].ID)
	}
}

func TestSWIMStartStop(t *testing.T) {
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

	// Wait a bit to ensure everything started
	time.Sleep(100 * time.Millisecond)

	if err := swim.Stop(); err != nil {
		t.Fatalf("Failed to stop SWIM: %v", err)
	}
}

func TestSWIMConfigDefaults(t *testing.T) {
	config := Config{
		NodeID:      "node1",
		BindAddr:    "127.0.0.1:8000",
		AdvertiseAddr: "127.0.0.1:8000",
		DiscoveryConfig: DiscoveryConfig{
			SeedNodes: []string{},
		},
	}

	swim := NewSWIM(config)

	if swim.config.GossipInterval != 1*time.Second {
		t.Errorf("Expected default GossipInterval 1s, got %v", swim.config.GossipInterval)
	}

	if swim.config.ProbeInterval != 1*time.Second {
		t.Errorf("Expected default ProbeInterval 1s, got %v", swim.config.ProbeInterval)
	}

	if swim.config.SuspicionMultiplier != 3 {
		t.Errorf("Expected default SuspicionMultiplier 3, got %d", swim.config.SuspicionMultiplier)
	}
}
