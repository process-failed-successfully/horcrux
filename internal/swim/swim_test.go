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

	if len(swim.members) != 1 {
		t.Errorf("Expected 1 member (self), got %d", len(swim.members))
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
	if len(members) != 2 {
		t.Errorf("Expected 2 members (self + node2), got %d", len(members))
	}

	if _, ok := members["node2"]; !ok {
		t.Error("node2 not found in members")
	}
}

func TestRemoveMember(t *testing.T) {
	swim := NewSWIM(&Node{ID: "node1"}, Config{})

	node2 := &Node{
		ID:      "node2",
		Address: "127.0.0.1:8081",
		Status:  "alive",
	}

	swim.AddMember(node2)

	// Remove node2
	swim.RemoveMember("node2")

	members := swim.GetMembers()
	if len(members) != 1 {
		t.Errorf("Expected 1 member after removal, got %d", len(members))
	}

	if _, ok := members["node2"]; ok {
		t.Error("node2 should have been removed")
	}
}

func TestGetAliveMembers(t *testing.T) {
	swim := NewSWIM(&Node{ID: "node1", Status: "alive"}, Config{})

	node2 := &Node{
		ID:      "node2",
		Address: "127.0.0.1:8081",
		Status:  "alive",
	}

	node3 := &Node{
		ID:      "node3",
		Address: "127.0.0.1:8082",
		Status:  "failed",
	}

	swim.AddMember(node2)
	swim.AddMember(node3)

	alive := swim.GetAliveMembers()
	if len(alive) != 2 {
		t.Errorf("Expected 2 alive members, got %d", len(alive))
	}

	for _, member := range alive {
		if member.Status != "alive" {
			t.Errorf("Expected member %s to be alive, got %s", member.ID, member.Status)
		}
	}
}

func TestStartStop(t *testing.T) {
	swim := NewSWIM(&Node{ID: "node1"}, Config{
		GossipInterval: 100 * time.Millisecond,
	})

	// Test start
	swim.Start()
	if !swim.running {
		t.Error("SWIM should be running after Start()")
	}

	// Test stop
	swim.Stop()
	if swim.running {
		t.Error("SWIM should not be running after Stop()")
	}
}
