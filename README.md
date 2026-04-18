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
| WhatsApp | Twilio Messaging + TwiML | Webhook-based message handling with inline TwiML responses |

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
| `voice_server.py` | Main voice server — Starlette HTTP + WebSocket (single port) for ConversationRelay + Gemini streaming |
| `server.py` | WhatsApp-only Flask server (Gemini via direct HTTP, no SDK) |
| `api/index.py` | Vercel serverless entry point — mirrors `server.py` |
| `create_elevenlabs_agent.py` | ElevenLabs ConvAI agent creation script |
| `marcela_agent_config.json` | Agent metadata and configuration |
| `prompts/marcela-voice-prompt.txt` | Production voice prompt with call screening logic |
| `prompts/marcela-context.txt` | Background context about Ricardo, Norfolk AI, Super Conversations |
| `skills/` | Agent Skills (SKILL.md) for WhatsApp and Voice agents |
| `CLAUDE.md` | Comprehensive project history, learnings, and instructions for AI agents |

## Environment Variables

| Variable | Description | Used By |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key | Both |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Both |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Both |
| `TWILIO_API_KEY` | Twilio API Key | Voice |
| `TWILIO_API_SECRET` | Twilio API Secret | Voice |
| `PUBLIC_URL` | Public WSS URL for ConversationRelay | Voice |
| `PORT` | Server port (default: 5005) | Voice |
| `WHATSAPP_SENDER` | WhatsApp sender number | WhatsApp |

## Running Locally

### WhatsApp Agent (Flask)

```bash
pip install flask requests
export GEMINI_API_KEY="your-key"
python3 server.py
```

Server starts on port 5005. Use ngrok or similar to expose the webhook.

### Voice Agent (Starlette)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
export PUBLIC_URL="wss://your-public-url"
python3 voice_server.py
```

Single-port server handles HTTP + WebSocket on port 5005.

## Phone Numbers

| Number | Purpose | Deployment |
|---|---|---|
| +19109944861 | Marcela Voice AI (inbound calls) | Railway |
| +15559178507 | Marcela WhatsApp (messaging) | Vercel |

---

*Powered by Norfolk AI*
