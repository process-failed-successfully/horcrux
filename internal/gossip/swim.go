package gossip

import (
	"context"
	"sync"
	"time"
)

type Node struct {
	ID      string
	Address string
	Status  string
}

type SWIM struct {
	ctx    context.Context
	cancel context.CancelFunc
	mu     sync.Mutex
	nodes  map[string]*Node
}

func NewSWIM(ctx context.Context) *SWIM {
	if ctx == nil {
		ctx = context.Background()
	}
	ctx, cancel := context.WithCancel(ctx)
	return &SWIM{
		ctx:    ctx,
		cancel: cancel,
		nodes:  make(map[string]*Node),
	}
}

func (s *SWIM) AddNode(node *Node) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.nodes[node.ID] = node
}

func (s *SWIM) GetNodes() []*Node {
	s.mu.Lock()
	defer s.mu.Unlock()
	nodes := make([]*Node, 0, len(s.nodes))
	for _, node := range s.nodes {
		nodes = append(nodes, node)
	}
	return nodes
}

func (s *SWIM) Stop() {
	s.cancel()
}
