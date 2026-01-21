package gossip

import (
	"context"
	"log"
	"math/rand"
	"time"
)

// FailureDetector handles failure detection for nodes
type FailureDetector struct {
	swim        *SWIM
	ctx         context.Context
	cancel      context.CancelFunc
	probeTicker *time.Ticker
}

// NewFailureDetector creates a new failure detector
func NewFailureDetector(swim *SWIM) *FailureDetector {
	return &FailureDetector{
		swim: swim,
	}
}

// Start starts the failure detector
func (fd *FailureDetector) Start() {
	fd.ctx, fd.cancel = context.WithCancel(context.Background())

	// Start probe loop
	fd.probeTicker = time.NewTicker(1 * time.Second)
	go fd.probeLoop()
}

// Stop stops the failure detector
func (fd *FailureDetector) Stop() {
	if fd.cancel != nil {
		fd.cancel()
	}
	if fd.probeTicker != nil {
		fd.probeTicker.Stop()
	}
}

// probeLoop periodically probes nodes
func (fd *FailureDetector) probeLoop() {
	for {
		select {
		case <-fd.probeTicker.C:
			fd.probeNodes()
		case <-fd.ctx.Done():
			return
		}
	}
}

// probeNodes probes all nodes to check if they are alive
func (fd *FailureDetector) probeNodes() {
	nodes := fd.swim.GetNodes()
	for _, node := range nodes {
		if node.ID == fd.swim.config.NodeID {
			continue // Skip self
		}

		// Simulate probe - in real implementation, this would be a network call
		if rand.Float32() < 0.1 { // 10% chance of failure for testing
			log.Printf("Node %s failed to respond to probe", node.ID)
			fd.handleNodeFailure(node)
		}
	}
}

// handleNodeFailure handles a node that has failed
func (fd *FailureDetector) handleNodeFailure(node *Node) {
	log.Printf("Marking node %s as failed", node.ID)
	// In a real implementation, we would update the node state
	// For now, we just log it
}
