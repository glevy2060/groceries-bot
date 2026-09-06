# Groceries Bot

A household grocery assistant. You and your husband message it to keep a shared
grocery list up to date, then ask it to execute the order.

## Roadmap

- **Phase 1 (this)** — naive markdown-file database, a Claude-powered agent that
  understands natural-language messages via tool use, exposed both as a REST API
  and a local CLI chat.
- **Phase 2** — `execute_order` creates a real cart on Rami Levy (using your
  saved credentials) and returns a checkout link instead of the current stub.
- **Phase 3** — wire the agent into a shared WhatsApp group so you and your
  husband message it directly.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY
```

## Usage

**CLI chat (fastest way to try it):**

```bash
python -m app.cli
```

**REST API:**

```bash
uvicorn app.api:app --reload
```

- `POST /chat` — `{"message": "add 2 milk and a bag of bread"}` → `{"reply": "..."}`
- `GET /items` — current grocery list as JSON

Both entry points share the same agent and read/write `data/groceries.md`,
which you can also open and edit directly since it's just a markdown file.

## Tests

```bash
pytest
```
