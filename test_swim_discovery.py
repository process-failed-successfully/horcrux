#!/usr/bin/env python3
"""
Integration tests for SWIM node discovery.
"""

import asyncio
import time
from internal.gossip.swim_gossip import SWIMGossipProvider

async def test_node_discovery_basic():
    """Test basic node discovery between two nodes"""
    # Create two nodes
    node1 = SWIMGossipProvider("node1", "127.0.0.1", 9001)
    node2 = SWIMGossipProvider("node2", "127.0.0.1", 9002, [("127.0.0.1", 9001)])

    # Start both nodes
    await node1.start()
    await node2.start()

    # Give them time to discover each other
    await asyncio.sleep(2)

    # Check membership
    membership1 = node1.get_membership()
    membership2 = node2.get_membership()

    print(f"Node1 membership: {[n.id for n in membership1.values()]}")
    print(f"Node2 membership: {[n.id for n in membership2.values()]}")

    # Cleanup
    await node1.stop()
    await node2.stop()

    # Verify both nodes discovered each other
    assert len(membership1) >= 2  # At least self and node2
    assert len(membership2) >= 2  # At least self and node1

async def test_three_node_cluster():
    """Test node discovery in a three-node cluster"""
    # Create three nodes with seed configuration
    node1 = SWIMGossipProvider("node1", "127.0.0.1", 9011)
    node2 = SWIMGossipProvider("node2", "127.0.0.1", 9012, [("127.0.0.1", 9011)])
    node3 = SWIMGossipProvider("node3", "127.0.0.1", 9013, [("127.0.0.1", 9011)])

    # Start all nodes
    await node1.start()
    await node2.start()
    await node3.start()

    # Give them time to discover each other
    await asyncio.sleep(3)

    # Check membership
    membership1 = node1.get_membership()
    membership2 = node2.get_membership()
    membership3 = node3.get_membership()

    print(f"Node1 membership: {[n.id for n in membership1.values()]}")
    print(f"Node2 membership: {[n.id for n in membership2.values()]}")
    print(f"Node3 membership: {[n.id for n in membership3.values()]}")

    # Cleanup
    await node1.stop()
    await node2.stop()
    await node3.stop()

    # Verify all nodes discovered each other
    assert len(membership1) >= 3
    assert len(membership2) >= 3
    assert len(membership3) >= 3

if __name__ == "__main__":
    asyncio.run(test_node_discovery_basic())
    asyncio.run(test_three_node_cluster())
    print("All tests passed!")
