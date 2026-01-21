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

// DiscoveryConfig represents the configuration for node discovery
type DiscoveryConfig struct {
	SeedNodes []string
	BindAddr  string
	Interval  time.Duration
}

// Config represents the configuration for SWIM
type Config struct {
	NodeID            string
	BindAddr          string
	AdvertiseAddr     string
	SeedNodes         []string
	ProbeInterval     time.Duration
	SuspicionMultiplier int
	GossipInterval    time.Duration
	DiscoveryConfig   DiscoveryConfig
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

// NewSWIM creates a new SWIM instance with the given configuration
func NewSWIM(ctx context.Context, config Config) *SWIM {
	if ctx == nil {
		ctx = context.Background()
	}

	ctx, cancel := context.WithCancel(ctx)

	// Set default values if not provided
	if config.GossipInterval == 0 {
		config.GossipInterval = 1 * time.Second
	}
	if config.ProbeInterval == 0 {
		config.ProbeInterval = 1 * time.Second
	}
	if config.SuspicionMultiplier == 0 {
		config.SuspicionMultiplier = 3
	}

	swim := &SWIM{
		ctx:    ctx,
		cancel: cancel,
		nodes:  make(map[string]*Node),
		config: config,
		done:   make(chan struct{}),
	}

	// Add self node
	swim.AddNode(&Node{
		ID:    config.NodeID,
		Addr:  config.AdvertiseAddr,
		State: NodeAlive,
	})

	return swim
}

// Start starts the SWIM protocol
func (s *SWIM) Start() error {
	// Start failure detector
	fd := NewFailureDetector(s)
	go fd.Start()

	// Start discovery service if configured
	if len(s.config.SeedNodes) > 0 || s.config.DiscoveryConfig.BindAddr != "" {
		ds := NewDiscoveryService(s, s.config.DiscoveryConfig)
		go ds.Start()
	}

	return nil
}

// Stop stops the SWIM protocol
func (s *SWIM) Stop() error {
	s.cancel()
	<-s.done
	return nil
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
