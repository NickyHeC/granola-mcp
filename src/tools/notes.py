"""Core note tools.

Tools:
  granola_list_notes              -- list note summaries with pagination
  granola_get_note                -- get a full note by ID
  granola_get_note_with_transcript -- get a full note including transcript
"""

from __future__ import annotations

from dedalus_mcp import tool
from dedalus_mcp.types import ToolAnnotations

from granola.request import _dict, _list, _opt_str, _str, api_get
from granola.types import (
    AttendeeInfo,
    CalendarEventInfo,
    GranolaResult,
    JSONObject,
    NoteDetail,
    NoteSummary,
    OwnerInfo,
    TranscriptEntry,
)


# --- Helpers ---


def _parse_note_summary(raw: JSONObject) -> NoteSummary:
    """Parse a raw note object into a NoteSummary.

    Args:
        raw: Untyped note object from the API list response.

    Returns:
        Parsed NoteSummary with coerced fields.

    """
    owner = _dict(raw.get("owner"))
    result = NoteSummary(
        id=_str(raw.get("id")),
        title=_str(raw.get("title")),
        owner_name=_opt_str(owner.get("name")) if owner else None,
        owner_email=_opt_str(owner.get("email")) if owner else None,
        created_at=_opt_str(raw.get("created_at")),
        updated_at=_opt_str(raw.get("updated_at")),
    )
    return result


def _parse_attendees(raw_list: list) -> list[AttendeeInfo]:  # noqa: ANN001
    """Parse attendee list into AttendeeInfo objects."""
    attendees: list[AttendeeInfo] = []
    for item in raw_list:
        if isinstance(item, dict):
            attendees.append(
                AttendeeInfo(
                    name=_str(item.get("name")),
                    email=_opt_str(item.get("email")),
                ),
            )
    return attendees


def _parse_calendar_event(raw: JSONObject) -> CalendarEventInfo | None:
    """Parse calendar event data."""
    if not raw:
        return None
    return CalendarEventInfo(
        title=_opt_str(raw.get("title")),
        start_at=_opt_str(raw.get("start_at")),
        end_at=_opt_str(raw.get("end_at")),
    )


def _parse_transcript(raw_list: list) -> list[TranscriptEntry]:  # noqa: ANN001
    """Parse transcript entries."""
    entries: list[TranscriptEntry] = []
    for item in raw_list:
        if isinstance(item, dict):
            speaker = _dict(item.get("speaker"))
            entries.append(
                TranscriptEntry(
                    speaker=_opt_str(speaker.get("name")) if speaker else None,
                    source=_opt_str(speaker.get("source")) if speaker else None,
                    text=_str(item.get("text")),
                    timestamp=_opt_str(item.get("timestamp")),
                    diarization_label=_opt_str(speaker.get("diarization_label"))
                    if speaker
                    else None,
                ),
            )
    return entries


def _parse_note_detail(
    raw: JSONObject,
    *,
    include_transcript: bool = False,
) -> NoteDetail:
    """Parse a raw note object into a NoteDetail.

    Args:
        raw: Untyped full note object from the API.
        include_transcript: Whether to parse transcript entries.

    Returns:
        Parsed NoteDetail with all metadata fields.

    """
    owner_raw = _dict(raw.get("owner"))
    owner = (
        OwnerInfo(
            name=_str(owner_raw.get("name")),
            email=_opt_str(owner_raw.get("email")),
        )
        if owner_raw
        else None
    )

    attendees = _parse_attendees(_list(raw.get("attendees")))
    calendar_event = _parse_calendar_event(_dict(raw.get("calendar_event")))
    transcript = (
        _parse_transcript(_list(raw.get("transcript")))
        if include_transcript
        else []
    )

    result = NoteDetail(
        id=_str(raw.get("id")),
        title=_str(raw.get("title")),
        owner=owner,
        web_url=_opt_str(raw.get("web_url")),
        created_at=_opt_str(raw.get("created_at")),
        updated_at=_opt_str(raw.get("updated_at")),
        summary_text=_opt_str(raw.get("summary_text")),
        summary_markdown=_opt_str(raw.get("summary_markdown")),
        attendees=attendees,
        calendar_event=calendar_event,
        transcript=transcript,
    )
    return result


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_list_notes(
    created_before: str | None = None,
    created_after: str | None = None,
    updated_after: str | None = None,
    cursor: str | None = None,
    page_size: int = 25,
) -> list[NoteSummary] | str:
    """List note summaries with optional date filters and pagination.

    Returns a paginated list of note summaries. Use ``cursor`` from a
    previous response to fetch the next page.

    Args:
        created_before: ISO 8601 datetime — only notes created before this time.
        created_after: ISO 8601 datetime — only notes created after this time.
        updated_after: ISO 8601 datetime — only notes updated after this time.
        cursor: Pagination cursor from a previous response.
        page_size: Number of notes per page (default 25).

    Returns:
        List of NoteSummary objects, or an error string on failure.

    """
    params = {
        "created_before": created_before,
        "created_after": created_after,
        "updated_after": updated_after,
        "cursor": cursor,
        "page_size": page_size,
    }
    response: GranolaResult = await api_get("/v1/notes", params)
    if not response.success:
        return response.error or "Failed to list notes"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"
    notes = _list(data.get("notes"))
    result = [_parse_note_summary(n) for n in notes if isinstance(n, dict)]
    return result


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_get_note(note_id: str) -> NoteDetail | str:
    """Get a full note by ID.

    Returns the complete note including owner, calendar event, attendees,
    folder membership, and summary fields.

    Args:
        note_id: The note ID (e.g. ``not_1d3tmYTlCICgjy``).

    Returns:
        NoteDetail with full metadata, or an error string on failure.

    """
    response: GranolaResult = await api_get(f"/v1/notes/{note_id}")
    if not response.success:
        return response.error or "Failed to fetch note"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"
    result = _parse_note_detail(data)
    return result


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_get_note_with_transcript(note_id: str) -> NoteDetail | str:
    """Get a full note including its transcript.

    Same as ``granola_get_note`` but also includes the full meeting transcript.
    Transcript format differs between macOS (microphone/speaker sources) and
    iOS (diarization labels like Speaker A/B).

    Args:
        note_id: The note ID (e.g. ``not_1d3tmYTlCICgjy``).

    Returns:
        NoteDetail with transcript entries populated, or an error string.

    """
    response: GranolaResult = await api_get(
        f"/v1/notes/{note_id}",
        {"include": "transcript"},
    )
    if not response.success:
        return response.error or "Failed to fetch note with transcript"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"
    result = _parse_note_detail(data, include_transcript=True)
    return result


note_tools = [
    granola_list_notes,
    granola_get_note,
    granola_get_note_with_transcript,
]
