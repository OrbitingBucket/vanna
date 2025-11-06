"""
Artelia Learning Platform - Web Server
FastAPI server with pre-built web UI for natural language database queries
"""

import os
from artelia_learning_agent import create_artelia_agent
from vanna.servers.fastapi import VannaFastAPIServer
import asyncio


async def create_artelia_server():
    """Create and configure FastAPI server for Artelia Learning."""

    # Get configuration from environment
    postgres_conn = os.getenv(
        "ARTELIA_POSTGRES_CONNECTION",
        "postgresql://user:password@localhost:5432/artelia_learning"
    )
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if not openrouter_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Set it with: export OPENROUTER_API_KEY='your-key-here'"
        )

    print("🚀 Starting Artelia Learning Web Server...")

    # Create agent
    agent = await create_artelia_agent(
        postgres_connection_string=postgres_conn,
        openrouter_api_key=openrouter_key,
        documentation_file="DB/DATABASE_DOCUMENTATION.md",
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        enable_memory=True,
        enable_visualization=True
    )

    # Create FastAPI server
    server = VannaFastAPIServer(
        agent=agent,
        port=int(os.getenv("PORT", "8000"))
    )

    print("\n" + "="*80)
    print("🎓 ARTELIA LEARNING ASSISTANT - WEB SERVER")
    print("="*80)
    print(f"🌐 Web UI:  http://localhost:{server.port}")
    print(f"📡 API:     http://localhost:{server.port}/docs")
    print("="*80)
    print("\nServer is ready! Press Ctrl+C to stop.\n")

    return server


def main():
    """Run the server."""
    # Create and run server
    server = asyncio.run(create_artelia_server())
    server.run()


if __name__ == "__main__":
    main()
