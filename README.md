# Marcela — Norfolk AI WhatsApp AI Agent

Marcela is a Claude-powered intelligent AI assistant for Norfolk AI, accessible directly via WhatsApp. She is designed to be warm, sharp, and professional, providing conversational assistance, strategic advice, and research capabilities.

## Features

- **WhatsApp Integration**: Receives and responds to messages via the Twilio WhatsApp API.
- **Claude Intelligence**: Powered by Anthropic's Claude model (`claude-sonnet-4-20250514`), offering advanced reasoning, writing, and analytical capabilities.
- **Contextual Memory**: Maintains conversation history (up to 10 exchanges per user) to ensure natural, flowing interactions.
- **Long Message Handling**: Automatically splits long responses to comply with Twilio's WhatsApp message length limits.

## Prerequisites

- Python 3.8+
- A Twilio account with a configured WhatsApp sender number
- An Anthropic API key

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ricardocidale/marcela-norfolk-ai.git
   cd marcela-norfolk-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install flask twilio anthropic
   ```

3. **Configure Environment Variables**:
   Set your Anthropic API key as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

4. **Update Configuration (if needed)**:
   In `server.py`, ensure the following variables match your Twilio setup:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `WHATSAPP_SENDER`

## Running the Server

Start the Flask webhook server:

```bash
python3 server.py
```

The server will run on port `5005` by default.

## Exposing the Webhook

To receive messages from Twilio, your server must be publicly accessible. You can use tools like `ngrok` or deploy the application to a cloud provider.

Example using ngrok:
```bash
ngrok http 5005
```

Once you have a public URL, configure your Twilio WhatsApp sender's webhook URL to point to `https://<your-public-url>/webhook`.

## Architecture

- **`server.py`**: The main Flask application that handles incoming webhooks, manages conversation history, communicates with the Anthropic API, and sends responses back via Twilio.

## License

Private repository for Norfolk AI.
