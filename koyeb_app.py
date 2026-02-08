#!/usr/bin/env python3
"""Koyeb entrypoint for hosting mcpdoc with streamable HTTP."""

from __future__ import annotations

import json
import os
import sys

from mcpdoc.main import DocSource, create_server
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

DEFAULT_DOC_SOURCES: list[DocSource] = [
    {
        "name": "LangGraph Python",
        "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt",
    },
    {
        "name": "LangGraph JS",
        "llms_txt": "https://langchain-ai.github.io/langgraphjs/llms.txt",
    },
    {
        "name": "LangChain Python",
        "llms_txt": "https://python.langchain.com/llms.txt",
    },
    {
        "name": "LangChain JS",
        "llms_txt": "https://js.langchain.com/llms.txt",
    },
]


def _parse_bool(name: str, *, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_doc_sources() -> list[DocSource]:
    raw = os.getenv("MCPDOC_SOURCES_JSON")
    if not raw:
        return DEFAULT_DOC_SOURCES

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("MCPDOC_SOURCES_JSON must be valid JSON") from exc

    if not isinstance(data, list):
        raise ValueError("MCPDOC_SOURCES_JSON must be a JSON list")

    parsed: list[DocSource] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(
                f"MCPDOC_SOURCES_JSON[{index}] must be an object with llms_txt"
            )

        llms_txt = item.get("llms_txt")
        if not isinstance(llms_txt, str) or not llms_txt.strip():
            raise ValueError(
                f"MCPDOC_SOURCES_JSON[{index}] is missing a non-empty llms_txt"
            )

        entry: DocSource = {"llms_txt": llms_txt.strip()}

        name = item.get("name")
        if isinstance(name, str) and name.strip():
            entry["name"] = name.strip()

        description = item.get("description")
        if isinstance(description, str) and description.strip():
            entry["description"] = description.strip()

        parsed.append(entry)

    return parsed


def _parse_allowed_domains() -> list[str] | None:
    raw = os.getenv("MCPDOC_ALLOWED_DOMAINS")
    if not raw:
        return None

    domains = [item.strip() for item in raw.split(",") if item.strip()]
    return domains or None


def main() -> None:
    doc_sources = _parse_doc_sources()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    transport = os.getenv("MCPDOC_TRANSPORT", "streamable-http")
    timeout = float(os.getenv("MCPDOC_TIMEOUT", "15"))
    follow_redirects = _parse_bool("MCPDOC_FOLLOW_REDIRECTS", default=False)
    allowed_domains = _parse_allowed_domains()

    settings = {
        "host": host,
        "port": port,
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    server = create_server(
        doc_sources,
        follow_redirects=follow_redirects,
        timeout=timeout,
        settings=settings,
        allowed_domains=allowed_domains,
    )

    print(
        (
            f"Starting mcpdoc on {host}:{port} "
            f"(transport={transport}, doc_sources={len(doc_sources)})"
        ),
        file=sys.stderr,
    )
    if transport == "streamable-http":
        mcp_app = server.streamable_http_app()

        async def _health(_request) -> JSONResponse:
            return JSONResponse(
                {
                    "status": "ok",
                    "transport": "streamable-http",
                    "doc_sources": len(doc_sources),
                }
            )

        async def _root(_request) -> JSONResponse:
            return JSONResponse(
                {
                    "name": "mcpdoc",
                    "transport": "streamable-http",
                    "endpoints": {
                        "mcp": "/mcp",
                        "health": "/health",
                    },
                }
            )

        app = Starlette(
            debug=mcp_app.debug,
            routes=[
                Route("/", _root),
                Route("/health", _health),
                *mcp_app.routes,
            ],
            middleware=mcp_app.user_middleware,
            lifespan=mcp_app.router.lifespan_context,
        )
        uvicorn.run(app, host=host, port=port, log_level=settings["log_level"].lower())
        return

    server.run(transport=transport)


if __name__ == "__main__":
    main()
