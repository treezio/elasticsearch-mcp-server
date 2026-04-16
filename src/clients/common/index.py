from typing import Dict, Optional

from src.clients.base import SearchClientBase


class IndexClient(SearchClientBase):
    def list_indices(self) -> str:
        """List all indices."""
        response = self.client.cat.indices()
        return self._process_response(response)

    def get_index(self, index: str) -> Dict:
        """Returns information (mappings, settings, aliases) about one or more indices."""
        response = self.client.indices.get(index=index)
        return self._process_response(response)

    def create_index(self, index: str, body: Optional[Dict] = None) -> Dict:
        """Creates an index with optional settings and mappings."""
        response = self.client.indices.create(index=index, body=body)
        return self._process_response(response)

    def delete_index(self, index: str) -> Dict:
        """Delete an index."""
        response = self.client.indices.delete(index=index)
        return self._process_response(response)
