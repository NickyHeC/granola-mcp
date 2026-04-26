"""Search and filtering tools.

Tools:
  granola_get_recent_notes      -- fetch notes from a recent time window
  granola_search_notes_by_date  -- filter notes by date range
  granola_list_notes_paginated  -- auto-paginate through all matching notes
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from dedalus_mcp import tool
from dedalus_mcp.types import ToolAnnotations

from granola.request import _list, api_get
from granola.types import GranolaResult, JSONObject, NoteSummary
from tools.notes import _parse_note_summary


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_get_recent_notes(
    window: str = "week",
    page_size: int = 25,
) -> list[NoteSummary] | str:
    """Fetch notes from a recent time window.

    Convenience wrapper around the notes endpoint using ``created_after``
    to retrieve notes from the last day, week, or month.

    Args:
        window: Time window — ``"day"``, ``"week"``, or ``"month"`` (default ``"week"``).
        page_size: Number of notes per page (default 25).

    Returns:
        List of NoteSummary objects from the specified window, or an error string.

    """
    now = datetime.now(tz=timezone.utc)
    deltas = {"day": timedelta(days=1), "week": timedelta(weeks=1), "month": timedelta(days=30)}
    delta = deltas.get(window.lower())
    if delta is None:
        return f"Invalid window '{window}'. Use 'day', 'week', or 'month'."
    created_after = (now - delta).isoformat()

    params = {"created_after": created_after, "page_size": page_size}
    response: GranolaResult = await api_get("/v1/notes", params)
    if not response.success:
        return response.error or "Failed to fetch recent notes"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"
    notes = _list(data.get("notes"))
    result = [_parse_note_summary(n) for n in notes if isinstance(n, dict)]
    return result


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_search_notes_by_date(
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    page_size: int = 25,
) -> list[NoteSummary] | str:
    """Filter notes by creation or update timestamps.

    At least one date filter must be provided. Dates should be ISO 8601
    format (e.g. ``2026-01-01T00:00:00Z``).

    Args:
        created_after: ISO 8601 datetime — notes created after this time.
        created_before: ISO 8601 datetime — notes created before this time.
        updated_after: ISO 8601 datetime — notes updated after this time.
        page_size: Number of notes per page (default 25).

    Returns:
        List of NoteSummary objects matching the date filters, or an error string.

    """
    if not any([created_after, created_before, updated_after]):
        return "At least one date filter is required."

    params: dict = {
        "created_after": created_after,
        "created_before": created_before,
        "updated_after": updated_after,
        "page_size": page_size,
    }
    response: GranolaResult = await api_get("/v1/notes", params)
    if not response.success:
        return response.error or "Failed to search notes"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"
    notes = _list(data.get("notes"))
    result = [_parse_note_summary(n) for n in notes if isinstance(n, dict)]
    return result


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_list_notes_paginated(
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    max_pages: int = 10,
    page_size: int = 25,
) -> list[NoteSummary] | str:
    """Paginate through notes until exhausted or a page limit is reached.

    Automatically follows cursor pagination. Useful for bulk retrieval
    within a date range.

    Args:
        created_after: ISO 8601 datetime — notes created after this time.
        created_before: ISO 8601 datetime — notes created before this time.
        updated_after: ISO 8601 datetime — notes updated after this time.
        max_pages: Maximum number of pages to fetch (default 10).
        page_size: Number of notes per page (default 25).

    Returns:
        List of all NoteSummary objects across pages, or an error string.

    """
    all_notes: list[NoteSummary] = []
    cursor: str | None = None

    for _ in range(max_pages):
        params: dict = {
            "created_after": created_after,
            "created_before": created_before,
            "updated_after": updated_after,
            "cursor": cursor,
            "page_size": page_size,
        }
        response: GranolaResult = await api_get("/v1/notes", params)
        if not response.success:
            return response.error or "Failed to fetch notes page"
        data = response.data
        if not isinstance(data, dict):
            return "Unexpected response format"

        notes = _list(data.get("notes"))
        all_notes.extend(
            _parse_note_summary(n) for n in notes if isinstance(n, dict)
        )

        has_more = data.get("hasMore", False)
        if not has_more:
            break
        cursor = data.get("cursor")  # type: ignore[assignment]
        if not cursor:
            break

    return all_notes


search_tools = [
    granola_get_recent_notes,
    granola_search_notes_by_date,
    granola_list_notes_paginated,
]
