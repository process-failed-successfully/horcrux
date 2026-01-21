package gossip

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"
	"time"
)

// DiscoveryConfig holds configuration for the discovery service
type DiscoveryConfig struct {
	SeedNodes    []string
	BindAddr     string
	Interval     time.Duration
}

// DiscoveryService handles node discovery
type DiscoveryService struct {
	swim    *SWIM
	config  DiscoveryConfig
	server  *http.Server
	mu      sync.Mutex
	running bool
}

// NewDiscoveryService creates a new discovery service
func NewDiscoveryService(swim *SWIM, config DiscoveryConfig) *DiscoveryService {
	if config.Interval == 0 {
		config.Interval = 5 * time.Second
	}
	if config.BindAddr == "" {
		config.BindAddr = ":8080"
	}

	return &DiscoveryService{
		swim:   swim,
		config: config,
	}
}

// Start starts the discovery service
func (d *DiscoveryService) Start() error {
	d.mu.Lock()
	defer d.mu.Unlock()

	if d.running {
		return nil
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/nodes", d.handleNodesRequest)

	d.server = &http.Server{
		Addr:    d.config.BindAddr,
		Handler: mux,
	}

	go func() {
		log.Printf("Starting discovery server on %s", d.config.BindAddr)
		if err := d.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("Discovery server error: %v", err)
		}
	}()

	d.running = true
	return nil
}

// Stop stops the discovery service
func (d *DiscoveryService) Stop() error {
	d.mu.Lock()
	defer d.mu.Unlock()

	if !d.running {
		return nil
	}

	if d.server != nil {
		if err := d.server.Close(); err != nil {
			return err
		}
	}

	d.running = false
	return nil
}

// handleNodesRequest handles requests for the list of nodes
func (d *DiscoveryService) handleNodesRequest(w http.ResponseWriter, r *http.Request) {
	nodes := d.swim.GetNodes()
	response, err := json.Marshal(nodes)
	if err != nil {
		http.Error(w, "Failed to marshal nodes", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(response)
}

// DiscoverFromSeeds discovers nodes from seed nodes
func (d *DiscoveryService) DiscoverFromSeeds() {
	for _, seed := range d.config.SeedNodes {
		go func(seedAddr string) {
			for {
				select {
				case <-d.swim.ctx.Done():
					return
				default:
					nodes, err := d.discoverFromSeed(seedAddr)
					if err != nil {
						log.Printf("Failed to discover from seed %s: %v", seedAddr, err)
					} else {
						for _, node := range nodes {
							d.swim.AddNode(node)
						}
					}
					time.Sleep(d.config.Interval)
				}
			}
		}(seed)
	}
}

// discoverFromSeed discovers nodes from a single seed node
func (d *DiscoveryService) discoverFromSeed(seedAddr string) ([]*Node, error) {
	resp, err := http.Get("http://" + seedAddr + "/nodes")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, nil
	}

	var nodes []*Node
	if err := json.NewDecoder(resp.Body).Decode(&nodes); err != nil {
		return nil, err
	}

	return nodes, nil
}
