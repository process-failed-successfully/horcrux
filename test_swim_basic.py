import pytest
import time
import threading
from internal.swim import SWIMGossipProvider, Node, NodeStatus

def test_node_creation():
    """Test basic node creation"""
    node = Node("node1", "127.0.0.1", 8000)
    assert node.id == "node1"
    assert node.address == "127.0.0.1"
    assert node.port == 8000
    assert node.status == NodeStatus.ALIVE
    assert node.is_alive()

def test_node_serialization():
    """Test node serialization/deserialization"""
    node = Node("node1", "127.0.0.1", 8000, NodeStatus.SUSPECT, 1, 123.45)
    node_dict = node.to_dict()
    assert node_dict['id'] == "node1"
    assert node_dict['status'] == "SUSPECT"

    restored = Node.from_dict(node_dict)
    assert restored.id == node.id
    assert restored.status == node.status
    assert restored.incarnation == node.incarnation

def test_swim_initialization():
    """Test SWIM provider initialization"""
    provider = SWIMGossipProvider("node1", "127.0.0.1", 8001)
    assert provider.node_id == "node1"
    assert provider.address == "127.0.0.1"
    assert provider.port == 8001
    assert len(provider.get_membership()) == 1
    assert provider.local_node.id == "node1"

def test_swim_with_seed_nodes():
    """Test SWIM provider with seed nodes"""
    seed_nodes = [("127.0.0.1", 8002), ("127.0.0.1", 8003)]
    provider = SWIMGossipProvider("node1", "127.0.0.1", 8001, seed_nodes)
    membership = provider.get_membership()
    assert len(membership) == 3  # self + 2 seed nodes

def test_node_management():
    """Test adding and updating nodes"""
    provider = SWIMGossipProvider("node1", "127.0.0.1", 8001)

    # Add a node
    node2 = Node("node2", "127.0.0.1", 8002)
    provider.add_node(node2)
    assert len(provider.get_membership()) == 2

    # Update the node
    updated_node2 = Node("node2", "127.0.0.1", 8002, NodeStatus.SUSPECT, 1)
    provider.update_node(updated_node2)
    assert provider.get_membership()["node2"].status == NodeStatus.SUSPECT

    # Remove the node
    provider.remove_node("node2")
    assert len(provider.get_membership()) == 1

def test_start_stop():
    """Test starting and stopping the provider"""
    provider = SWIMGossipProvider("node1", "127.0.0.1", 8001)
    provider.start()
    assert provider.running

    # Give it a moment to start threads
    time.sleep(0.1)

    provider.stop()
    assert not provider.running

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
