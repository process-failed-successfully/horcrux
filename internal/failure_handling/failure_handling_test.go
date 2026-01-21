package failure_handling

import (
	"testing"
	"horcruxkv/internal/sharding"
	"horcruxkv/internal/storage"
)

func TestNodeFailureAndRecovery(t *testing.T) {
	// Create a shard manager with 3 nodes
	shardManager := sharding.NewShardManager(3)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Add nodes
	store1 := storage.NewStorage()
	store2 := storage.NewStorage()
	store3 := storage.NewStorage()

	failureHandler.AddNode(0, store1)
	failureHandler.AddNode(1, store2)
	failureHandler.AddNode(2, store3)

	// Store data in node 0
	key := "test_key"
	value := []byte("test_value")
	err := store1.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Verify data is accessible
	retrieved, err := failureHandler.GetDataFromAvailableNodes(key)
	if err != nil {
		t.Fatalf("Failed to retrieve data: %v", err)
	}
	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match stored value")
	}

	// Simulate node failure
	err = failureHandler.SimulateNodeFailure(0)
	if err != nil {
		t.Fatalf("Failed to simulate node failure: %v", err)
	}

	// Verify node is not available
	_, err = failureHandler.GetDataFromAvailableNodes(key)
	if err == nil {
		t.Error("Expected error when node is not available")
	}

	// Verify node health check
	if failureHandler.CheckNodeHealth(0) {
		t.Error("Node should not be healthy after failure")
	}

	// Recover the node
	newStore := storage.NewStorage()
	err = newStore.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value in new store: %v", err)
	}

	err = failureHandler.RecoverNode(0, newStore)
	if err != nil {
		t.Fatalf("Failed to recover node: %v", err)
	}

	// Verify data is accessible again
	retrieved, err = failureHandler.GetDataFromAvailableNodes(key)
	if err != nil {
		t.Fatalf("Failed to retrieve data after recovery: %v", err)
	}
	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match stored value after recovery")
	}

	// Verify node health check
	if !failureHandler.CheckNodeHealth(0) {
		t.Error("Node should be healthy after recovery")
	}
}

func TestRebalanceData(t *testing.T) {
	shardManager := sharding.NewShardManager(3)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Add nodes
	store1 := storage.NewStorage()
	store2 := storage.NewStorage()
	store3 := storage.NewStorage()

	failureHandler.AddNode(0, store1)
	failureHandler.AddNode(1, store2)
	failureHandler.AddNode(2, store3)

	// Rebalancing should not fail
	err := failureHandler.RebalanceData()
	if err != nil {
		t.Fatalf("RebalanceData failed: %v", err)
	}
}

func TestSimulateNodeFailureNonExistentNode(t *testing.T) {
	shardManager := sharding.NewShardManager(3)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Try to fail a non-existent node
	err := failureHandler.SimulateNodeFailure(99)
	if err == nil {
		t.Error("Expected error for non-existent node")
	}
}
