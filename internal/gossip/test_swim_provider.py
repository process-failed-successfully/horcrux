import pytest
import time
from internal.gossip.swim_provider import SWIMGossipProvider
from internal.gossip.types import Node

def test_swim_gossip_init():
    """Test SWIM Gossip provider initialization."""
    # Step 1: Import the SWIM Gossip provider module
    from internal.gossip.swim_provider import SWIMGossipProvider

    # Step 2: Initialize the provider with default configuration
    provider = SWIMGossipProvider(
        node_id="node1",
        host="127.0.0.1",
        port=8080
    )

    # Step 3: Verify the provider is initialized without errors
    assert provider.node_id == "node1"
    assert provider.host == "127.0.0.1"
    assert provider.port == 8080
    assert provider.gossip_interval == 1.0  # Default value
    assert provider.failure_timeout == 3.0  # Default value
    assert provider.probe_timeout == 1.0  # Default value

    # Check that self is in members
    members = provider.get_members()
    assert len(members) == 1
    assert members[0].id == "node1"

    # Step 4: Check that the provider can be stopped gracefully
    provider.start()
    assert provider.is_running()

    provider.stop()
    assert not provider.is_running()

def test_swim_gossip_init_with_config():
    """Test SWIM Gossip provider initialization with custom config."""
    config = {
        "gossip_interval": 2.0,
        "failure_timeout": 5.0,
        "probe_timeout": 2.0
    }

    provider = SWIMGossipProvider(
        node_id="node2",
        host="127.0.0.1",
        port=8081,
        config=config
    )

    assert provider.gossip_interval == 2.0
    assert provider.failure_timeout == 5.0
    assert provider.probe_timeout == 2.0

if __name__ == "__main__":
    test_swim_gossip_init()
    test_swim_gossip_init_with_config()
    print("All tests passed!")
