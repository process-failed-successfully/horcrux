
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
