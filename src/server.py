"""MCP server entrypoint.

Expose Granola meeting-notes tools via Dedalus MCP framework.
API Key credentials provided by DAuth at runtime.
"""

import os

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from granola.config import granola
from tools import granola_tools


def _disable_auto_output_schemas(server: MCPServer) -> None:
    # pylint: disable=protected-access
    server.tools._build_output_schema = lambda _fn: None  # type: ignore[assignment]


def create_server() -> MCPServer:
    """Create MCP server with current env config.

    Returns:
        Configured MCPServer instance.

    """
    as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    server = MCPServer(
        name="granola-mcp",
        connections=[granola],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=as_url,
    )
    _disable_auto_output_schemas(server)
    return server


async def main() -> None:
    """Start MCP server."""
    server = create_server()
    server.collect(*granola_tools)
    await server.serve(port=8080)
