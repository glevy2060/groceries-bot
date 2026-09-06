# Groceries Bot

A household grocery assistant. You and your husband message it to keep a shared
grocery list up to date, then ask it to execute the order.

## Roadmap

- **Phase 1 ✅** — naive markdown-file database, a Claude-powered agent that
  understands natural-language messages via tool use, exposed both as a REST API
  and a local CLI chat.
- **Phase 2 ✅** — `execute_order` creates a real cart on Rami Levy (using your
  saved credentials) and returns a checkout link. Two-step flow: search catalog
  for products, show top matches, user confirms selections, cart created.
- **Phase 3** — wire the agent into a shared WhatsApp group so you and your
  husband message it directly.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# then edit .env and set both ANTHROPIC_API_KEY and RAMI_LEVY_AUTH_TOKEN
```

### Getting your Rami Levy auth tokens & cookies

1. Log into https://www.rami-levy.co.il
2. Open DevTools (F12) → Network tab
3. Make any request (e.g., search for a product or view cart)
4. Find the request, inspect the request headers:
   - **Authorization**: Copy everything after `Bearer ` (e.g., `eyJ...`) → `RAMI_LEVY_AUTH_TOKEN`
   - **ecomtoken**: If present in headers → `RAMI_LEVY_ECOM_TOKEN`
   - **Cookie**: Copy the full value → `RAMI_LEVY_COOKIES`

5. Paste these into `.env`:
```
RAMI_LEVY_AUTH_TOKEN=eyJ...
RAMI_LEVY_ECOM_TOKEN=...
RAMI_LEVY_COOKIES=...
```

Only `RAMI_LEVY_AUTH_TOKEN` is required; the other two are optional but recommended for reliability.

(Tokens may expire periodically — if `execute_order` fails with "auth failed", refresh using the same steps.)

## Usage

**CLI chat (fastest way to try it):**

```bash
python -m app.cli
```

Example conversation:
```
you> add 2 milk and a dozen eggs
agent> Added 2 milk and 12 eggs to the list!

you> execute the order
agent> 🛒 Found products for your order:
**חלב** (qty: 2):
  1. חלב טרי 3% 1L (₪8.99) [ID: 12345]
  2. חלב טרי 1.5% 1L (₪7.99) [ID: 67890]
  3. חלב צמחי אגוז קוקוס 1L (₪13.99) [ID: 11111]
...
Please confirm by listing the product IDs you want (e.g., "use 12345 for חלב, 67890 for ביצים").

you> use 12345 for milk and 99999 for eggs
agent> ✅ Cart created! Complete checkout here: https://www.rami-levy.co.il/he/dashboard/checkout
```

**REST API:**

```bash
uvicorn app.api:app --reload
```

- `POST /chat` — `{"message": "add 2 milk", "session_identifier": "household"}` → `{"reply": "..."}`
- `GET /items` — current grocery list as JSON

Both entry points share the same agent and read/write `data/groceries.md`,
which you can also open and edit directly since it's just a markdown file.

## Tests

```bash
pytest
```
