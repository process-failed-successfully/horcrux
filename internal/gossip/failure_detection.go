package gossip

import (
	"log"
	"math/rand"
	"sync"
	"time"
)

// FailureDetector handles failure detection using SWIM protocol
type FailureDetector struct {
	swim           *SWIM
	mu             sync.RWMutex
	suspects       map[string]time.Time
	failureTimeout time.Duration
	pingTimeout    time.Duration
}

// NewFailureDetector creates a new failure detector
func NewFailureDetector(swim *SWIM) *FailureDetector {
	return &FailureDetector{
		swim:           swim,
		suspects:       make(map[string]time.Time),
		failureTimeout: time.Duration(swim.config.SuspicionMultiplier) * swim.config.ProbeInterval,
		pingTimeout:    swim.config.ProbeInterval,
	}
}

// Start starts the failure detection process
func (fd *FailureDetector) Start() {
	go fd.monitorNodes()
}

// monitorNodes periodically checks node health
func (fd *FailureDetector) monitorNodes() {
	ticker := time.NewTicker(fd.pingTimeout)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			fd.checkNodeHealth()
		case <-fd.swim.done:
			return
		}
	}
}

// checkNodeHealth checks the health of all nodes
func (fd *FailureDetector) checkNodeHealth() {
	nodes := fd.swim.GetNodes()

	for _, node := range nodes {
		if node.ID == fd.swim.config.NodeID {
			continue // Skip self
		}

		if node.State == NodeFailed {
			continue // Already marked as failed
		}

		if fd.isSuspected(node.ID) {
			// Node is already suspected, check if timeout has passed
			if time.Since(fd.getSuspicionTime(node.ID)) > fd.failureTimeout {
				fd.markNodeAsFailed(node)
			}
			continue
		}

		// Ping the node
		go fd.pingNode(node)
	}
}

// pingNode sends a ping to a node
func (fd *FailureDetector) pingNode(node *Node) {
	// Simulate network ping
	// In a real implementation, this would be an actual network call
	// For now, we'll simulate with random failures for testing
	if rand.Float32() < 0.1 { // 10% chance of failure for testing
		fd.handlePingFailure(node)
		return
	}

	// Ping successful
	fd.mu.Lock()
	defer fd.mu.Unlock()
	delete(fd.suspects, node.ID)
}

// handlePingFailure handles a failed ping
func (fd *FailureDetector) handlePingFailure(node *Node) {
	fd.mu.Lock()
	defer fd.mu.Unlock()

	// Mark node as suspected
	fd.suspects[node.ID] = time.Now()
	log.Printf("Node %s is suspected of failure", node.ID)

	// In a real SWIM implementation, we would ask other nodes to ping this node
	// For simplicity, we'll just mark it as suspected and wait for timeout
}

// markNodeAsFailed marks a node as failed
func (fd *FailureDetector) markNodeAsFailed(node *Node) {
	fd.mu.Lock()
	defer fd.mu.Unlock()

	// Remove from suspects
	delete(fd.suspects, node.ID)

	// Update node state
	node.State = NodeFailed
	fd.swim.updateNode(node)

	log.Printf("Node %s marked as failed", node.ID)
}

// isSuspected checks if a node is suspected
func (fd *FailureDetector) isSuspected(nodeID string) bool {
	fd.mu.RLock()
	defer fd.mu.RUnlock()

	_, exists := fd.suspects[nodeID]
	return exists
}

// getSuspicionTime gets the time when a node was suspected
func (fd *FailureDetector) getSuspicionTime(nodeID string) time.Time {
	fd.mu.RLock()
	defer fd.mu.RUnlock()

	return fd.suspects[nodeID]
}

// GetSuspectedNodes returns the list of suspected nodes
func (fd *FailureDetector) GetSuspectedNodes() []string {
	fd.mu.RLock()
	defer fd.mu.RUnlock()

	nodes := make([]string, 0, len(fd.suspects))
	for id := range fd.suspects {
		nodes = append(nodes, id)
	}
	return nodes
}
