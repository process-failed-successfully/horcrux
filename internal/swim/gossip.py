"""
Gossip Protocol implementation for SWIM.
"""

import random
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

@dataclass
class GossipMessage:
    """Represents a gossip message."""
    message_id: str
    sender_id: str
    content: Dict[str, Any]
    timestamp: float
    ttl: int = 5  # Time-to-live (number of hops)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "ttl": self.ttl
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GossipMessage':
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            content=data["content"],
            timestamp=data["timestamp"],
            ttl=data.get("ttl", 5)
        )

class GossipProtocol:
    """
    Gossip Protocol for message propagation in SWIM.
    """

    def __init__(self, node_id: str, node_discovery: 'NodeDiscovery'):
        """
        Initialize gossip protocol.

        Args:
            node_id: ID of the local node
            node_discovery: NodeDiscovery instance for cluster membership
        """
        self.node_id = node_id
        self.node_discovery = node_discovery
        self.message_store: Dict[str, GossipMessage] = {}
        self.message_queue: List[GossipMessage] = []
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Configuration
        self.gossip_interval = 0.5  # seconds
        self.max_queue_size = 100

    def start(self) -> None:
        """Start the gossip protocol."""
        if self.running:
            return

        self.running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()

    def stop(self) -> None:
        """Stop the gossip protocol."""
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join()

    def _gossip_loop(self) -> None:
        """Main gossip loop for message propagation."""
        while self.running:
            try:
                self._process_queue()
                self._propagate_messages()
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Gossip protocol error: {e}")
                time.sleep(1)

    def _process_queue(self) -> None:
        """Process incoming messages from the queue."""
        with self.lock:
            while self.message_queue:
                message = self.message_queue.pop(0)
                self._handle_message(message)

    def _propagate_messages(self) -> None:
        """Propagate messages to other nodes."""
        with self.lock:
            if not self.message_store:
                return

            # Get alive members to gossip with
            members = self.node_discovery.get_alive_members()
            if not members:
                return

            # Select a random subset of members to gossip with
            targets = random.sample(members, min(3, len(members)))

            # Select messages to propagate (avoid sending too many at once)
            messages_to_send = list(self.message_store.values())[:5]

            for target in targets:
                if target.node_id == self.node_id:
                    continue

                try:
                    self._send_messages(target, messages_to_send)
                except Exception as e:
                    print(f"Failed to send gossip to {target.node_id}: {e}")

    def _send_messages(self, target: 'Node', messages: List[GossipMessage]) -> None:
        """
        Send messages to a target node.

        Args:
            target: Target node
            messages: List of messages to send
        """
        # Simulate network communication
        # In a real implementation, this would use actual network calls
        try:
            # Simulate network delay
            time.sleep(0.05)

            # Simulate 5% chance of message loss
            if random.random() < 0.05:
                return

            # Process messages on the target node
            for message in messages:
                # Decrement TTL
                message.ttl -= 1

                if message.ttl > 0:
                    # Add to target's queue
                    # In real implementation, this would be sent over network
                    pass

        except Exception as e:
            print(f"Message send error: {e}")

    def _handle_message(self, message: GossipMessage) -> None:
        """
        Handle an incoming gossip message.

        Args:
            message: Incoming gossip message
        """
        with self.lock:
            # Check if we've already seen this message
            if message.message_id in self.message_store:
                return

            # Store the message
            self.message_store[message.message_id] = message

            # Process the message content
            self._process_message_content(message)

    def _process_message_content(self, message: GossipMessage) -> None:
        """
        Process the content of a gossip message.

        Args:
            message: Gossip message to process
        """
        # This would be overridden by specific implementations
        pass

    def inject_message(self, content: Dict[str, Any]) -> GossipMessage:
        """
        Inject a new gossip message into the system.

        Args:
            content: Message content

        Returns:
            Created gossip message
        """
        message_id = f"{self.node_id}-{time.time()}-{random.randint(0, 10000)}"
        message = GossipMessage(
            message_id=message_id,
            sender_id=self.node_id,
            content=content,
            timestamp=time.time(),
            ttl=5
        )

        with self.lock:
            self.message_store[message_id] = message
            self.message_queue.append(message)

        return message

    def get_message(self, message_id: str) -> Optional[GossipMessage]:
        """
        Get a message by ID.

        Args:
            message_id: Message ID

        Returns:
            GossipMessage if found, None otherwise
        """
        with self.lock:
            return self.message_store.get(message_id)

    def get_all_messages(self) -> List[GossipMessage]:
        """
        Get all stored messages.

        Returns:
            List of all gossip messages
        """
        with self.lock:
            return list(self.message_store.values())
