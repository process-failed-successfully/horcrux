
package swim

import (
	"testing"
	"time"
)

func TestGossipPropagation(t *testing.T) {
	// Create a SWIM instance
	self := &Node{
		ID:      "node1",
		Address: "127.0.0.1:8080",
		Status:  "alive",
	}

	config := Config{
		GossipInterval:   100 * time.Millisecond,
		PingTimeout:      50 * time.Millisecond,
		FailureThreshold: 3,
	}

	swim := NewSWIM(self, config)

	// Add some members
	node2 := &Node{ID: "node2", Address: "127.0.0.1:8081", Status: "alive"}
	node3 := &Node{ID: "node3", Address: "127.0.0.1:8082", Status: "alive"}

	swim.AddMember(node2)
	swim.AddMember(node3)

	// Create a gossip message
	gossipMsg := Message{
		Type:    GossipMessage,
		Sender:  self,
		Members: swim.getMembersCopy(),
	}

	// Handle the gossip message
	swim.handleGossip(gossipMsg)

	// Verify members were updated
	members := swim.GetMembers()
	if len(members) != 2 {
		t.Errorf("Expected 2 members after gossip, got %d", len(members))
	}

	// Verify the gossip message contains the expected members
	if len(gossipMsg.Members) != 2 {
		t.Errorf("Expected gossip message to contain 2 members, got %d", len(gossipMsg.Members))
	}
}

func TestMessageHandling(t *testing.T) {
	swim := NewSWIM(&Node{ID: "node1"}, Config{})

	// Test ping message handling
	pingMsg := Message{
		Type:   PingMessage,
		Sender: &Node{ID: "node2", Address: "127.0.0.1:8081"},
	}

	swim.handleMessage(pingMsg)

	// Verify the sender was added to members
	members := swim.GetMembers()
	if _, ok := members["node2"]; !ok {
		t.Error("Expected node2 to be added after ping message")
	}
}
