# Deploy MCPDOC On Koyeb (CPU Eco)

This repo includes `koyeb_app.py`, a `Dockerfile`, and a `Procfile` so Koyeb can run a hosted MCP docs server with either Docker or Buildpack.

## What this server exposes

- Transport: `streamable-http` by default
- Main endpoint: `/mcp`
- Built-in documentation sources:
  - `https://langchain-ai.github.io/langgraph/llms.txt`
  - `https://langchain-ai.github.io/langgraphjs/llms.txt`
  - `https://python.langchain.com/llms.txt`
  - `https://js.langchain.com/llms.txt`

## 1) Create your own GitHub repo from this

Recommended for your use case:
- `fork` this repo if you want to keep syncing upstream `langchain-ai/mcpdoc`
- `new repo + copy` if you expect major custom changes

For most users, start with a fork.

## 2) Deploy on Koyeb (Free / CPU Eco)

1. In Koyeb, create a **Web Service** from your GitHub repo.
2. Choose branch `main`.
3. Builder:
   - preferred: **Dockerfile** (build image from repo)
   - fallback: **Buildpack** (uses `Procfile`)
4. Instance type: **Free / CPU Eco**.
5. Port:
   - `PORT=8000` in environment variables
   - Exposed HTTP port `8000`
   - Health check path: `/health`
6. Deploy.

When using Buildpack, the `Procfile` runs:

```bash
python koyeb_app.py
```

## 3) Optional environment variables

- `PORT` (default `8000`)
- `HOST` (default `0.0.0.0`)
- `MCPDOC_TRANSPORT` (default `streamable-http`)
- `MCPDOC_TIMEOUT` (default `15`)
- `MCPDOC_FOLLOW_REDIRECTS` (`true/false`, default `false`)
- `MCPDOC_ALLOWED_DOMAINS` (comma-separated domains or `*`)
- `MCPDOC_SOURCES_JSON` (JSON list to override default `llms.txt` sources)

Example:

```json
[{"name":"LangGraph Python","llms_txt":"https://langchain-ai.github.io/langgraph/llms.txt"}]
```

## 4) Connect from MCP clients (including Codex-compatible hosts)

Use your Koyeb URL with `/mcp`, for example:

```text
https://your-service-name.koyeb.app/mcp
```

If your client supports custom headers, no auth header is required for this public docs server.
