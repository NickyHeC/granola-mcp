# granola-mcp

A [Granola](https://granola.ai) meeting notes MCP server built on the [Dedalus](https://dedaluslabs.ai) platform.

Search through meeting history, retrieve meeting notes and transcripts, and extract business insights — all through AI assistants using the Model Context Protocol.

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- A [Granola](https://granola.ai) account with Business or Enterprise plan
- A Granola Personal API key
- A [Dedalus](https://dedaluslabs.ai) account

---

## Quick Start

### 1. Create a Granola API Key

1. Open the **Granola desktop app**.
2. Go to **Settings → API**.
3. Click **Create new key**.
4. Copy the key (it starts with `grn_`).

> **Note:** Personal API keys require a Granola Business or Enterprise plan.

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Fill in your `.env`:

```env
# Granola API Key
GRANOLA_API_KEY=grn_your-api-key-here

# Dedalus Platform (for the sample client)
DEDALUS_API_KEY=dsk-live-your-api-key
DEDALUS_API_URL=https://api.dedaluslabs.ai
DEDALUS_AS_URL=https://as.dedaluslabs.ai

# After deploying, set this to your slug
GRANOLA_MCP_SLUG=nickyhec/granola-mcp
```

### 3. Deploy to Dedalus

1. Log in to the [Dedalus Dashboard](https://dedaluslabs.ai).
2. Go to **Add Server** and connect this GitHub repository.
3. In the server configuration, enter the `GRANOLA_API_KEY` from your `.env`.
4. Deploy. The dashboard will show your server slug (e.g. `nickyhec/granola-mcp`).

### 4. Install Dependencies

```bash
uv sync
```

### 5. Run the Client

```bash
uv run src/_client.py
```

```
=== Granola MCP Agent ===
Server: nickyhec/granola-mcp
Type 'quit' or 'exit' to end the session.

You: What meetings did I have this week?
Assistant: ...
```

---

## Environment Variables

| Variable | Description |
| --- | --- |
| `GRANOLA_API_KEY` | Your Granola API key (`grn_*`). Get from Granola desktop app → Settings → API. |
| `DEDALUS_API_KEY` | Your Dedalus API key (`dsk_*`) |
| `DEDALUS_API_URL` | API base URL (default: `https://api.dedaluslabs.ai`) |
| `DEDALUS_AS_URL` | Authorization server URL (default: `https://as.dedaluslabs.ai`) |
| `GRANOLA_MCP_SLUG` | Your deployed server slug (e.g. `nickyhec/granola-mcp`) |

---

## Running the Server Locally

```bash
uv run src/main.py
```

This starts the MCP server on port 8080. The `_client.py` connects through
Dedalus (not localhost). Use this for local testing with a direct MCP client.

---

## Lint & Typecheck

```bash
uv run --group lint ruff format src/
uv run --group lint ruff check src/ --fix
uv run --group lint ty check src/
```

---

## Available Tools

| Tool | Description |
| --- | --- |
| `granola_list_notes` | List note summaries with optional date filters and pagination |
| `granola_get_note` | Get a full note by ID (owner, attendees, calendar event, summary) |
| `granola_get_note_with_transcript` | Get a full note including its meeting transcript |
| `granola_get_recent_notes` | Fetch notes from a recent time window (day, week, or month) |
| `granola_search_notes_by_date` | Filter notes by creation or update date ranges |
| `granola_list_notes_paginated` | Auto-paginate through all matching notes |
| `granola_get_meeting_summary` | Get meeting metadata plus summary text for concise responses |
| `granola_get_transcript_text` | Get normalized transcript entries (speaker, text, timestamps) |

All tools are **read-only** — this server does not modify any data in Granola.

### Tool Details

#### `granola_list_notes`

List note summaries with optional date filtering and cursor-based pagination.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `created_before` | `str \| None` | `None` | ISO 8601 datetime upper bound |
| `created_after` | `str \| None` | `None` | ISO 8601 datetime lower bound |
| `updated_after` | `str \| None` | `None` | Only notes updated after this time |
| `cursor` | `str \| None` | `None` | Pagination cursor from previous response |
| `page_size` | `int` | `25` | Notes per page |

#### `granola_get_note`

Fetch a complete note by ID, including owner info, calendar event, attendees, and AI summary.

| Parameter | Type | Description |
| --- | --- | --- |
| `note_id` | `str` | Note ID (e.g. `not_1d3tmYTlCICgjy`) |

#### `granola_get_note_with_transcript`

Same as `granola_get_note` but also includes the full meeting transcript.

| Parameter | Type | Description |
| --- | --- | --- |
| `note_id` | `str` | Note ID (e.g. `not_1d3tmYTlCICgjy`) |

#### `granola_get_recent_notes`

Convenience wrapper that fetches notes from a relative time window.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `window` | `str` | `"week"` | Time window: `"day"`, `"week"`, or `"month"` |
| `page_size` | `int` | `25` | Notes per page |

#### `granola_search_notes_by_date`

Filter notes by specific date ranges. At least one date filter is required.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `created_after` | `str \| None` | `None` | ISO 8601 datetime lower bound |
| `created_before` | `str \| None` | `None` | ISO 8601 datetime upper bound |
| `updated_after` | `str \| None` | `None` | Only notes updated after this time |
| `page_size` | `int` | `25` | Notes per page |

#### `granola_list_notes_paginated`

Automatically follows cursor pagination to retrieve multiple pages of notes.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `created_after` | `str \| None` | `None` | ISO 8601 datetime lower bound |
| `created_before` | `str \| None` | `None` | ISO 8601 datetime upper bound |
| `updated_after` | `str \| None` | `None` | Only notes updated after this time |
| `max_pages` | `int` | `10` | Maximum pages to fetch |
| `page_size` | `int` | `25` | Notes per page |

#### `granola_get_meeting_summary`

Returns just the meeting metadata and summary fields — no transcript or heavy content.

| Parameter | Type | Description |
| --- | --- | --- |
| `note_id` | `str` | Note ID (e.g. `not_1d3tmYTlCICgjy`) |

#### `granola_get_transcript_text`

Returns normalized transcript entries with speaker identification.

| Parameter | Type | Description |
| --- | --- | --- |
| `note_id` | `str` | Note ID (e.g. `not_1d3tmYTlCICgjy`) |

---

## Architecture

Granola provides a REST API at `https://public-api.granola.ai`. The request
layer dispatches calls through the Dedalus HTTP enclave, which injects API
Key credentials transparently.

```
src/
├── granola/
│   ├── config.py      # Connection definition (API Key / Bearer token)
│   ├── request.py     # REST dispatch + coercion helpers
│   └── types.py       # Typed dataclass models
├── tools/
│   ├── notes.py       # Core note retrieval (list, get, get with transcript)
│   ├── search.py      # Date filtering + pagination helpers
│   └── summaries.py   # Summary + transcript extraction
├── server.py          # MCPServer setup
├── main.py            # Server entry point
└── _client.py         # Interactive agent client (DAuth)
```

---

## Rate Limits

Granola enforces the following rate limits:

- **Burst capacity:** 25 requests
- **Sustained rate:** 5 requests/second (300/minute)

Rate limits apply per-workspace for Enterprise API keys and per-user for
Personal API keys. The server does not currently implement automatic retry
logic — if you hit rate limits, wait and retry.

---

## Troubleshooting

### "Failed to fetch note" / 404 errors

The Granola API only returns notes that have completed AI processing (summary
and transcript generation). Notes that are still being processed or were never
summarized will return 404.

### API key not working

- Verify you have a **Business or Enterprise** Granola plan (required for Personal API keys).
- Check that the key starts with `grn_`.
- Enterprise admins can disable Personal API key creation — check with your workspace admin.

### Transcript format differences

Transcript format varies by recording platform:
- **macOS:** Speaker `source` is `"microphone"` (local) or `"speaker"` (remote audio).
- **iOS:** Speaker `source` is `"microphone"` with optional `diarization_label` for speaker identification (e.g. `"Speaker A"`, `"Speaker B"`).

### "Granola MCP server is currently unavailable"

The client routes through the Dedalus platform by slug. Common causes:

1. **Server not deployed** — deploy from the Dedalus Dashboard first.
2. **Wrong slug** — verify `GRANOLA_MCP_SLUG` matches your deployment.

---

## Notes

- The API only returns notes with completed AI processing (summary + transcript).
- Personal API keys give access to notes you own, notes shared with you, and notes in shared private folders.
- Enterprise API keys give access to all notes in the Team space.
- Two API key types exist: Personal (user-scoped) and Enterprise (workspace-scoped).
- API keys appear to be long-lived with no expiry.
- All tools are read-only — this server does not create or modify notes.
- Authentication uses API Key (Bearer token) via DAuth. The raw key is never exposed to the server.
