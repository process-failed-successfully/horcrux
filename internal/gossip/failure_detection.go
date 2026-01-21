package gossip

import (
	"context"
	"log"
	"time"
)

// FailureDetector handles failure detection
type FailureDetector struct {
	swim   *SWIM
	ctx    context.Context
	cancel context.CancelFunc
}

// NewFailureDetector creates a new failure detector
func NewFailureDetector(swim *SWIM) *FailureDetector {
	ctx, cancel := context.WithCancel(context.Background())
	return &FailureDetector{
		swim:   swim,
		ctx:    ctx,
		cancel: cancel,
	}
}

// Start starts the failure detector
func (fd *FailureDetector) Start() {
	go fd.run()
}

// Stop stops the failure detector
func (fd *FailureDetector) Stop() {
	fd.cancel()
}

// run is the main failure detection loop
func (fd *FailureDetector) run() {
	ticker := time.NewTicker(fd.swim.config.ProbeInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			fd.probeNodes()
		case <-fd.ctx.Done():
			return
		}
	}
}

// probeNodes probes all nodes to detect failures
func (fd *FailureDetector) probeNodes() {
	nodes := fd.swim.GetNodes()
	for _, node := range nodes {
		if node.State == NodeAlive {
			// Simulate probing
			log.Printf("Probing node %s at %s", node.ID, node.Addr)
		}
	}
}
