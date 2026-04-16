from typing import Dict

from src.clients.base import SearchClientBase


class AliasClient(SearchClientBase):
    def list_aliases(self) -> str:
        """Get all aliases."""
        response = self.client.cat.aliases()
        return self._process_response(response)

    def get_alias(self, index: str) -> Dict:
        """Get aliases for the specified index."""
        response = self.client.indices.get_alias(index=index)
        return self._process_response(response)

    def put_alias(self, index: str, name: str, body: Dict) -> Dict:
        """Creates or updates an alias."""
        response = self.client.indices.put_alias(index=index, name=name, body=body)
        return self._process_response(response)

    def delete_alias(self, index: str, name: str) -> Dict:
        """Delete an alias for the specified index."""
        response = self.client.indices.delete_alias(index=index, name=name)
        return self._process_response(response)
