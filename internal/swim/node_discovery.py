"""
Node Discovery Module for SWIM Gossip Protocol

This module implements node discovery functionality for the SWIM gossip protocol,
which is used for distributed node discovery and failure detection.
"""

class NodeDiscovery:
    """
    A class that handles node discovery in a SWIM gossip protocol cluster.

    The SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    is used for distributed node discovery and failure detection.
    """

    def discover_nodes(self, input_data):
        """
        Discover nodes in the cluster.

        Args:
            input_data (dict): Input data containing node information

        Returns:
            dict: Input data with discovery status added
        """
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")

        output_data = input_data.copy()
        output_data['discovered'] = True
        return output_data

    def batch_discover(self, input_data_list):
        """
        Discover multiple nodes in batch.

        Args:
            input_data_list (list): List of input data dictionaries

        Returns:
            list: List of output data with discovery status added
        """
        if not isinstance(input_data_list, list):
            raise ValueError("Input data must be a list")

        return [self.discover_nodes(data) for data in input_data_list]
