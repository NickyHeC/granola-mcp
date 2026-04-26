"""Sample MCP client demonstrating Dedalus Auth (DAuth) with interactive loop.

DAuth (Dedalus Auth):
    Multi-tenant MCP authentication requires the Dedalus SDK. Generic MCP clients
    are spec-compliant but don't support credential injection.

    This file demonstrates DAuth: API Key credentials are securely managed by the
    platform. The server NEVER sees the raw API key directly.

    For custom runners or lower-level SDK usage, see https://docs.dedaluslabs.ai

Environment variables:
    DEDALUS_API_KEY:  Your Dedalus API key (dsk_*)
    DEDALUS_API_URL:  API base URL
    DEDALUS_AS_URL:   Authorization server URL
"""

import asyncio
import os

from dotenv import load_dotenv


load_dotenv()

from dedalus_labs import AsyncDedalus, DedalusRunner
from dedalus_labs.utils.stream import stream_async


class MissingEnvError(ValueError):
    """Required environment variable not set."""


def get_env(key: str) -> str:
    """Get required env var or raise."""
    val = os.getenv(key)
    if not val:
        raise MissingEnvError(key)
    return val


API_URL = get_env("DEDALUS_API_URL")
AS_URL = get_env("DEDALUS_AS_URL")
DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY")
MCP_SLUG = os.getenv("GRANOLA_MCP_SLUG", "nickyhec/granola-mcp")

print("=== Environment ===")
print(f"  DEDALUS_API_URL: {API_URL}")
print(f"  DEDALUS_AS_URL: {AS_URL}")
print(
    f"  DEDALUS_API_KEY: {DEDALUS_API_KEY[:20]}..."
    if DEDALUS_API_KEY
    else "  DEDALUS_API_KEY: None"
)
print(f"  MCP Server: {MCP_SLUG}")


async def run_agent_loop() -> None:
    """Interactive agent loop with streaming."""
    client = AsyncDedalus(api_key=DEDALUS_API_KEY, base_url=API_URL, as_base_url=AS_URL)
    runner = DedalusRunner(client)
    messages: list[dict] = []

    async def run_turn() -> None:
        stream = runner.run(
            input=messages,
            model="anthropic/claude-opus-4-5",
            mcp_servers=[MCP_SLUG],
            stream=True,
        )
        print("\nAssistant: ", end="", flush=True)
        await stream_async(stream)

    print("\n=== Granola MCP Agent ===")
    print(f"Server: {MCP_SLUG}")
    print("Type 'quit' or 'exit' to end the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        await run_turn()
        print()


async def main() -> None:
    """Run interactive agent loop."""
    await run_agent_loop()


if __name__ == "__main__":
    asyncio.run(main())
