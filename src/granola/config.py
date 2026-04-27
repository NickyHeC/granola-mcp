"""Granola connection configuration.

Evaluated at import time, after ``load_dotenv()`` in ``main.py``
has already injected the .env file.

Granola uses API Key (Bearer token) authentication.
DAuth encrypts the key client-side and executes API calls
inside a sealed enclave.

Objects:
  granola -- Connection with Bearer token auth
"""

from __future__ import annotations

from dedalus_mcp.auth import Connection, SecretKeys


granola = Connection(
    name="granola-mcp",
    secrets=SecretKeys(token="GRANOLA_API_KEY"),  # noqa: S106
    base_url="https://public-api.granola.ai",
    auth_header_format="Bearer {api_key}",
)
