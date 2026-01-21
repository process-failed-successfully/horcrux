package gossip

import (
	"context"
	"log"
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
	ID      string
	Address string
	State   NodeState
}

// Config holds configuration for the SWIM gossip provider
type Config struct {
	NodeID         string
	BindAddr       string
	AdvertiseAddr  string
	GossipInterval time.Duration
	ProbeInterval  time.Duration
	SuspicionMultiplier int
	DiscoveryConfig
}

// SWIM is the main SWIM gossip provider
type SWIM struct {
	config Config
	nodes  map[string]*Node
	mu     sync.RWMutex
	ctx    context.Context
	cancel context.CancelFunc
	done   chan struct{}
	discoveryService *DiscoveryService
	failureDetector *FailureDetector
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

	swim := &SWIM{
		config: config,
		nodes:  make(map[string]*Node),
		done:   make(chan struct{}),
	}

	// Add self to the node list
	selfNode := &Node{
		ID:      config.NodeID,
		Address: config.AdvertiseAddr,
		State:   NodeAlive,
	}
	swim.addNode(selfNode)

	return swim
}

// Start starts the SWIM gossip provider
func (s *SWIM) Start() error {
	s.ctx, s.cancel = context.WithCancel(context.Background())

	// Initialize discovery service
	s.discoveryService = NewDiscoveryService(s, s.config.DiscoveryConfig)
	if err := s.discoveryService.Start(); err != nil {
		return err
	}

	// Initialize failure detector
	s.failureDetector = NewFailureDetector(s)
	s.failureDetector.Start()

	// Start gossip loop
	go s.gossipLoop()

	log.Printf("SWIM gossip provider started for node %s", s.config.NodeID)
	return nil
}

// Stop stops the SWIM gossip provider
func (s *SWIM) Stop() error {
	if s.cancel != nil {
		s.cancel()
	}

	if s.discoveryService != nil {
		s.discoveryService.Stop()
	}

	// Only close done channel if it's not already closed
	select {
	case <-s.done:
		// Already closed
	default:
		close(s.done)
	}

	log.Printf("SWIM gossip provider stopped for node %s", s.config.NodeID)
	return nil
}

// gossipLoop periodically gossips with other nodes
func (s *SWIM) gossipLoop() {
	ticker := time.NewTicker(s.config.GossipInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			s.gossipWithNodes()
		case <-s.done:
			return
		}
	}
}

// gossipWithNodes gossips with other nodes
func (s *SWIM) gossipWithNodes() {
	nodes := s.GetNodes()
	log.Printf("Gossiping with %d nodes", len(nodes))
}

// AddNode adds a node to the cluster
func (s *SWIM) AddNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.nodes[node.ID]; !exists {
		s.nodes[node.ID] = node
		log.Printf("Added node %s to cluster", node.ID)
	}
}

// GetNodes returns the list of nodes
func (s *SWIM) GetNodes() []*Node {
	s.mu.RLock()
	defer s.mu.RUnlock()

	nodes := make([]*Node, 0, len(s.nodes))
	for _, node := range s.nodes {
		nodes = append(nodes, node)
	}
	return nodes
}

// GetNode returns a specific node by ID
func (s *SWIM) GetNode(nodeID string) (*Node, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	node, exists := s.nodes[nodeID]
	return node, exists
}

// updateNode updates a node in the cluster
func (s *SWIM) updateNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.nodes[node.ID] = node
}

// addNode adds a node to the cluster (internal)
func (s *SWIM) addNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.nodes[node.ID] = node
}
