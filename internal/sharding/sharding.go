package sharding

import (
	"errors"
	"hash/fnv"
	"horcruxkv/internal/storage"
	"sync"
)

// Node represents a storage node in the cluster
type Node struct {
	ID     int
	Store  *storage.Storage
}

// ShardManager handles data sharding across multiple nodes
type ShardManager struct {
	nodes      []*Node
	replicas   int
	mu         sync.RWMutex
}

// NewShardManager creates a new ShardManager with specified number of nodes and replicas
func NewShardManager(numNodes, replicas int) (*ShardManager, error) {
	if numNodes <= 0 {
		return nil, errors.New("number of nodes must be positive")
	}
	if replicas <= 0 {
		return nil, errors.New("number of replicas must be positive")
	}
	if replicas > numNodes {
		return nil, errors.New("replicas cannot exceed number of nodes")
	}

	sm := &ShardManager{
		replicas: replicas,
	}

	// Initialize nodes
	for i := 0; i < numNodes; i++ {
		node := &Node{
			ID:    i,
			Store: storage.NewStorage(),
		}
		sm.nodes = append(sm.nodes, node)
	}

	return sm, nil
}

// GetNode returns the node responsible for a given key
func (sm *ShardManager) GetNode(key string) (*Node, error) {
	if key == "" {
		return nil, errors.New("key cannot be empty")
	}

	sm.mu.RLock()
	defer sm.mu.RUnlock()

	if len(sm.nodes) == 0 {
		return nil, errors.New("no nodes available")
	}

	// Use consistent hashing to determine node
	hash := fnv.New32a()
	hash.Write([]byte(key))
	nodeIndex := int(hash.Sum32()) % len(sm.nodes)

	return sm.nodes[nodeIndex], nil
}

// Store stores a key-value pair across the appropriate nodes
func (sm *ShardManager) Store(key string, value []byte) error {
	if key == "" {
		return errors.New("key cannot be empty")
	}
	if value == nil {
		return errors.New("value cannot be nil")
	}

	sm.mu.RLock()
	defer sm.mu.RUnlock()

	if len(sm.nodes) == 0 {
		return errors.New("no nodes available")
	}

	// Store on primary node
	primaryNode, err := sm.getNodeForKey(key)
	if err != nil {
		return err
	}

	if err := primaryNode.Store.Store(key, value); err != nil {
		return err
	}

	// Store on replica nodes
	for i := 1; i <= sm.replicas; i++ {
		replicaIndex := (primaryNode.ID + i) % len(sm.nodes)
		replicaNode := sm.nodes[replicaIndex]
		if err := replicaNode.Store.Store(key, value); err != nil {
			return err
		}
	}

	return nil
}

// Get retrieves a value by key from the appropriate node
func (sm *ShardManager) Get(key string) ([]byte, error) {
	if key == "" {
		return nil, errors.New("key cannot be empty")
	}

	sm.mu.RLock()
	defer sm.mu.RUnlock()

	if len(sm.nodes) == 0 {
		return nil, errors.New("no nodes available")
	}

	// Try primary node first
	primaryNode, err := sm.getNodeForKey(key)
	if err != nil {
		return nil, err
	}

	value, err := primaryNode.Store.Get(key)
	if err == nil {
		return value, nil
	}

	// If primary fails, try replicas
	for i := 1; i <= sm.replicas; i++ {
		replicaIndex := (primaryNode.ID + i) % len(sm.nodes)
		replicaNode := sm.nodes[replicaIndex]
		value, err := replicaNode.Store.Get(key)
		if err == nil {
			return value, nil
		}
	}

	return nil, errors.New("key not found on any node")
}

// GetAllNodes returns all nodes in the cluster
func (sm *ShardManager) GetAllNodes() []*Node {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	nodes := make([]*Node, len(sm.nodes))
	copy(nodes, sm.nodes)
	return nodes
}

// getNodeForKey is a helper method to get the node for a key (without locking)
func (sm *ShardManager) getNodeForKey(key string) (*Node, error) {
	if len(sm.nodes) == 0 {
		return nil, errors.New("no nodes available")
	}

	hash := fnv.New32a()
	hash.Write([]byte(key))
	nodeIndex := int(hash.Sum32()) % len(sm.nodes)

	return sm.nodes[nodeIndex], nil
}
