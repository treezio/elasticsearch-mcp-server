from typing import Dict, Optional
from src.clients.base import SearchClientBase


class DataStreamClient(SearchClientBase):
    def create_data_stream(self, name: str) -> Dict:
        """Create a new data stream."""
        response = self.client.indices.create_data_stream(name=name)
        return self._process_response(response)

    def get_data_stream(self, name: Optional[str] = None) -> Dict:
        """Get information about one or more data streams."""
        if name:
            response = self.client.indices.get_data_stream(name=name)
        else:
            response = self.client.indices.get_data_stream()
        return self._process_response(response)

    def delete_data_stream(self, name: str) -> Dict:
        """Delete one or more data streams."""
        response = self.client.indices.delete_data_stream(name=name)
        return self._process_response(response)
