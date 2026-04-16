"""
Authentication middleware for MCP server.

Provides Bearer Token authentication for HTTP-based transports (SSE, Streamable HTTP).
"""

import logging
import os
import secrets
from typing import Optional

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError


logger = logging.getLogger(__name__)


def _get_bearer_token() -> Optional[str]:
    """
    Extract Bearer token from the Authorization header.

    Returns:
        The token if found and properly formatted, None otherwise
    """
    try:
        headers = get_http_headers()
        logger.info(f"Got headers in _get_bearer_token: {headers}")
        if not headers:
            logger.warning("No headers available")
            return None

        auth_header = headers.get("authorization") or headers.get("Authorization")
        logger.info(f"Auth header value: {auth_header}")
        if not auth_header:
            logger.warning("No Authorization header found")
            return None

        # Check for Bearer scheme (case-insensitive per RFC 6750)
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            logger.warning(
                f"Invalid scheme or empty token. Scheme: {scheme}, Token present: {bool(token)}"
            )
            return None

        logger.info(f"Extracted Bearer token (first 5 chars): {token[:5]}...")
        return token.strip()
    except Exception as e:
        logger.error(f"Error getting headers: {e}")
        return None


class BearerAuthMiddleware(Middleware):
    """
    Middleware that validates Bearer token authentication.

    This middleware checks the Authorization header for a valid Bearer token.
    If no token is configured (MCP_API_KEY not set), authentication is disabled.

    Environment Variables:
        MCP_API_KEY: The API key that clients must provide to authenticate.
                     If not set, authentication is disabled.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the middleware.

        Args:
            api_key: The API key to validate against. If None, reads from MCP_API_KEY env var.
        """
        logger.info(
            f"BearerAuthMiddleware initialized with API key: {api_key is not None}"
        )
        self._api_key = api_key

    @property
    def is_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return bool(self._api_key)

    def _validate_token(self, token: str) -> bool:
        """
        Validate the provided token against the configured API key.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            token: The token to validate

        Returns:
            True if valid, False otherwise
        """
        if not self._api_key:
            return True  # No API key configured, allow all
        return secrets.compare_digest(token, self._api_key)

    def _check_auth(self) -> None:
        """
        Check if the request is authenticated.

        Raises:
            ToolError: If authentication fails
        """
        logger.info(
            f"Starting authentication check. API key enabled: {self.is_enabled}"
        )

        if not self.is_enabled:
            logger.warning(
                "Authentication is disabled (no API key configured). Allowing request."
            )
            return

        token = _get_bearer_token()

        if not token:
            logger.warning("Authentication failed: No Bearer token provided")
            raise ToolError(
                "Unauthorized: Missing or invalid Authorization header. "
                "Please provide a valid Bearer token in the Authorization header."
            )

        if not self._validate_token(token):
            logger.warning("Authentication failed: Invalid Bearer token")
            raise ToolError(
                "Unauthorized: Invalid API key. "
                "Please check your MCP_API_KEY configuration."
            )

        logger.info("Authentication successful")

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Authenticate before calling a tool."""
        self._check_auth()
        return await call_next(context)

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Authenticate before listing tools."""
        self._check_auth()
        return await call_next(context)

    async def on_list_resources(self, context: MiddlewareContext, call_next):
        """Authenticate before listing resources."""
        self._check_auth()
        return await call_next(context)

    async def on_read_resource(self, context: MiddlewareContext, call_next):
        """Authenticate before reading a resource."""
        self._check_auth()
        return await call_next(context)

    async def on_list_prompts(self, context: MiddlewareContext, call_next):
        """Authenticate before listing prompts."""
        self._check_auth()
        return await call_next(context)

    async def on_get_prompt(self, context: MiddlewareContext, call_next):
        """Authenticate before getting a prompt."""
        self._check_auth()
        return await call_next(context)

    async def on_request(self, context: MiddlewareContext, call_next):
        """Authenticate on every request."""
        logger.info(f"BEARER_AUTH_ON_REQUEST triggered. Context type: {type(context)}")
        self._check_auth()
        return await call_next(context)

    async def on_initialize(self, context: MiddlewareContext, call_next):
        """Authenticate before initializing SSE connection."""
        logger.info(
            f"BEARER_AUTH_ON_INITIALIZE triggered. Context type: {type(context)}"
        )
        logger.info(f"Context dir: {dir(context)}")
        if hasattr(context, "__dict__"):
            logger.info(f"Context dict keys: {context.__dict__.keys()}")
        self._check_auth()
        return await call_next(context)
