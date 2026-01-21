package failure_handling

import (
	"errors"
	"sync"
	"horcruxkv/internal/sharding"
	"horcruxkv/internal/storage"
)

// NodeFailureHandler manages node failures and recovery
type NodeFailureHandler struct {
	shardManager *sharding.ShardManager
	nodes        map[int]*storage.Storage
	mu           sync.RWMutex
}

// NewNodeFailureHandler creates a new NodeFailureHandler
func NewNodeFailureHandler(shardManager *sharding.ShardManager) *NodeFailureHandler {
	return &NodeFailureHandler{
		shardManager: shardManager,
		nodes:        make(map[int]*storage.Storage),
	}
}

// AddNode adds a node to the failure handler
func (nfh *NodeFailureHandler) AddNode(nodeID int, store *storage.Storage) {
	nfh.mu.Lock()
	defer nfh.mu.Unlock()
	nfh.nodes[nodeID] = store
}

// SimulateNodeFailure simulates a node failure
func (nfh *NodeFailureHandler) SimulateNodeFailure(nodeID int) error {
	nfh.mu.Lock()
	defer nfh.mu.Unlock()

	if _, exists := nfh.nodes[nodeID]; !exists {
		return errors.New("node does not exist")
	}

	// Remove the node from the map to simulate failure
	delete(nfh.nodes, nodeID)
	return nil
}

// RecoverNode recovers a failed node
func (nfh *NodeFailureHandler) RecoverNode(nodeID int, store *storage.Storage) error {
	nfh.mu.Lock()
	defer nfh.mu.Unlock()

	nfh.nodes[nodeID] = store
	return nil
}

// GetDataFromAvailableNodes retrieves data from available nodes
func (nfh *NodeFailureHandler) GetDataFromAvailableNodes(key string) ([]byte, error) {
	nfh.mu.RLock()
	defer nfh.mu.RUnlock()

	// Get the shard for the key using the shard manager's GetShard method
	shardID := nfh.shardManager.GetShard(key)

	// Check if the node is available
	if store, exists := nfh.nodes[shardID]; exists {
		return store.Get(key)
	}

	return nil, errors.New("node not available")
}

// RebalanceData rebalances data across available nodes
func (nfh *NodeFailureHandler) RebalanceData() error {
	nfh.mu.Lock()
	defer nfh.mu.Unlock()

	// This is a simplified rebalancing strategy
	// In a real implementation, we would redistribute data from failed nodes
	// to available nodes based on the sharding strategy

	return nil
}

// CheckNodeHealth checks if a node is healthy
func (nfh *NodeFailureHandler) CheckNodeHealth(nodeID int) bool {
	nfh.mu.RLock()
	defer nfh.mu.RUnlock()

	_, exists := nfh.nodes[nodeID]
	return exists
}
