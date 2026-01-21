"""
SWIM Gossip Provider for Node Discovery

This module implements the SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
for node discovery and failure detection in distributed systems.
"""

from typing import Dict, List, Optional, Set, Tuple
import random
import time
import threading
import json
import socket
import struct
from dataclasses import dataclass, field
from enum import Enum, auto

class NodeStatus(Enum):
    """Node status enumeration"""
    ALIVE = auto()
    SUSPECT = auto()
    FAILED = auto()

@dataclass
class Node:
    """Represents a node in the cluster"""
    id: str
    address: str
    port: int
    status: NodeStatus = NodeStatus.ALIVE
    incarnation: int = 0
    last_seen: float = field(default_factory=time.time)

    def is_alive(self) -> bool:
        """Check if node is considered alive"""
        return self.status == NodeStatus.ALIVE

    def to_dict(self) -> Dict:
        """Convert node to dictionary for serialization"""
        return {
            'id': self.id,
            'address': self.address,
            'port': self.port,
            'status': self.status.name,
            'incarnation': self.incarnation,
            'last_seen': self.last_seen
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """Create node from dictionary"""
        return cls(
            id=data['id'],
            address=data['address'],
            port=data['port'],
            status=NodeStatus[data['status']],
            incarnation=data['incarnation'],
            last_seen=data['last_seen']
        )

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for node discovery and failure detection

    The SWIM protocol consists of three main components:
    1. Periodic membership probing (ping/pong)
    2. Failure detection (ping-req)
    3. Dissemination of membership changes (gossip)
    """

    def __init__(self, node_id: str, address: str, port: int, seed_nodes: Optional[List[Tuple[str, int]]] = None):
        """
        Initialize SWIM Gossip Provider

        Args:
            node_id: Unique identifier for this node
            address: Network address to bind to
            port: Network port to bind to
            seed_nodes: List of (address, port) tuples for initial cluster members
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.seed_nodes = seed_nodes or []

        # Local node
        self.local_node = Node(node_id, address, port)

        # Membership list
        self.membership: Dict[str, Node] = {}
        self.membership[self.node_id] = self.local_node

        # Configuration
        self.probe_interval = 1.0  # seconds
        self.gossip_interval = 0.5  # seconds
        self.failure_timeout = 3.0  # seconds
        self.suspicion_timeout = 2.0  # seconds

        # Network
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        self.socket.bind((self.address, self.port))

        # State
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # Initialize with seed nodes
        for addr, port in self.seed_nodes:
            if f"{addr}:{port}" != f"{self.address}:{self.port}":
                self.add_node(Node(f"{addr}:{port}", addr, port))

    def add_node(self, node: Node) -> None:
        """Add a node to the membership list"""
        if node.id not in self.membership:
            self.membership[node.id] = node
            print(f"Added node: {node.id}")

    def update_node(self, node: Node) -> None:
        """Update node information"""
        if node.id in self.membership:
            existing = self.membership[node.id]
            if node.incarnation > existing.incarnation:
                self.membership[node.id] = node
                print(f"Updated node: {node.id} (incarnation {node.incarnation})")
            elif node.incarnation == existing.incarnation:
                # Update last_seen if this is a more recent sighting
                if node.last_seen > existing.last_seen:
                    existing.last_seen = node.last_seen

    def remove_node(self, node_id: str) -> None:
        """Remove a node from the membership list"""
        if node_id in self.membership:
            del self.membership[node_id]
            print(f"Removed node: {node_id}")

    def get_random_node(self) -> Optional[Node]:
        """Get a random node from the membership list (excluding self)"""
        candidates = [n for n in self.membership.values() if n.id != self.node_id]
        return random.choice(candidates) if candidates else None

    def get_random_nodes(self, count: int = 3) -> List[Node]:
        """Get a random sample of nodes from the membership list"""
        candidates = [n for n in self.membership.values() if n.id != self.node_id]
        return random.sample(candidates, min(count, len(candidates)))

    def ping(self, node: Node) -> bool:
        """Send a ping message to a node"""
        try:
            message = self._serialize_message({
                'type': 'ping',
                'from': self.local_node.to_dict(),
                'to': node.id
            })
            self.socket.sendto(message, (node.address, node.port))

            # Wait for pong response
            try:
                data, addr = self.socket.recvfrom(1024)
                response = self._deserialize_message(data)
                if response.get('type') == 'pong' and response.get('from') == node.id:
                    return True
            except socket.timeout:
                pass
        except Exception as e:
            print(f"Ping failed: {e}")
        return False

    def ping_req(self, target_node: Node, suspect_node: Node) -> None:
        """Send a ping request to check if other nodes can reach a suspect node"""
        try:
            message = self._serialize_message({
                'type': 'ping_req',
                'from': self.local_node.to_dict(),
                'target': suspect_node.to_dict(),
                'to': target_node.id
            })
            self.socket.sendto(message, (target_node.address, target_node.port))
        except Exception as e:
            print(f"Ping request failed: {e}")

    def gossip(self, target_node: Node) -> None:
        """Send gossip message with membership information"""
        try:
            # Select random nodes to gossip about
            nodes_to_gossip = self.get_random_nodes(3)
            node_dicts = [n.to_dict() for n in nodes_to_gossip]

            message = self._serialize_message({
                'type': 'gossip',
                'from': self.local_node.to_dict(),
                'nodes': node_dicts,
                'to': target_node.id
            })
            self.socket.sendto(message, (target_node.address, target_node.port))
        except Exception as e:
            print(f"Gossip failed: {e}")

    def _serialize_message(self, message: Dict) -> bytes:
        """Serialize message to bytes"""
        return json.dumps(message).encode('utf-8')

    def _deserialize_message(self, data: bytes) -> Dict:
        """Deserialize message from bytes"""
        return json.loads(data.decode('utf-8'))

    def _handle_message(self, message: Dict, sender_addr: Tuple[str, int]) -> None:
        """Handle incoming message"""
        msg_type = message.get('type')
        sender_id = message.get('from', {}).get('id')

        if not msg_type or not sender_id:
            return

        # Update sender in membership list
        sender_node = Node.from_dict(message['from'])
        self.update_node(sender_node)

        if msg_type == 'ping':
            # Respond with pong
            self._send_pong(sender_node)
        elif msg_type == 'pong':
            # Update node status
            if sender_id in self.membership:
                self.membership[sender_id].status = NodeStatus.ALIVE
                self.membership[sender_id].last_seen = time.time()
        elif msg_type == 'ping_req':
            # Handle ping request
            target_node = Node.from_dict(message['target'])
            if self.ping(target_node):
                # Send pong back to requester
                self._send_pong(sender_node)
            else:
                # Mark as suspect
                if target_node.id in self.membership:
                    self.membership[target_node.id].status = NodeStatus.SUSPECT
        elif msg_type == 'gossip':
            # Update membership with gossiped nodes
            for node_dict in message.get('nodes', []):
                node = Node.from_dict(node_dict)
                self.update_node(node)

    def _send_pong(self, target_node: Node) -> None:
        """Send pong response"""
        try:
            message = self._serialize_message({
                'type': 'pong',
                'from': self.local_node.to_dict(),
                'to': target_node.id
            })
            self.socket.sendto(message, (target_node.address, target_node.port))
        except Exception as e:
            print(f"Pong failed: {e}")

    def _probe(self) -> None:
        """Periodic probing of random nodes"""
        while self.running:
            try:
                target = self.get_random_node()
                if target:
                    if not self.ping(target):
                        # Mark as suspect and send ping-req to other nodes
                        target.status = NodeStatus.SUSPECT
                        target.last_seen = time.time()

                        # Send ping-req to other nodes
                        other_nodes = [n for n in self.membership.values()
                                     if n.id != self.node_id and n.id != target.id]
                        for node in other_nodes[:3]:  # Limit to 3 nodes
                            self.ping_req(node, target)
            except Exception as e:
                print(f"Probe error: {e}")

            time.sleep(self.probe_interval)

    def _gossip_loop(self) -> None:
        """Periodic gossip dissemination"""
        while self.running:
            try:
                target = self.get_random_node()
                if target:
                    self.gossip(target)
            except Exception as e:
                print(f"Gossip error: {e}")

            time.sleep(self.gossip_interval)

    def _failure_detection(self) -> None:
        """Check for failed nodes"""
        while self.running:
            try:
                current_time = time.time()
                for node_id, node in list(self.membership.items()):
                    if node.status == NodeStatus.SUSPECT and \
                       current_time - node.last_seen > self.suspicion_timeout:
                        node.status = NodeStatus.FAILED
                    elif node.status == NodeStatus.FAILED and \
                         current_time - node.last_seen > self.failure_timeout:
                        self.remove_node(node_id)
            except Exception as e:
                print(f"Failure detection error: {e}")

            time.sleep(1.0)

    def _listen(self) -> None:
        """Listen for incoming messages"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = self._deserialize_message(data)
                self._handle_message(message, addr)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")

    def start(self) -> None:
        """Start the SWIM gossip provider"""
        if self.running:
            return

        self.running = True

        # Start threads
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

        threading.Thread(target=self._probe, daemon=True).start()
        threading.Thread(target=self._gossip_loop, daemon=True).start()
        threading.Thread(target=self._failure_detection, daemon=True).start()

        print(f"SWIM Gossip Provider started on {self.address}:{self.port}")

    def stop(self) -> None:
        """Stop the SWIM gossip provider"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.socket.close()
        print("SWIM Gossip Provider stopped")

    def get_membership(self) -> Dict[str, Node]:
        """Get current membership list"""
        return self.membership.copy()

    def get_alive_nodes(self) -> List[Node]:
        """Get list of alive nodes"""
        return [n for n in self.membership.values() if n.is_alive()]
