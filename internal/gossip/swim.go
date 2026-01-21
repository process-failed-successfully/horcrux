package gossip

import (
	"context"
	"log"
	"sync"
	"time"
)

// Config holds configuration for the SWIM gossip provider
type Config struct {
	// NodeID is the unique identifier for this node
	NodeID string
	// BindAddr is the address to bind to for gossip communication
	BindAddr string
	// AdvertiseAddr is the address to advertise to other nodes
	AdvertiseAddr string
	// GossipInterval is how often to gossip with other nodes
	GossipInterval time.Duration
	// ProbeInterval is how often to probe for failed nodes
	ProbeInterval time.Duration
	// SuspicionMultiplier is the multiplier for suspicion timeout
	SuspicionMultiplier int
}

// Node represents a node in the cluster
type Node struct {
	ID      string
	Address string
	State   NodeState
}

// NodeState represents the state of a node
type NodeState int

const (
	NodeAlive NodeState = iota
	NodeSuspicious
	NodeDead
)

// SWIM is the main gossip provider implementing the SWIM protocol
type SWIM struct {
	config Config
	nodes  map[string]*Node
	mu     sync.RWMutex
	ctx    context.Context
	cancel context.CancelFunc
	done   chan struct{}
}

// NewSWIM creates a new SWIM gossip provider
func NewSWIM(config Config) *SWIM {
	if config.GossipInterval == 0 {
		config.GossipInterval = 1 * time.Second
	}
	if config.ProbeInterval == 0 {
		config.ProbeInterval = 1 * time.Second
	}
	if config.SuspicionMultiplier == 0 {
		config.SuspicionMultiplier = 3
	}

	s := &SWIM{
		config: config,
		nodes:  make(map[string]*Node),
	}

	// Add self to the node list
	s.nodes[config.NodeID] = &Node{
		ID:      config.NodeID,
		Address: config.AdvertiseAddr,
		State:   NodeAlive,
	}

	return s
}

// Start starts the SWIM gossip provider
func (s *SWIM) Start() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.ctx != nil {
		return nil // Already started
	}

	s.ctx, s.cancel = context.WithCancel(context.Background())
	s.done = make(chan struct{})

	// Start gossip loop
	go s.gossipLoop()
	// Start failure detection loop
	go s.failureDetectionLoop()

	log.Printf("SWIM gossip provider started for node %s", s.config.NodeID)
	return nil
}

// Stop stops the SWIM gossip provider
func (s *SWIM) Stop() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.cancel == nil {
		return nil // Not started
	}

	s.cancel()
	<-s.done
	log.Printf("SWIM gossip provider stopped for node %s", s.config.NodeID)
	return nil
}

// gossipLoop handles periodic gossip with other nodes
func (s *SWIM) gossipLoop() {
	ticker := time.NewTicker(s.config.GossipInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			s.gossip()
		case <-s.ctx.Done():
			close(s.done)
			return
		}
	}
}

// failureDetectionLoop handles failure detection
func (s *SWIM) failureDetectionLoop() {
	ticker := time.NewTicker(s.config.ProbeInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			s.detectFailures()
		case <-s.ctx.Done():
			return
		}
	}
}

// gossip implements the gossip protocol
func (s *SWIM) gossip() {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// TODO: Implement actual gossip protocol
	log.Printf("Gossiping with %d nodes", len(s.nodes))
}

// detectFailures implements failure detection
func (s *SWIM) detectFailures() {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// TODO: Implement actual failure detection
}

// AddNode adds a node to the cluster
func (s *SWIM) AddNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.nodes[node.ID] = node
	log.Printf("Added node %s to cluster", node.ID)
}

// GetNodes returns all known nodes
func (s *SWIM) GetNodes() []*Node {
	s.mu.RLock()
	defer s.mu.RUnlock()

	nodes := make([]*Node, 0, len(s.nodes))
	for _, node := range s.nodes {
		nodes = append(nodes, node)
	}
	return nodes
}
