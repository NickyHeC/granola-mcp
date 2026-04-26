"""Tool registry for granola-mcp.

Modules:
  notes       -- granola_list_notes, granola_get_note, granola_get_note_with_transcript
  search      -- granola_get_recent_notes, granola_search_notes_by_date, granola_list_notes_paginated
  summaries   -- granola_get_meeting_summary, granola_get_transcript_text
"""

from __future__ import annotations

from tools.notes import note_tools
from tools.search import search_tools
from tools.summaries import summary_tools


granola_tools = [
    *note_tools,
    *search_tools,
    *summary_tools,
]
