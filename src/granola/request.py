"""Granola REST request dispatch and response helpers.

Granola uses a standard REST API with GET endpoints.
All requests go through the Dedalus enclave for secure
credential injection.

Functions:
  api_get(path, params)  -- dispatch GET request via Dedalus enclave

Coercion helpers (safe extraction from untyped API dicts):
  _str(val, default)      -- coerce to str
  _opt_str(val)           -- coerce to str | None
  _list(val)              -- coerce to list
  _dict(val)              -- coerce to dict
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from dedalus_mcp import HttpMethod, HttpRequest, get_context

from granola.config import granola
from granola.types import GranolaResult


# --- REST dispatch ---


async def api_get(
    path: str,
    params: dict[str, Any] | None = None,
) -> GranolaResult:
    """Execute a GET request to the Granola API via the Dedalus enclave.

    All Granola API interaction goes through this single function.

    Args:
        path: API path (e.g. ``/v1/notes``).
        params: Optional query parameters. ``None`` values are filtered out.

    Returns:
        GranolaResult wrapping the response data or error.

    """
    if params:
        filtered = {k: str(v) for k, v in params.items() if v is not None}
        if filtered:
            path = f"{path}?{urlencode(filtered)}"

    ctx = get_context()
    req = HttpRequest(method=HttpMethod.GET, path=path)
    resp = await ctx.dispatch(granola, req)
    if resp.success and resp.response is not None:
        result = GranolaResult(success=True, data=resp.response.body)
        return result
    error = resp.error.message if resp.error else "Request failed"
    result = GranolaResult(success=False, error=error)
    return result


# --- Coercion helpers (safe extraction from untyped API dicts) ---


def _str(val: Any, default: str = "") -> str:  # noqa: ANN401
    """Safely coerce to string."""
    return str(val) if val is not None else default


def _opt_str(val: Any) -> str | None:  # noqa: ANN401
    """Safely coerce to optional string."""
    return str(val) if val is not None else None


def _list(val: Any) -> list[Any]:  # noqa: ANN401
    """Safely coerce to list."""
    return val if isinstance(val, list) else []


def _dict(val: Any) -> dict[str, Any]:  # noqa: ANN401
    """Safely coerce to dict."""
    return val if isinstance(val, dict) else {}
