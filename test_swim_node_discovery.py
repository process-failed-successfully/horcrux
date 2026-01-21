import unittest
import subprocess
import time
import json
import os

class TestSWIMNodeDiscovery(unittest.TestCase):
    """Test SWIM node discovery functionality"""

    def setUp(self):
        """Set up test environment"""
        # Ensure we have the Go implementation
        self.go_file = "internal/swim/swim.go"
        self.assertTrue(os.path.exists(self.go_file), f"SWIM implementation not found at {self.go_file}")

    def test_swim_implementation_exists(self):
        """Verify that the SWIM implementation file exists and has basic structure"""
        with open(self.go_file, 'r') as f:
            content = f.read()

        # Check for key components
        self.assertIn("type Node struct", content)
        self.assertIn("type SWIM struct", content)
        self.assertIn("func NewSWIM", content)
        self.assertIn("func (s *SWIM) AddMember", content)
        self.assertIn("func (s *SWIM) GetMembers", content)
        self.assertIn("func (s *SWIM) Start", content)

    def test_node_structure(self):
        """Verify Node structure has required fields"""
        with open(self.go_file, 'r') as f:
            content = f.read()

        # Check for required fields in Node struct
        self.assertIn("ID      string", content)
        self.assertIn("Address string", content)
        self.assertIn("Status  string", content)
        self.assertIn("LastSeen time.Time", content)

    def test_swim_structure(self):
        """Verify SWIM structure has required components"""
        with open(self.go_file, 'r') as f:
            content = f.read()

        # Check for required components in SWIM struct
        self.assertIn("self          *Node", content)
        self.assertIn("members       map[string]*Node", content)
        self.assertIn("config        Config", content)

    def test_config_structure(self):
        """Verify Config structure has required fields"""
        with open(self.go_file, 'r') as f:
            content = f.read()

        # Check for required config fields
        self.assertIn("GossipInterval    time.Duration", content)
        self.assertIn("PingTimeout       time.Duration", content)
        self.assertIn("FailureThreshold  int", content)

    def test_basic_functionality(self):
        """Test basic SWIM functionality through a simple Go test"""
        # Create a simple Go test file
        test_content = '''
package swim

import (
	"testing"
	"time"
)

func TestNewSWIM(t *testing.T) {
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

	if swim == nil {
		t.Fatal("NewSWIM returned nil")
	}

	if swim.self.ID != "node1" {
		t.Errorf("Expected self.ID to be 'node1', got %s", swim.self.ID)
	}
}

func TestAddMember(t *testing.T) {
	swim := NewSWIM(&Node{ID: "node1"}, Config{})

	node2 := &Node{
		ID:      "node2",
		Address: "127.0.0.1:8081",
		Status:  "alive",
	}

	swim.AddMember(node2)

	members := swim.GetMembers()
	if len(members) != 1 {
		t.Errorf("Expected 1 member, got %d", len(members))
	}

	if _, ok := members["node2"]; !ok {
		t.Error("node2 not found in members")
	}
}

func TestGetMembers(t *testing.T) {
	swim := NewSWIM(&Node{ID: "node1"}, Config{})

	node2 := &Node{ID: "node2", Address: "127.0.0.1:8081"}
	node3 := &Node{ID: "node3", Address: "127.0.0.1:8082"}

	swim.AddMember(node2)
	swim.AddMember(node3)

	members := swim.GetMembers()
	if len(members) != 2 {
		t.Errorf("Expected 2 members, got %d", len(members))
	}
}
'''

        # Write the test file
        with open("internal/swim/swim_test.go", "w") as f:
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
