# PROJECT.md — Platform Research Notes

> This file is a working notepad for the developer (or AI coding agent) building
> this MCP server. Fill in each section as you research the target platform.
> The information here drives the implementation in `src/main.py` and `src/tools.py`.
>
> **Do not commit secrets.** Store credentials in `.env` (which is gitignored).

---

## Platform Overview

**Platform name:** Granola API
**Official docs:** https://docs.granola.ai/introduction
**Base URL:** `https://public-api.granola.ai`

Granola is a business AI tool that captures, transcribes, and summarizes meeting audio to generate comprehensive meeting notes. It connects to Google Calendar or Outlook, automatically processes meeting recordings, and creates AI-enhanced notes with summaries, action items, and transcripts. The API provides programmatic access to meeting notes, transcripts, attendee data, and calendar event information. Building an MCP server allows AI assistants to search through meeting history, extract insights from past conversations, retrieve specific meeting details, and help users analyze their meeting data for better business intelligence and follow-up actions.

---

## Authentication

**Auth type:** Bearer Token (API Key)
**How to obtain credentials:** Open Granola desktop app → Settings → API → Create new key

### Credential details

- **Token / key name:** `GRANOLA_API_KEY`
- **Header format:** `Bearer {api_key}`
- **Scopes required:**
  - Personal API key: Access to notes you own, notes shared with you, notes in private folders shared with you
  - Enterprise API key: Access to all notes in the Team space

### OAuth-specific (skip if using API Key)

Not applicable - uses API Key authentication.

### Example authenticated request

```bash
curl "https://public-api.granola.ai/v1/notes" \
  -H "Authorization: Bearer grn_YOUR_API_KEY"
```

---

## Endpoints / Features to Implement

| Tool name | Method | Path | Description |
|-----------|--------|------|-------------|
| list_notes | GET | `/v1/notes` | List note summaries. Supports `created_before`, `created_after`, `updated_after`, `cursor`, and `page_size` query parameters. Returns `{ notes, hasMore, cursor }`. |
| get_note | GET | `/v1/notes/{note_id}` | Get a full note by `not_...` ID, including owner, calendar event, attendees, folder membership, and summary fields. |
| get_note_with_transcript | GET | `/v1/notes/{note_id}?include=transcript` | Get a full note plus the transcript. `include` currently accepts only `transcript`. |
| get_recent_notes | GET | `/v1/notes` | Convenience wrapper around `list_notes` using `created_after` for recent windows such as last week or last month. |
| search_notes_by_date | GET | `/v1/notes` | Convenience wrapper around `list_notes` for date/date-time filtering by creation or update timestamp. |
| list_notes_paginated | GET | `/v1/notes` | Follow cursor pagination until exhausted or a caller-provided page limit is reached. |
| get_meeting_summary | GET | `/v1/notes/{note_id}` | Return just the meeting metadata plus `summary_text` and `summary_markdown` for concise assistant responses. |
| get_transcript_text | GET | `/v1/notes/{note_id}?include=transcript` | Return transcript entries normalized into speaker/source, text, and optional timestamps. |

---

## Rate Limits and Restrictions

- **Rate limit:** 25 requests burst capacity, 5 requests/second sustained rate (300/minute)
- **Retry strategy:** Exponential backoff, respect `429 Too Many Requests` responses
- **Other restrictions:** API only returns notes with generated AI summary and transcript; notes still processing or never summarized return 404; Personal API keys require Business or Enterprise plan

---

## Response Format Notes

```json
{
  "notes": [
    {
      "id": "not_1d3tmYTlCICgjy",
      "object": "note",
      "title": "Quarterly yoghurt budget review",
      "owner": {
        "name": "Oat Benson",
        "email": "oat@granola.ai"
      },
      "created_at": "2026-01-27T15:30:00Z",
      "updated_at": "2026-01-27T16:45:00Z"
    }
  ],
  "hasMore": true,
  "cursor": "eyJjcmVkZW50aWFsfQ=="
}
```

Full note object includes additional fields: web_url, calendar_event, attendees, folder_membership, summary_text, summary_markdown, and transcript (when include=transcript parameter is used). Transcript format differs between macOS and iOS - macOS shows speaker.source as "microphone" or "speaker", while iOS shows speaker.source as "microphone" with optional diarization_label for "Speaker A/B" identification.

---

## Token / Credential Notes

- Two types of API keys: Personal (user-scoped) and Enterprise (workspace-scoped)
- Personal API keys require Business or Enterprise plan
- Enterprise API keys require workspace admin privileges to create
- On Enterprise plans, admins can disable Personal API key creation via workspace settings
- Rate limits applied per workspace for Enterprise keys, per user for Personal keys
- No mentioned token expiry - appears to be long-lived API keys

---

## Additional References

- OpenAPI specification: `api-reference/openapi.json.md`
- API introduction: https://docs.granola.ai/introduction
- MCP integration documentation: https://docs.granola.ai/help-center/sharing/integrations/mcp
- Personal API documentation: https://docs.granola.ai/help-center/sharing/integrations/personal-api
- Enterprise API documentation: https://docs.granola.ai/help-center/sharing/integrations/enterprise-api

---

## Notes for README

- Requires Granola Business or Enterprise plan for Personal API access
- API only returns notes with completed AI processing (notes still being processed won't appear)
- Supports both Personal API keys (user notes) and Enterprise API keys (workspace notes)
- Rate limited to 25 requests burst capacity, 5 requests/second sustained
- Transcript format differs between macOS (microphone/speaker sources) and iOS (diarization labels)
- Perfect for building AI assistants that can search meeting history and extract business insights
- Supports advanced filtering by date ranges, attendees, and meeting metadata