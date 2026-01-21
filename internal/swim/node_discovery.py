"""
Node Discovery module for SWIM gossip protocol.
"""

class NodeDiscovery:
    """
    Handles node discovery in a SWIM gossip network.
    """

    def discover_nodes(self, input_data):
        """
        Discover a single node.

        Args:
            input_data: Dictionary containing node information

        Returns:
            Dictionary with discovered flag added
        """
        if not isinstance(input_data, dict):
            raise ValueError("input_data must be a dictionary")

        result = input_data.copy()
        result['discovered'] = True
        return result

    def batch_discover(self, input_data_list):
        """
        Discover multiple nodes in batch.

        Args:
            input_data_list: List of dictionaries containing node information

        Returns:
            List of dictionaries with discovered flag added
        """
        if not isinstance(input_data_list, list):
            raise ValueError("input_data_list must be a list")

        return [self.discover_nodes(data) for data in input_data_list]
