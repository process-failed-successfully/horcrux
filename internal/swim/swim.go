package swim

import (
	"context"
	"log"
	"math/rand"
	"sync"
	"time"
)

// MessageType defines the type of SWIM message
type MessageType string

const (
	PingMessage     MessageType = "ping"
	PingReqMessage  MessageType = "ping-req"
	AckMessage      MessageType = "ack"
	GossipMessage   MessageType = "gossip"
)

// Message represents a SWIM protocol message
type Message struct {
	Type      MessageType
	Sender    *Node
	Target    *Node
	Members   map[string]*Node
	Timestamp time.Time
}

// Node represents a member in the cluster
type Node struct {
	ID      string
	Address string
	Status  string // alive, suspect, dead
	LastSeen time.Time
}

// SWIM is the main gossip protocol implementation
type SWIM struct {
	mu            sync.RWMutex
	self          *Node
	members       map[string]*Node
	config        Config
	messageChan   chan Message
	pingHandler   func(ctx context.Context, target *Node) (bool, error)
	pingReqHandler func(ctx context.Context, sender *Node, target *Node) (bool, error)
	ackHandler    func(ctx context.Context, sender *Node) error
}

// Config holds SWIM configuration
type Config struct {
	GossipInterval    time.Duration
	PingTimeout       time.Duration
	PingReqTimeout    time.Duration
	FailureThreshold  int
	MaxGossipPeers    int
	ProbeInterval     time.Duration
}

// NewSWIM creates a new SWIM instance
func NewSWIM(self *Node, config Config) *SWIM {
	if config.GossipInterval == 0 {
		config.GossipInterval = 1 * time.Second
	}
	if config.PingTimeout == 0 {
		config.PingTimeout = 500 * time.Millisecond
	}
	if config.PingReqTimeout == 0 {
		config.PingReqTimeout = 1 * time.Second
	}
	if config.FailureThreshold == 0 {
		config.FailureThreshold = 3
	}
	if config.MaxGossipPeers == 0 {
		config.MaxGossipPeers = 3
	}
	if config.ProbeInterval == 0 {
		config.ProbeInterval = 2 * time.Second
	}

	return &SWIM{
		self:        self,
		members:     make(map[string]*Node),
		config:      config,
		messageChan: make(chan Message, 100),
	}
}

// AddMember adds a new node to the membership list
func (s *SWIM) AddMember(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.members[node.ID] = node
}

// GetMembers returns the current membership list
func (s *SWIM) GetMembers() map[string]*Node {
	s.mu.RLock()
	defer s.mu.RUnlock()

	members := make(map[string]*Node)
	for id, node := range s.members {
		members[id] = &Node{
			ID:      node.ID,
			Address: node.Address,
			Status:  node.Status,
			LastSeen: node.LastSeen,
		}
	}
	return members
}

// Start begins the SWIM protocol
func (s *SWIM) Start(ctx context.Context) {
	// Start message processor
	go s.processMessages(ctx)

	// Start gossip dissemination
	go s.gossipLoop(ctx)

	// Start failure detection
	go s.failureDetectionLoop(ctx)
}

// processMessages handles incoming SWIM messages
func (s *SWIM) processMessages(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-s.messageChan:
			s.handleMessage(msg)
		}
	}
}

// handleMessage processes different types of SWIM messages
func (s *SWIM) handleMessage(msg Message) {
	switch msg.Type {
	case PingMessage:
		s.handlePing(msg)
	case PingReqMessage:
		s.handlePingReq(msg)
	case AckMessage:
		s.handleAck(msg)
	case GossipMessage:
		s.handleGossip(msg)
	}
}

// handlePing processes a ping message
func (s *SWIM) handlePing(msg Message) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Update the sender's last seen time
	if node, ok := s.members[msg.Sender.ID]; ok {
		node.LastSeen = time.Now()
		if node.Status != "alive" {
			node.Status = "alive"
		}
	}

	// Send ack back to sender
	ackMsg := Message{
		Type:   AckMessage,
		Sender: s.self,
	}
	s.messageChan <- ackMsg
}

// handlePingReq processes a ping request
func (s *SWIM) handlePingReq(msg Message) {
	// In a real implementation, we would ping the target node
	// For now, we'll just send an ack
	ackMsg := Message{
		Type:   AckMessage,
		Sender: s.self,
	}
	s.messageChan <- ackMsg
}

// handleAck processes an acknowledgment
func (s *SWIM) handleAck(msg Message) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Update the sender's last seen time
	if node, ok := s.members[msg.Sender.ID]; ok {
		node.LastSeen = time.Now()
		if node.Status != "alive" {
			node.Status = "alive"
		}
	}
}

// handleGossip processes a gossip message
func (s *SWIM) handleGossip(msg Message) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Update membership with gossip information
	for id, node := range msg.Members {
		if existing, ok := s.members[id]; ok {
			// Update existing node
			existing.Status = node.Status
			existing.LastSeen = node.LastSeen
			existing.Address = node.Address
		} else {
			// Add new node
			s.members[id] = &Node{
				ID:      node.ID,
				Address: node.Address,
				Status:  node.Status,
				LastSeen: node.LastSeen,
			}
		}
	}
}

// gossipLoop periodically sends gossip messages
func (s *SWIM) gossipLoop(ctx context.Context) {
	ticker := time.NewTicker(s.config.GossipInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.gossip()
		}
	}
}

// gossip sends membership information to random peers
func (s *SWIM) gossip() {
	s.mu.RLock()

	if len(s.members) <= 1 {
		s.mu.RUnlock()
		return // No one to gossip to
	}

	// Create gossip message with current membership
	gossipMsg := Message{
		Type:    GossipMessage,
		Sender:  s.self,
		Members: s.getMembersCopy(),
	}

	// Select random peers to gossip to
	peers := s.selectRandomPeers(s.config.MaxGossipPeers)
	s.mu.RUnlock()

	for _, peer := range peers {
		if peer.ID == s.self.ID {
			continue // Don't gossip to self
		}

		// In a real implementation, we would send this to the peer
		// For testing purposes, we'll simulate receiving it
		log.Printf("Sending gossip to %s with %d members", peer.Address, len(gossipMsg.Members))

		// Simulate the peer receiving and processing the gossip
		s.handleGossip(gossipMsg)
	}
}

// getMembersCopy returns a copy of the members map
func (s *SWIM) getMembersCopy() map[string]*Node {
	members := make(map[string]*Node)
	for id, node := range s.members {
		members[id] = &Node{
			ID:      node.ID,
			Address: node.Address,
			Status:  node.Status,
			LastSeen: node.LastSeen,
		}
	}
	return members
}

// selectRandomPeers selects n random peers from the membership list
func (s *SWIM) selectRandomPeers(n int) []*Node {
	peers := make([]*Node, 0, len(s.members))
	for _, node := range s.members {
		peers = append(peers, node)
	}

	// Shuffle the peers
	for i := range peers {
		j := rand.Intn(i + 1)
		peers[i], peers[j] = peers[j], peers[i]
	}

	if n > len(peers) {
		n = len(peers)
	}
	return peers[:n]
}

// failureDetectionLoop periodically checks for failed nodes
func (s *SWIM) failureDetectionLoop(ctx context.Context) {
	ticker := time.NewTicker(s.config.ProbeInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.detectFailures()
		}
	}
}

// detectFailures checks for nodes that haven't been seen recently
func (s *SWIM) detectFailures() {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now()
	for id, node := range s.members {
		if node.Status == "dead" {
			continue
		}

		if now.Sub(node.LastSeen) > s.config.PingTimeout*time.Duration(s.config.FailureThreshold) {
			log.Printf("Marking node %s as dead (last seen: %v)", id, node.LastSeen)
			node.Status = "dead"
		}
	}
}

// UpdateLastSeen updates the last seen time for a node
func (s *SWIM) UpdateLastSeen(nodeID string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if node, ok := s.members[nodeID]; ok {
		node.LastSeen = time.Now()
		if node.Status != "alive" {
			node.Status = "alive"
		}
	}
}
