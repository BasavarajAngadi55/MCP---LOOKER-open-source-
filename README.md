# Looker MCP + Python SDK starter

This project connects a Looker instance in two ways:

1. **Cursor MCP server** — Google [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) with the prebuilt Looker toolsets, so Agent chat can list models, run queries, and (optionally) work with LookML.
2. **Python Looker SDK** — `main.py` authenticates with API 4.0 keys and lists models/explores for a LookML project.

Official Looker + Toolbox docs: [Connect an IDE to Looker using MCP Toolbox](https://docs.cloud.google.com/looker/docs/2608/connect-ide-to-looker-using-mcp-toolbox).

Target GitHub remote: [BasavarajAngadi55/MCP---LOOKER-open-source-](https://github.com/BasavarajAngadi55/MCP---LOOKER-open-source-).

## What is in this repo

| Path | Purpose |
| --- | --- |
| `mcp.json.example` | Copy to `.cursor/mcp.json` in Cursor. Starts the Toolbox binary over stdio. |
| `.env.example` | Placeholder env vars. Copy to `looker-env/.env` locally. |
| `main.py` | SDK script: list models and explores for `PROJECT_NAME`. |
| `requirements.txt` | Python dependencies (`looker_sdk`, `python-dotenv`). |
| `bin/` | Download `toolbox` here (binary is gitignored). |

These are **not** committed (see `.gitignore`):

- `looker-env/.env` and any other `.env` files (API client id/secret)
- `looker-env/` (virtualenv)
- `bin/toolbox` (downloaded binary)
- Root `mcp.json` if present (older drafts sometimes hardcoded secrets)

## Secrets stay local

Cursor and git **do not** need your Looker client secret in the repo.

1. Copy `.env.example` to `looker-env/.env`.
2. Fill in your Looker URL and API 4.0 Client ID / Client Secret.
3. `.gitignore` blocks `.env` files and the virtualenv from being staged.

Create API keys in Looker: **Admin → Users → (your user) → API 4.0 Keys**, or from your account’s API Keys page. The secret is shown once.

If a secret was ever pasted into chat, a public gist, or a committed `mcp.json`, **rotate the API key in Looker** and update only the local `.env`.

## MCP vs Python script

They share the same Looker instance and similar credentials, but they are not the same process.

| | MCP (Cursor Agent) | `main.py` |
| --- | --- | --- |
| Who runs it | Cursor starts `bin/toolbox` | You run Python |
| Env names | `LOOKER_BASE_URL`, `LOOKER_CLIENT_ID`, `LOOKER_CLIENT_SECRET` | `LOOKERSDK_BASE_URL`, `LOOKERSDK_CLIENT_ID`, `LOOKERSDK_CLIENT_SECRET` |
| Typical use | Natural-language questions in chat | Repeatable scripts / CI |

Put **both** name sets in `looker-env/.env` (as in `.env.example`) so both paths work.

## Why you may see ~18 tools instead of ~40

Toolbox ships **separate Looker prebuilt configs**. They are not one big list.

| `--prebuilt` value | Role | Approx. tools (Toolbox v1.0.0) |
| --- | --- | --- |
| `looker` | Consume BI: models, explores, query, Looks, dashboards | 18 |
| `looker-dev` | LookML / git / connections / validate / health | 27 |
| `looker-conversational-analytics` | Conversational Analytics (needs extra GCP settings) | 3 |

This repo enables `looker,looker-dev` in `.cursor/mcp.json` (about **45** tools). `looker-dev` includes write/delete LookML and git tools — leave Cursor tool approval **on**.

There is **no** npm package named `@google-cloud/looker-mcp-server`. Using `npx` on that name fails with 404. The supported local server is the Toolbox binary.

## Setup

### 1. Python environment (for `main.py`)

```bash
python3 -m venv looker-env
./looker-env/bin/pip install -r requirements.txt
mkdir -p looker-env
cp .env.example looker-env/.env
# edit looker-env/.env with your keys
```

If `looker-env` already exists as a venv, just copy `.env.example` into `looker-env/.env`.

Run the explore listing (change `PROJECT_NAME` in `main.py` if needed):

```bash
./looker-env/bin/python main.py
```

A successful connection prints models and explores. Use the venv interpreter — system `python3` will not see `looker_sdk`.

### 2. MCP Toolbox binary (for Cursor)

On Apple Silicon macOS:

```bash
mkdir -p bin
curl -fsSL -o bin/toolbox \
  https://storage.googleapis.com/mcp-toolbox-for-databases/v1.0.0/darwin/arm64/toolbox
chmod +x bin/toolbox
./bin/toolbox --version
```

Other platforms (linux/amd64, darwin/amd64, windows) are listed in Google’s [MCP Toolbox Looker docs](https://docs.cloud.google.com/looker/docs/2608/connect-ide-to-looker-using-mcp-toolbox).

### 3. Cursor MCP

Cursor only loads MCP from:

- **Project:** `.cursor/mcp.json`
- **Global:** `~/.cursor/mcp.json`

A file named `mcp.json` at the **repo root is ignored** by Cursor. Copy the example:

```bash
mkdir -p .cursor
cp mcp.json.example .cursor/mcp.json
```

Example contents (no secrets; credentials come from `looker-env/.env`):

```json
{
  "mcpServers": {
    "looker": {
      "type": "stdio",
      "command": "${workspaceFolder}/bin/toolbox",
      "args": ["--stdio", "--prebuilt", "looker,looker-dev"],
      "envFile": "${workspaceFolder}/looker-env/.env"
    }
  }
}
```

Then:

1. Quit and reopen Cursor (MCP command/env changes are picked up at launch).
2. **Settings → Tools & MCP** — `looker` should be green.
3. Start a **new** Agent chat and ask, for example: “List models and explores in project `q_project`.”

If the server stays red: **Output → MCP Logs**. Toolbox checks Looker login at startup, so a bad URL or key fails immediately.

To expose only the 18 consumption tools, change `"looker,looker-dev"` to `"looker"`.

## How `main.py` works

1. Loads `looker-env/.env`.
2. Calls `looker_sdk.init40()` (API 4.0).
3. `sdk.all_lookml_models()`, keeps models whose `project_name` matches `PROJECT_NAME`.
4. Prints each model’s name, allowed DB connections, and explore name/label.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `ModuleNotFoundError: looker_sdk` | Ran system Python; use `./looker-env/bin/python` |
| MCP toggle error / 404 | Old `npx @google-cloud/looker-mcp-server` config |
| MCP red, toolbox logs login error | Wrong `LOOKER_*` values or SSL |
| Only 18 tools | `--prebuilt looker` without `looker-dev` |
| Cursor does not see MCP | Config not in `.cursor/mcp.json` |

## License

Use and modify as you like for your Looker workspace. MCP Toolbox itself is licensed by Google (Apache 2.0) — download the binary from their releases/storage, do not vendor a modified binary unless you follow that license.
