package failure_handling

import (
	"errors"
	"sync"
	"horcruxkv/internal/sharding"
)

// NodeFailureHandler manages node failures and recovery
type NodeFailureHandler struct {
	shardManager *sharding.ShardManager
	failedNodes  map[int]bool
	mu           sync.RWMutex
}

// NewNodeFailureHandler creates a new NodeFailureHandler
func NewNodeFailureHandler(shardManager *sharding.ShardManager) *NodeFailureHandler {
	return &NodeFailureHandler{
		shardManager: shardManager,
		failedNodes:  make(map[int]bool),
	}
}

// SimulateNodeFailure simulates a node failure
func (nfh *NodeFailureHandler) SimulateNodeFailure(nodeID int) error {
	nfh.mu.Lock()
	defer nfh.mu.Unlock()

	// Check if node exists
	nodes := nfh.shardManager.GetAllNodes()
	found := false
	for _, node := range nodes {
		if node.ID == nodeID {
			found = true
			break
		}
	}
	if !found {
		return errors.New("node does not exist")
	}

	nfh.failedNodes[nodeID] = true
	return nil
}

// RecoverNode recovers a failed node
func (nfh *NodeFailureHandler) RecoverNode(nodeID int) error {
	nfh.mu.Lock()
	defer nfh.mu.Unlock()

	// Check if node exists
	nodes := nfh.shardManager.GetAllNodes()
	found := false
	for _, node := range nodes {
		if node.ID == nodeID {
			found = true
			break
		}
	}
	if !found {
		return errors.New("node does not exist")
	}

	delete(nfh.failedNodes, nodeID)
	return nil
}

// GetDataFromAvailableNodes retrieves data from available nodes
func (nfh *NodeFailureHandler) GetDataFromAvailableNodes(key string) ([]byte, error) {
	nfh.mu.RLock()
	defer nfh.mu.RUnlock()

	// Get all nodes from shard manager
	nodes := nfh.shardManager.GetAllNodes()

	// Try to get data from available nodes
	for _, node := range nodes {
		if !nfh.failedNodes[node.ID] {
			value, err := node.Store.Get(key)
			if err == nil {
				return value, nil
			}
		}
	}

	return nil, errors.New("key not found on any available node")
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

	return !nfh.failedNodes[nodeID]
}
