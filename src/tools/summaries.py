"""Summary and transcript tools.

Tools:
  granola_get_meeting_summary  -- meeting metadata plus summary text
  granola_get_transcript_text  -- normalized transcript entries
"""

from __future__ import annotations

from dedalus_mcp import tool
from dedalus_mcp.types import ToolAnnotations

from granola.request import _dict, _list, _opt_str, _str, api_get
from granola.types import (
    AttendeeInfo,
    GranolaResult,
    MeetingSummary,
    TranscriptEntry,
)
from tools.notes import _parse_attendees


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_get_meeting_summary(note_id: str) -> MeetingSummary | str:
    """Get meeting metadata and summary for concise assistant responses.

    Returns the note title, owner, attendees, and summary text/markdown
    without the full transcript or other heavy fields.

    Args:
        note_id: The note ID (e.g. ``not_1d3tmYTlCICgjy``).

    Returns:
        MeetingSummary with title and summary fields, or an error string.

    """
    response: GranolaResult = await api_get(f"/v1/notes/{note_id}")
    if not response.success:
        return response.error or "Failed to fetch meeting summary"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"

    owner = _dict(data.get("owner"))
    attendees = _parse_attendees(_list(data.get("attendees")))

    result = MeetingSummary(
        id=_str(data.get("id")),
        title=_str(data.get("title")),
        owner_name=_opt_str(owner.get("name")) if owner else None,
        created_at=_opt_str(data.get("created_at")),
        attendees=attendees,
        summary_text=_opt_str(data.get("summary_text")),
        summary_markdown=_opt_str(data.get("summary_markdown")),
    )
    return result


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def granola_get_transcript_text(note_id: str) -> list[TranscriptEntry] | str:
    """Get the transcript entries for a note.

    Returns transcript entries normalized into speaker, source, text,
    and optional timestamps. On macOS, speaker source is ``"microphone"``
    or ``"speaker"``. On iOS, source is ``"microphone"`` with optional
    ``diarization_label`` for speaker identification.

    Args:
        note_id: The note ID (e.g. ``not_1d3tmYTlCICgjy``).

    Returns:
        List of TranscriptEntry objects, or an error string.

    """
    response: GranolaResult = await api_get(
        f"/v1/notes/{note_id}",
        {"include": "transcript"},
    )
    if not response.success:
        return response.error or "Failed to fetch transcript"
    data = response.data
    if not isinstance(data, dict):
        return "Unexpected response format"

    raw_transcript = _list(data.get("transcript"))
    entries: list[TranscriptEntry] = []
    for item in raw_transcript:
        if not isinstance(item, dict):
            continue
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


summary_tools = [
    granola_get_meeting_summary,
    granola_get_transcript_text,
]
