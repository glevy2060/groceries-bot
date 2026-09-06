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
- **Phase 3 ✅** — wire the agent into a shared WhatsApp group ("קניות") so you and your
  husband message it directly. Hybrid Node.js (WhatsApp Web) + Python (agent logic).

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
agent> Here are the top matches:

**חלב** (qty: 2):
1. חלב תנובה 3% שומן 2 ל' – ₪14.9 [457691]
2. חלב נטול לקטוז וויטמין 1ל טרה – ₪9.3 [398234]
3. חלב מועשר 2 ל 3% יטבתה – ₪16.7 [31680]

**לחם** (qty: 1):
1. לחם אחיד פרוס 900 ג רמי לוי – ₪8.3 [397356]
2. לחם כוסמין קל 600 גר – ₪16.1 [404583]
3. לחם אחיד פרוס אנג'ל – ₪8.3 [397353]

Which product IDs would you like to use for each?

you> use 457691 for חלב and 397356 for לחם
agent> Your order is ready! 🛒

- 2x חלב תנובה 3% (₪14.9 each)
- 1x לחם אחיד פרוס רמי לוי (₪8.3)

Complete your purchase here: https://www.rami-levy.co.il/he/dashboard/checkout
```

**REST API:**

```bash
uvicorn app.api:app --reload
```

- `POST /chat` — `{"message": "add 2 milk", "session_identifier": "household"}` → `{"reply": "..."}`
- `GET /items` — current grocery list as JSON

Both entry points share the same agent and read/write `data/groceries.md`,
which you can also open and edit directly since it's just a markdown file.

**WhatsApp (full household integration):**

Run both services in separate terminals:

Terminal 1 (Python API):
```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Terminal 2 (WhatsApp listener):
```bash
cd services/whatsapp-listener
npm install  # first time only
cp .env.example .env  # first time only
npm start
```

On first run, scan the QR code with WhatsApp. Then message the "קניות" group, and the
bot will listen and respond automatically. All messages are processed by the Python
agent, so it works exactly like the CLI but in your WhatsApp group.

## Tests

```bash
pytest
```
