package gossip

import (
	"context"
	"sync"
	"time"
)

// NodeState represents the state of a node
type NodeState int

const (
	NodeAlive NodeState = iota
	NodeSuspected
	NodeFailed
)

// Node represents a node in the cluster
type Node struct {
	ID    string
	Addr  string
	State NodeState
}

// Config represents the configuration for SWIM
type Config struct {
	NodeID            string
	BindAddr          string
	SeedNodes         []string
	ProbeInterval     time.Duration
	SuspicionMultiplier int
}

// SWIM represents the SWIM gossip protocol implementation
type SWIM struct {
	ctx    context.Context
	cancel context.CancelFunc
	mu     sync.Mutex
	nodes  map[string]*Node
	config Config
	done   chan struct{}
}

// NewSWIM creates a new SWIM instance
func NewSWIM(ctx context.Context) *SWIM {
	if ctx == nil {
		ctx = context.Background()
	}

	ctx, cancel := context.WithCancel(ctx)

	return &SWIM{
		ctx:    ctx,
		cancel: cancel,
		nodes:  make(map[string]*Node),
		done:   make(chan struct{}),
	}
}

// Start starts the SWIM protocol
func (s *SWIM) Start() {
	// Start failure detector
	fd := NewFailureDetector(s)
	fd.Start()
}

// Stop stops the SWIM protocol
func (s *SWIM) Stop() {
	s.cancel()
	close(s.done)
}

// GetNodes returns all nodes
func (s *SWIM) GetNodes() []*Node {
	s.mu.Lock()
	defer s.mu.Unlock()

	nodes := make([]*Node, 0, len(s.nodes))
	for _, node := range s.nodes {
		nodes = append(nodes, node)
	}
	return nodes
}

// GetNode returns a specific node by ID
func (s *SWIM) GetNode(id string) *Node {
	s.mu.Lock()
	defer s.mu.Unlock()

	return s.nodes[id]
}

// AddNode adds a node to the cluster
func (s *SWIM) AddNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.nodes[node.ID] = node
}

// updateNode updates a node in the cluster
func (s *SWIM) updateNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.nodes[node.ID] = node
}
