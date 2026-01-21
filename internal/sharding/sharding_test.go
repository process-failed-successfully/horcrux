package sharding

import (
	"testing"
)

func TestShardManagerCreation(t *testing.T) {
	// Test valid creation
	sm, err := NewShardManager(3, 1)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	if len(sm.GetAllNodes()) != 3 {
		t.Errorf("Expected 3 nodes, got %d", len(sm.GetAllNodes()))
	}

	// Test invalid creation - zero nodes
	_, err = NewShardManager(0, 1)
	if err == nil {
		t.Error("Expected error for zero nodes, got nil")
	}

	// Test invalid creation - zero replicas
	_, err = NewShardManager(3, 0)
	if err == nil {
		t.Error("Expected error for zero replicas, got nil")
	}

	// Test invalid creation - replicas > nodes
	_, err = NewShardManager(2, 3)
	if err == nil {
		t.Error("Expected error for replicas > nodes, got nil")
	}
}

func TestStoreAndRetrieve(t *testing.T) {
	sm, err := NewShardManager(3, 1)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	// Store a value
	key := "test_key"
	value := []byte("test_value")
	err = sm.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Retrieve the value
	retrieved, err := sm.Get(key)
	if err != nil {
		t.Fatalf("Failed to retrieve value: %v", err)
	}

	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match. Expected: %s, Got: %s", string(value), string(retrieved))
	}
}

func TestDataDistribution(t *testing.T) {
	sm, err := NewShardManager(4, 1)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	// Store multiple keys
	keys := []string{"key1", "key2", "key3", "key4", "key5"}
	for _, key := range keys {
		err := sm.Store(key, []byte("value_"+key))
		if err != nil {
			t.Fatalf("Failed to store key %s: %v", key, err)
		}
	}

	// Verify data is distributed across nodes
	nodes := sm.GetAllNodes()
	nodeCounts := make(map[int]int)

	for _, key := range keys {
		node, err := sm.GetNode(key)
		if err != nil {
			t.Fatalf("Failed to get node for key %s: %v", key, err)
		}

		// Verify the key exists on the node
		exists := node.Store.Has(key)
		if !exists {
			t.Errorf("Key %s not found on node %d", key, node.ID)
		}

		nodeCounts[node.ID]++
	}

	// Check that data is distributed (not all on one node)
	if len(nodeCounts) != len(nodes) {
		t.Errorf("Data not distributed across all nodes. Node counts: %v", nodeCounts)
	}
}

func TestReplication(t *testing.T) {
	sm, err := NewShardManager(3, 2)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	key := "test_key"
	value := []byte("test_value")
	err = sm.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Verify value is stored on primary and replica nodes
	nodes := sm.GetAllNodes()
	primaryNode, err := sm.GetNode(key)
	if err != nil {
		t.Fatalf("Failed to get primary node: %v", err)
	}

	// Check primary node
	if !primaryNode.Store.Has(key) {
		t.Error("Key not found on primary node")
	}

	// Check replica nodes
	replicaFound := false
	for i := 1; i <= 2; i++ {
		replicaIndex := (primaryNode.ID + i) % len(nodes)
		replicaNode := nodes[replicaIndex]
		if replicaNode.Store.Has(key) {
			replicaFound = true
			break
		}
	}

	if !replicaFound {
		t.Error("Key not found on any replica node")
	}
}

func TestGetNonExistentKey(t *testing.T) {
	sm, err := NewShardManager(3, 1)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	_, err = sm.Get("non_existent_key")
	if err == nil {
		t.Error("Expected error for non-existent key, got nil")
	}
}

func TestEmptyKey(t *testing.T) {
	sm, err := NewShardManager(3, 1)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	err = sm.Store("", []byte("value"))
	if err == nil {
		t.Error("Expected error for empty key, got nil")
	}

	_, err = sm.Get("")
	if err == nil {
		t.Error("Expected error for empty key, got nil")
	}
}

func TestNilValue(t *testing.T) {
	sm, err := NewShardManager(3, 1)
	if err != nil {
		t.Fatalf("Failed to create ShardManager: %v", err)
	}

	err = sm.Store("test_key", nil)
	if err == nil {
		t.Error("Expected error for nil value, got nil")
	}
}
