"""
SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol) Module

This module provides implementations for distributed node discovery and failure detection
using the SWIM gossip protocol.
"""

from .node_discovery import NodeDiscovery

__all__ = ['NodeDiscovery']
