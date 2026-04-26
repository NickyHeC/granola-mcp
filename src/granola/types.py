"""Typed models for Granola API responses.

Result types (frozen dataclasses):
  GranolaResult        -- raw REST result wrapper
  NoteSummary          -- note from list endpoint
  OwnerInfo            -- note owner (name + email)
  AttendeeInfo         -- meeting attendee
  CalendarEventInfo    -- linked calendar event
  NoteDetail           -- full note with metadata
  TranscriptEntry      -- single transcript segment
  MeetingSummary       -- meeting metadata + summary only

Type aliases:
  JSONPrimitive        -- scalar JSON values
  JSONValue            -- recursive JSON value
  JSONObject           -- dict[str, JSONValue]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias


# --- JSON types ---

JSONPrimitive: TypeAlias = str | int | float | bool | None

JSONValue: TypeAlias = str | int | float | bool | dict[str, Any] | list[Any] | None

JSONObject: TypeAlias = dict[str, JSONValue]


# --- Generic result ---


@dataclass(frozen=True, slots=True)
class GranolaResult:
    """Raw Granola REST result.

    Used as the internal request return type.
    """

    # fmt: off
    success: bool
    data:    JSONValue | None = None
    error:   str | None       = None
    # fmt: on


# --- Owner ---


@dataclass(frozen=True, slots=True)
class OwnerInfo:
    """Note owner."""

    # fmt: off
    name:  str
    email: str | None = None
    # fmt: on


# --- Note summary (from list endpoint) ---


@dataclass(frozen=True, slots=True)
class NoteSummary:
    """Note summary from list endpoint."""

    # fmt: off
    id:         str
    title:      str
    owner_name: str | None = None
    owner_email: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    # fmt: on


# --- Attendee ---


@dataclass(frozen=True, slots=True)
class AttendeeInfo:
    """Meeting attendee."""

    # fmt: off
    name:  str
    email: str | None = None
    # fmt: on


# --- Calendar event ---


@dataclass(frozen=True, slots=True)
class CalendarEventInfo:
    """Linked calendar event."""

    # fmt: off
    title:    str | None = None
    start_at: str | None = None
    end_at:   str | None = None
    # fmt: on


# --- Full note detail ---


@dataclass(frozen=True, slots=True)
class NoteDetail:
    """Full note with all metadata.

    Returned by ``get_note`` and ``get_note_with_transcript``.
    """

    # fmt: off
    id:               str
    title:            str
    owner:            OwnerInfo | None           = None
    web_url:          str | None                 = None
    created_at:       str | None                 = None
    updated_at:       str | None                 = None
    summary_text:     str | None                 = None
    summary_markdown: str | None                 = None
    attendees:        list[AttendeeInfo]          = field(default_factory=list)
    calendar_event:   CalendarEventInfo | None   = None
    transcript:       list["TranscriptEntry"]     = field(default_factory=list)
    # fmt: on


# --- Transcript entry ---


@dataclass(frozen=True, slots=True)
class TranscriptEntry:
    """Single transcript segment.

    On macOS, ``source`` is ``"microphone"`` or ``"speaker"``.
    On iOS, ``source`` is ``"microphone"`` with optional ``diarization_label``
    for speaker identification (e.g. ``"Speaker A"``).
    """

    # fmt: off
    speaker:            str | None = None
    source:             str | None = None
    text:               str        = ""
    timestamp:          str | None = None
    diarization_label:  str | None = None
    # fmt: on


# --- Meeting summary (lightweight) ---


@dataclass(frozen=True, slots=True)
class MeetingSummary:
    """Meeting metadata plus summary fields.

    Lightweight projection of a full note, used by ``get_meeting_summary``.
    """

    # fmt: off
    id:               str
    title:            str
    owner_name:       str | None        = None
    created_at:       str | None        = None
    attendees:        list[AttendeeInfo] = field(default_factory=list)
    summary_text:     str | None        = None
    summary_markdown: str | None        = None
    # fmt: on
