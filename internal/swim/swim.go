package swim

import (
	"context"
	"sync"
	"time"
)

// Node represents a node in the cluster
type Node struct {
	ID      string
	Address string
	Status  string
}

// Config represents SWIM configuration
type Config struct {
	GossipInterval   time.Duration
	PingTimeout      time.Duration
	FailureThreshold int
}

// MessageType represents the type of a message
type MessageType string

const (
	PingMessage   MessageType = "ping"
	GossipMessage MessageType = "gossip"
)

// Message represents a gossip message
type Message struct {
	Type    MessageType
	Sender  *Node
	Members map[string]*Node
}

// SWIM represents the SWIM gossip protocol implementation
type SWIM struct {
	self    *Node
	config  Config
	members map[string]*Node
	mu      sync.RWMutex
}

// NewSWIM creates a new SWIM instance
func NewSWIM(self *Node, config Config) *SWIM {
	return &SWIM{
		self:    self,
		config:  config,
		members: make(map[string]*Node),
	}
}

// AddMember adds a new member to the cluster
func (s *SWIM) AddMember(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.members[node.ID] = node
}

// GetMembers returns all members in the cluster
func (s *SWIM) GetMembers() map[string]*Node {
	s.mu.RLock()
	defer s.mu.RUnlock()
	members := make(map[string]*Node)
	for k, v := range s.members {
		members[k] = v
	}
	return members
}

// getMembersCopy returns a copy of the members map
func (s *SWIM) getMembersCopy() map[string]*Node {
	s.mu.RLock()
	defer s.mu.RUnlock()
	members := make(map[string]*Node)
	for k, v := range s.members {
		members[k] = v
	}
	return members
}

// handleMessage processes incoming messages
func (s *SWIM) handleMessage(msg Message) {
	s.mu.Lock()
	defer s.mu.Unlock()

	switch msg.Type {
	case PingMessage:
		// Add or update the sender in the membership list
		s.members[msg.Sender.ID] = msg.Sender
	case GossipMessage:
		// Update membership list with gossip information
		for id, node := range msg.Members {
			s.members[id] = node
		}
	}
}

// handleGossip processes gossip messages
func (s *SWIM) handleGossip(msg Message) {
	s.handleMessage(msg)
}

// processMessages processes messages in the context
func (s *SWIM) processMessages(ctx context.Context) {
	// This would be implemented for actual message processing
}
