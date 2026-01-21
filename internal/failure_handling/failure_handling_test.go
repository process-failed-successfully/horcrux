package failure_handling

import (
	"testing"
	"horcruxkv/internal/sharding"
)

func TestNodeFailureAndRecovery(t *testing.T) {
	// Create a shard manager with 3 nodes and 1 replica
	shardManager, _ := sharding.NewShardManager(3, 1)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Store data through the shard manager
	key := "test_key"
	value := []byte("test_value")
	err := shardManager.Store(key, value)
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

	// Simulate node failure (node 0 is the primary for this key)
	err = failureHandler.SimulateNodeFailure(0)
	if err != nil {
		t.Fatalf("Failed to simulate node failure: %v", err)
	}

	// Verify node is not available
	if failureHandler.CheckNodeHealth(0) {
		t.Error("Node should not be healthy after failure")
	}

	// Data should still be accessible from replica (node 1)
	retrieved, err = failureHandler.GetDataFromAvailableNodes(key)
	if err != nil {
		t.Fatalf("Failed to retrieve data from replica: %v", err)
	}
	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match stored value from replica")
	}

	// Recover the node
	err = failureHandler.RecoverNode(0)
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
	shardManager, _ := sharding.NewShardManager(3, 1)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Rebalancing should not fail
	err := failureHandler.RebalanceData()
	if err != nil {
		t.Fatalf("RebalanceData failed: %v", err)
	}
}

func TestSimulateNodeFailureNonExistentNode(t *testing.T) {
	shardManager, _ := sharding.NewShardManager(3, 1)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Try to fail a non-existent node
	err := failureHandler.SimulateNodeFailure(99)
	if err == nil {
		t.Error("Expected error for non-existent node")
	}
}

func TestGetDataFromFailedNode(t *testing.T) {
	shardManager, _ := sharding.NewShardManager(3, 1)
	failureHandler := NewNodeFailureHandler(shardManager)

	// Store data
	key := "test_key"
	value := []byte("test_value")
	err := shardManager.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Fail all nodes
	for i := 0; i < 3; i++ {
		err = failureHandler.SimulateNodeFailure(i)
		if err != nil {
			t.Fatalf("Failed to simulate node failure: %v", err)
		}
	}

	// Data should not be accessible
	_, err = failureHandler.GetDataFromAvailableNodes(key)
	if err == nil {
		t.Error("Expected error when all nodes are failed")
	}
}
