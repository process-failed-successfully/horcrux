"""
Unit tests for SWIM Gossip Provider.
"""

import asyncio
import pytest
import time
from internal.gossip.swim_provider import SWIMGossipProvider, Node

@pytest.mark.asyncio
async def test_swim_gossip_initialization():
    """Test that the SWIM gossip provider initializes correctly."""
    provider = SWIMGossipProvider(
        node_id="test_node_1",
        address="127.0.0.1",
        port=8001
    )

    assert provider.node_id == "test_node_1"
    assert provider.address == "127.0.0.1"
    assert provider.port == 8001
    assert provider.is_running is False
    assert len(provider.get_membership()) == 1  # Only local node
    assert provider.get_membership()[0].node_id == "test_node_1"

@pytest.mark.asyncio
async def test_swim_gossip_start_stop():
    """Test that the provider can be started and stopped gracefully."""
    provider = SWIMGossipProvider(
        node_id="test_node_2",
        address="127.0.0.1",
        port=8002
    )

    # Test starting
    await provider.start()
    assert provider.is_running is True

    # Test stopping
    await provider.stop()
    assert provider.is_running is False

    # Test double stop
    await provider.stop()  # Should not raise error
    assert provider.is_running is False

@pytest.mark.asyncio
async def test_swim_gossip_with_seed_nodes():
    """Test initialization with seed nodes."""
    seed_nodes = [("192.168.1.1", 8001), ("192.168.1.2", 8002)]
    provider = SWIMGossipProvider(
        node_id="test_node_3",
        address="127.0.0.1",
        port=8003,
        seed_nodes=seed_nodes
    )

    membership = provider.get_membership()
    assert len(membership) == 3  # Local node + 2 seed nodes

    # Check that seed nodes are in membership
    seed_node_ids = {provider._generate_node_id(addr, port) for addr, port in seed_nodes}
    membership_ids = {node.node_id for node in membership}
    assert seed_node_ids.issubset(membership_ids)

@pytest.mark.asyncio
async def test_swim_gossip_gossip_round():
    """Test that gossip rounds execute without errors."""
    provider = SWIMGossipProvider(
        node_id="test_node_4",
        address="127.0.0.1",
        port=8004
    )

    await provider.start()

    # Let it run for a few gossip intervals
    await asyncio.sleep(2.5)

    # Should still be running
    assert provider.is_running is True

    # Should have at least the local node
    assert len(provider.get_membership()) >= 1

    await provider.stop()

@pytest.mark.asyncio
async def test_swim_gossip_node_management():
    """Test node management functionality."""
    provider = SWIMGossipProvider(
        node_id="test_node_5",
        address="127.0.0.1",
        port=8005
    )

    # Add a node manually
    new_node = Node(
        node_id="manual_node_1",
        address="192.168.1.10",
        port=9000
    )
    provider.membership[new_node.node_id] = new_node

    # Check membership
    membership = provider.get_membership()
    assert len(membership) == 2
    assert any(node.node_id == "manual_node_1" for node in membership)

    # Mark node as failed
    provider.membership[new_node.node_id].is_alive = False
    failed_nodes = provider.get_failed_nodes()
    assert len(failed_nodes) == 1
    assert failed_nodes[0].node_id == "manual_node_1"

    # Check alive nodes
    alive_nodes = provider.get_alive_nodes()
    assert len(alive_nodes) == 1
    assert alive_nodes[0].node_id == "test_node_5"

def test_node_serialization():
    """Test node serialization and deserialization."""
    node = Node(
        node_id="test_node",
        address="127.0.0.1",
        port=8000,
        last_seen=12345.67,
        is_alive=True,
        incarnation=5
    )

    # Test to_dict
    node_dict = node.to_dict()
    assert node_dict['node_id'] == "test_node"
    assert node_dict['address'] == "127.0.0.1"
    assert node_dict['port'] == 8000
    assert node_dict['last_seen'] == 12345.67
    assert node_dict['is_alive'] is True
    assert node_dict['incarnation'] == 5

    # Test from_dict
    new_node = Node.from_dict(node_dict)
    assert new_node.node_id == node.node_id
    assert new_node.address == node.address
    assert new_node.port == node.port
    assert new_node.last_seen == node.last_seen
    assert new_node.is_alive == node.is_alive
    assert new_node.incarnation == node.incarnation

@pytest.mark.asyncio
async def test_swim_gossip_configuration():
    """Test custom configuration parameters."""
    provider = SWIMGossipProvider(
        node_id="test_node_6",
        address="127.0.0.1",
        port=8006,
        gossip_interval=0.5,
        ping_timeout=0.2,
        ping_req_timeout=0.1,
        failure_threshold=2
    )

    assert provider.gossip_interval == 0.5
    assert provider.ping_timeout == 0.2
    assert provider.ping_req_timeout == 0.1
    assert provider.failure_threshold == 2

    await provider.start()
    assert provider.is_running is True
    await provider.stop()
