import unittest
import subprocess
import time
import json
import os

class TestSWIMGossipPropagation(unittest.TestCase):
    """Test SWIM gossip propagation functionality"""

    def setUp(self):
        """Set up test environment"""
        # Ensure we have the Go implementation
        self.go_file = "internal/swim/swim.go"
        self.assertTrue(os.path.exists(self.go_file), f"SWIM implementation not found at {self.go_file}")

    def test_gossip_message_structure(self):
        """Verify that gossip message structure exists"""
        with open(self.go_file, 'r') as f:
            content = f.read()

        # Check for message types and structure
        self.assertIn("type MessageType string", content)
        self.assertIn("PingMessage     MessageType = \"ping\"", content)
        self.assertIn("GossipMessage   MessageType = \"gossip\"", content)
        self.assertIn("type Message struct", content)
        self.assertIn("Members   map[string]*Node", content)

    def test_gossip_handling(self):
        """Verify that gossip handling functions exist"""
        with open(self.go_file, 'r') as f:
            content = f.read()

        # Check for gossip handling functions
        self.assertIn("func (s *SWIM) handleGossip(msg Message)", content)
        self.assertIn("func (s *SWIM) processMessages(ctx context.Context)", content)
        self.assertIn("func (s *SWIM) handleMessage(msg Message)", content)

    def test_gossip_propagation_logic(self):
        """Test gossip propagation through Go tests"""
        # Create a Go test for gossip propagation
        test_content = '''
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
'''

        # Write the test file
        with open("internal/swim/gossip_test.go", "w") as f:
            f.write(test_content)

        # Run the Go tests
        result = subprocess.run(
            ["go", "test", "-v", "./internal/swim/"],
            capture_output=True,
            text=True
        )

        # Check if tests passed
        if result.returncode != 0:
            print("Go test output:", result.stdout)
            print("Go test errors:", result.stderr)
            self.fail(f"Go tests failed with return code {result.returncode}")

if __name__ == "__main__":
    unittest.main()
