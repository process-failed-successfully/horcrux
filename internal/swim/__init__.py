"""
SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol) implementation.

This module provides gossip-based membership and failure detection for distributed systems.
"""

from .node_discovery import NodeDiscovery
from .gossip import GossipProvider

__all__ = ['NodeDiscovery', 'GossipProvider']
