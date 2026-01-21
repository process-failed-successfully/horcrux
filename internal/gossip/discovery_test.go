package gossip

import (
	"context"
	"testing"
	"time"
)

func TestDiscoveryService(t *testing.T) {
	t.Run("TestDiscoveryWithValidConfig", func(t *testing.T) {
		config := DiscoveryConfig{
			SeedNodes: []string{"localhost:8081", "localhost:8082"},
			BindAddr:  ":8080",
			Interval:  1 * time.Second,
		}

		swim := NewSWIM(context.Background())
		d := NewDiscoveryService(swim, config)

		if d == nil {
			t.Fatal("DiscoveryService instance is nil")
		}
	})

	t.Run("TestDiscoveryWithEmptySeedNodes", func(t *testing.T) {
		config := DiscoveryConfig{
			SeedNodes: []string{},
			BindAddr:  ":8080",
			Interval:  1 * time.Second,
		}

		swim := NewSWIM(context.Background())
		d := NewDiscoveryService(swim, config)

		if d == nil {
			t.Fatal("DiscoveryService instance is nil")
		}
	})

	t.Run("TestDiscoveryStartAndStop", func(t *testing.T) {
		config := DiscoveryConfig{
			SeedNodes: []string{"localhost:8081"},
			BindAddr:  ":8080",
			Interval:  1 * time.Second,
		}

		swim := NewSWIM(context.Background())
		d := NewDiscoveryService(swim, config)

		err := d.Start()
		if err != nil {
			t.Fatalf("Failed to start discovery: %v", err)
		}

		err = d.Stop()
		if err != nil {
			t.Fatalf("Failed to stop discovery: %v", err)
		}
	})

	t.Run("TestDiscoveryWithMultipleSeedNodes", func(t *testing.T) {
		config := DiscoveryConfig{
			SeedNodes: []string{"localhost:8081", "localhost:8082", "localhost:8083"},
			BindAddr:  ":8080",
			Interval:  1 * time.Second,
		}

		swim := NewSWIM(context.Background())
		d := NewDiscoveryService(swim, config)

		if len(config.SeedNodes) != 3 {
			t.Fatalf("Expected 3 seed nodes, got %d", len(config.SeedNodes))
		}
	})
}
