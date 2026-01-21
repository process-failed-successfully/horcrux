package gossip

import (
	"context"
	"testing"
	"time"
)

func TestDiscovery(t *testing.T) {
	t.Run("TestDiscoveryWithValidConfig", func(t *testing.T) {
		config := DiscoveryConfig{
			Port:        8080,
			Interval:    1 * time.Second,
			Timeout:     500 * time.Millisecond,
			MaxRetries:  3,
			SeedNodes:   []string{"localhost:8081", "localhost:8082"},
		}

		d, err := NewDiscovery(config)
		if err != nil {
			t.Fatalf("Failed to create discovery: %v", err)
		}
		defer d.Stop()

		if d == nil {
			t.Fatal("Discovery instance is nil")
		}
	})

	t.Run("TestDiscoveryWithInvalidPort", func(t *testing.T) {
		config := DiscoveryConfig{
			Port:        0,
			Interval:    1 * time.Second,
			Timeout:     500 * time.Millisecond,
			MaxRetries:  3,
			SeedNodes:   []string{"localhost:8081"},
		}

		_, err := NewDiscovery(config)
		if err == nil {
			t.Fatal("Expected error for invalid port, got nil")
		}
	})

	t.Run("TestDiscoveryWithEmptySeedNodes", func(t *testing.T) {
		config := DiscoveryConfig{
			Port:        8080,
			Interval:    1 * time.Second,
			Timeout:     500 * time.Millisecond,
			MaxRetries:  3,
			SeedNodes:   []string{},
		}

		d, err := NewDiscovery(config)
		if err != nil {
			t.Fatalf("Failed to create discovery: %v", err)
		}
		defer d.Stop()

		if d == nil {
			t.Fatal("Discovery instance is nil")
		}
	})

	t.Run("TestDiscoveryStartAndStop", func(t *testing.T) {
		config := DiscoveryConfig{
			Port:        8080,
			Interval:    1 * time.Second,
			Timeout:     500 * time.Millisecond,
			MaxRetries:  3,
			SeedNodes:   []string{"localhost:8081"},
		}

		d, err := NewDiscovery(config)
		if err != nil {
			t.Fatalf("Failed to create discovery: %v", err)
		}

		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()

		err = d.Start(ctx)
		if err != nil {
			t.Fatalf("Failed to start discovery: %v", err)
		}

		d.Stop()
	})

	t.Run("TestDiscoveryWithMultipleSeedNodes", func(t *testing.T) {
		config := DiscoveryConfig{
			Port:        8080,
			Interval:    1 * time.Second,
			Timeout:     500 * time.Millisecond,
			MaxRetries:  3,
			SeedNodes:   []string{"localhost:8081", "localhost:8082", "localhost:8083"},
		}

		d, err := NewDiscovery(config)
		if err != nil {
			t.Fatalf("Failed to create discovery: %v", err)
		}
		defer d.Stop()

		if len(d.seedNodes) != 3 {
			t.Fatalf("Expected 3 seed nodes, got %d", len(d.seedNodes))
		}
	})
}
