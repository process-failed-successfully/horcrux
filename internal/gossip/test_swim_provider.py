import pytest
import time
import threading
from internal.gossip.swim_provider import SWIMGossipProvider, NodeInfo

def test_swim_gossip_init():
    """Test initialization of SWIM Gossip provider."""
    # Step 1: Import the SWIM Gossip provider module
    from internal.gossip.swim_provider import SWIMGossipProvider

    # Step 2: Initialize the provider with default configuration
    provider = SWIMGossipProvider(
        node_id="node1",
        address="127.0.0.1",
        port=8001
    )

    # Step 3: Verify the provider is initialized without errors
    assert provider.node_id == "node1"
    assert provider.address == "127.0.0.1"
    assert provider.port == 8001
    assert provider.gossip_interval == 1.0  # default
    assert provider.running is False
    assert len(provider.get_nodes()) == 1  # should have self
    assert provider.get_node("node1") is not None

    # Step 4: Check that the provider can be stopped gracefully
    # First start it
    provider.start()
    assert provider.running is True

    # Then stop it
    provider.stop()
    assert provider.running is False

def test_swim_gossip_init_with_config():
    """Test initialization with custom configuration."""
    custom_config = {
        "gossip_interval": 2.0,
        "probe_timeout": 0.5,
        "suspicion_timeout": 2.0,
        "max_nodes": 50
    }

    provider = SWIMGossipProvider(
        node_id="node2",
        address="127.0.0.1",
        port=8002,
        config=custom_config
    )

    assert provider.gossip_interval == 2.0
    assert provider.probe_timeout == 0.5
    assert provider.suspicion_timeout == 2.0
    assert provider.max_nodes == 50

def test_swim_gossip_start_stop():
    """Test starting and stopping the provider multiple times."""
    provider = SWIMGossipProvider(
        node_id="node3",
        address="127.0.0.1",
        port=8003
    )

    # Start and stop multiple times
    for _ in range(3):
        provider.start()
        assert provider.running is True
        time.sleep(0.1)  # Let it run briefly

        provider.stop()
        assert provider.running is False

def test_swim_gossip_node_management():
    """Test node management functionality."""
    provider = SWIMGossipProvider(
        node_id="node4",
        address="127.0.0.1",
        port=8004
    )

    # Initially should only have self
    nodes = provider.get_nodes()
    assert len(nodes) == 1
    assert nodes[0].node_id == "node4"

    # Add another node (simulating discovery)
    provider._update_node("node5", "127.0.0.1", 8005, "alive")
    nodes = provider.get_nodes()
    assert len(nodes) == 2

    # Verify we can get specific node
    node5 = provider.get_node("node5")
    assert node5 is not None
    assert node5.node_id == "node5"
    assert node5.status == "alive"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
