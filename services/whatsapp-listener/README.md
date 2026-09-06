# WhatsApp Listener Service

Listens to WhatsApp group messages and forwards them to the groceries bot Python API.

## Setup

```bash
# Install Node.js dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env and set:
# - TARGET_GROUP_NAME: your WhatsApp group name (default: "קניות")
# - PYTHON_API_URL: where the Python API is running (default: http://localhost:8000)
```

## Running

```bash
npm start
```

On first run, you'll see a QR code. Scan it with WhatsApp to authenticate. The session is saved locally, so you only need to scan once.

The service will:
- Listen for all messages in the target group
- Send them to `http://localhost:8000/whatsapp/message`
- Post the Python API's reply back to WhatsApp

## How it works

1. WhatsApp message arrives in the group
2. `listener.js` receives it via `whatsapp-web.js`
3. Posts to Python API endpoint `/whatsapp/message`
4. Python agent processes and returns reply
5. Reply sent back to WhatsApp group

## Troubleshooting

- **QR code not showing**: Make sure terminal supports Unicode. Try running in a different terminal.
- **Connection refused**: Make sure Python API is running on the configured port
- **Messages not received**: Check `TARGET_GROUP_NAME` matches exactly (case-sensitive)
- **Session expired**: Delete `.wppconnect/` and re-scan the QR code
