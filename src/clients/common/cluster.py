from typing import Dict

from src.clients.base import SearchClientBase


class ClusterClient(SearchClientBase):
    def get_cluster_health(self) -> Dict:
        """Get cluster health information from OpenSearch."""
        response = self.client.cluster.health()
        return self._process_response(response)

    def get_cluster_stats(self) -> Dict:
        """Get cluster statistics from OpenSearch."""
        response = self.client.cluster.stats()
        return self._process_response(response)
