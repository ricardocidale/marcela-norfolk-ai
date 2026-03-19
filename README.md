# Marcela — Norfolk AI Voice & WhatsApp AI Agent

Marcela is Ricardo Cidale's personal AI assistant, built for Norfolk AI. She operates across two channels: **voice calls** and **WhatsApp messaging**, powered by Gemini 2.5 Flash with ultra-low-latency streaming.

*Powered by Norfolk AI*

---

## Architecture

Marcela uses a streaming-first architecture designed for sub-500ms response latency on voice calls.

| Component | Technology | Role |
|---|---|---|
| Speech-to-Text | Deepgram nova-3-general | Real-time transcription via ConversationRelay |
| Language Model | Gemini 2.5 Flash (streaming) | Conversational AI with streaming token output |
| Text-to-Speech | ElevenLabs Flash 2.5 | Ultra-low-latency voice synthesis |
| Voice Transport | Twilio ConversationRelay | WebSocket-based bidirectional audio streaming |
| WhatsApp | Twilio Messaging API | Webhook-based message handling with TwiML |

The voice call flow operates as follows: an incoming call hits Twilio, which connects to ConversationRelay. Deepgram transcribes the caller's speech in real time and sends it over a WebSocket to the Marcela server. The server streams the transcription to Gemini 2.5 Flash, which generates a response token-by-token. Each token is immediately sent back through the WebSocket to ConversationRelay, where ElevenLabs synthesizes speech on the fly. The result is a natural, low-latency conversational experience.

## Voice & Persona

Marcela's voice and tone are inspired by Mel Robbins: direct, warm, energetic, motivating, and confident. She speaks with authority and genuine care, using short punchy sentences mixed with deeper explanations when needed.

The ElevenLabs voice is configured with custom parameters for speed (1.05x), stability (0.55), and similarity (0.80) to achieve the right energy and expressiveness.

## Multilingual Support

Marcela automatically detects the language the caller is speaking and switches seamlessly mid-conversation. Priority languages are English, Portuguese (Brazilian), Italian, and Spanish, with support for any language Gemini 2.5 Flash handles. Language detection uses Deepgram's `multi` mode, and each priority language has a dedicated ElevenLabs voice configuration for natural-sounding TTS.

## Capabilities

Marcela can perform the following on voice calls:

1. **Call Filtering** — Asks the caller's name and purpose
2. **Call Transfer** — Offers to connect directly to Ricardo
3. **WhatsApp Handoff** — Suggests continuing via WhatsApp for text-based follow-up
4. **Meeting Booking** — Helps schedule meetings with Ricardo
5. **General Knowledge** — Answers questions about agentic AI, Norfolk AI, Super Conversations, Austin Texas, and Sao Paulo Brasil
6. **Thought Leadership** — Speaks knowledgeably about Ricardo Cidale's work in AI and Super Conversations

On WhatsApp, Marcela supports direct messaging, group chat triggers (@marcela, /ask, /quick, /translate), and maintains conversation history for natural multi-turn dialogue.

## Files

| File | Description |
|---|---|
| `voice_server.py` | Main server — Flask HTTP + WebSocket for ConversationRelay + Gemini streaming |
| `server.py` | WhatsApp-only server (legacy, for Vercel deployment) |
| `requirements.txt` | Python dependencies |

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `PUBLIC_WS_URL` | Public WebSocket URL for ConversationRelay (wss://...) |

## Running Locally

```bash
pip install flask websockets google-genai twilio
export GEMINI_API_KEY="your-key"
export TWILIO_ACCOUNT_SID="your-sid"
export TWILIO_AUTH_TOKEN="your-token"
python3 voice_server.py
```

The server starts two listeners: Flask HTTP on port 5005 (for TwiML webhooks and health checks) and a WebSocket server on port 8765 (for ConversationRelay).

## Phone Numbers

| Number | Purpose |
|---|---|
| +19109944861 | Marcela Voice AI (inbound calls) |
| +15559178507 | Marcela WhatsApp (messaging) |

---

*Powered by Norfolk AI*
