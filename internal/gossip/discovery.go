package gossip

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

// DiscoveryConfig holds configuration for node discovery
type DiscoveryConfig struct {
	// SeedNodes are the initial nodes to connect to for bootstrap
	SeedNodes []string
	// DiscoveryPort is the port to use for discovery
	DiscoveryPort int
	// DiscoveryInterval is how often to perform discovery
	DiscoveryInterval time.Duration
}

// DiscoveryService handles node discovery
type DiscoveryService struct {
	swim       *SWIM
	config     DiscoveryConfig
	httpServer *http.Server
	mu         sync.RWMutex
	peers      map[string]bool
}

// NewDiscoveryService creates a new discovery service
func NewDiscoveryService(swim *SWIM, config DiscoveryConfig) *DiscoveryService {
	if config.DiscoveryInterval == 0 {
		config.DiscoveryInterval = 5 * time.Second
	}
	if config.DiscoveryPort == 0 {
		config.DiscoveryPort = 8080
	}

	return &DiscoveryService{
		swim:   swim,
		config: config,
		peers:  make(map[string]bool),
	}
}

// Start starts the discovery service
func (d *DiscoveryService) Start() error {
	// Start HTTP server for discovery
	mux := http.NewServeMux()
	mux.HandleFunc("/discover", d.handleDiscovery)
	mux.HandleFunc("/nodes", d.handleNodesRequest)

	addr := fmt.Sprintf(":%d", d.config.DiscoveryPort)
	server := &http.Server{
		Addr:    addr,
		Handler: mux,
	}

	d.httpServer = server

	// Start server in goroutine
	go func() {
		log.Printf("Starting discovery server on %s", addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("Discovery server error: %v", err)
		}
	}()

	// Start discovery loop
	go d.discoveryLoop()

	// Connect to seed nodes
	go d.connectToSeedNodes()

	return nil
}

// Stop stops the discovery service
func (d *DiscoveryService) Stop() error {
	if d.httpServer != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		return d.httpServer.Shutdown(ctx)
	}
	return nil
}

// discoveryLoop periodically discovers new nodes
func (d *DiscoveryService) discoveryLoop() {
	ticker := time.NewTicker(d.config.DiscoveryInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			d.discoverNodes()
		case <-d.swim.ctx.Done():
			return
		}
	}
}

// connectToSeedNodes connects to the seed nodes
func (d *DiscoveryService) connectToSeedNodes() {
	for _, seed := range d.config.SeedNodes {
		go d.discoverFromSeed(seed)
	}
}

// discoverFromSeed discovers nodes from a seed node
func (d *DiscoveryService) discoverFromSeed(seed string) {
	url := fmt.Sprintf("http://%s/nodes", seed)
	resp, err := http.Get(url)
	if err != nil {
		log.Printf("Failed to discover from seed %s: %v", seed, err)
		return
	}
	defer resp.Body.Close()

	var nodes []*Node
	if err := json.NewDecoder(resp.Body).Decode(&nodes); err != nil {
		log.Printf("Failed to decode nodes from seed %s: %v", seed, err)
		return
	}

	for _, node := range nodes {
		d.addDiscoveredNode(node)
	}
}

// discoverNodes discovers new nodes in the network
func (d *DiscoveryService) discoverNodes() {
	// Get current nodes
	nodes := d.swim.GetNodes()

	// For each node, try to discover more nodes
	for _, node := range nodes {
		if node.ID == d.swim.config.NodeID {
			continue // Skip self
		}
		go d.discoverFromNode(node)
	}
}

// discoverFromNode discovers nodes from a specific node
func (d *DiscoveryService) discoverFromNode(node *Node) {
	url := fmt.Sprintf("http://%s/nodes", node.Address)
	resp, err := http.Get(url)
	if err != nil {
		log.Printf("Failed to discover from node %s: %v", node.ID, err)
		return
	}
	defer resp.Body.Close()

	var discoveredNodes []*Node
	if err := json.NewDecoder(resp.Body).Decode(&discoveredNodes); err != nil {
		log.Printf("Failed to decode nodes from node %s: %v", node.ID, err)
		return
	}

	for _, discoveredNode := range discoveredNodes {
		d.addDiscoveredNode(discoveredNode)
	}
}

// addDiscoveredNode adds a discovered node to the cluster
func (d *DiscoveryService) addDiscoveredNode(node *Node) {
	d.mu.Lock()
	defer d.mu.Unlock()

	// Check if we already know about this node
	if _, exists := d.peers[node.ID]; exists {
		return
	}

	// Add to peers
	d.peers[node.ID] = true

	// Add to SWIM
	d.swim.AddNode(node)
	log.Printf("Discovered new node: %s at %s", node.ID, node.Address)
}

// handleDiscovery handles discovery requests from other nodes
func (d *DiscoveryService) handleDiscovery(w http.ResponseWriter, r *http.Request) {
	// Return information about this node
	node := &Node{
		ID:      d.swim.config.NodeID,
		Address: d.swim.config.AdvertiseAddr,
		State:   NodeAlive,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(node)
}

// handleNodesRequest handles requests for the list of known nodes
func (d *DiscoveryService) handleNodesRequest(w http.ResponseWriter, r *http.Request) {
	nodes := d.swim.GetNodes()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(nodes)
}
