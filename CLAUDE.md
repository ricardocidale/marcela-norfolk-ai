# Marcela — Norfolk AI AI Agent

## Project Overview

Marcela is Ricardo Cidale's personal AI assistant, built for Norfolk AI. She operates across two channels: **voice calls** (inbound phone) and **WhatsApp messaging**. The project has gone through multiple architectural iterations, platform migrations, and debugging cycles documented below.

**Owner**: Ricardo Cidale, Founder & CEO of Norfolk AI (Austin, TX)
**Repository**: `ricardocidale/marcela-norfolk-ai` (private)

---

## Architecture Summary

| Component | Technology | Deployment |
|---|---|---|
| WhatsApp Agent | Flask + Gemini 2.5 Flash (direct HTTP) | Vercel Serverless (`api/index.py`) |
| Voice Agent | Starlette + Gemini 2.5 Flash (streaming) + ConversationRelay | Railway (Docker container) |
| STT | Deepgram nova-3-general | Via Twilio ConversationRelay |
| TTS | ElevenLabs Flash 2.5 | Via Twilio ConversationRelay |
| LLM | Google Gemini 2.5 Flash | Direct API (WhatsApp) / google-genai SDK (Voice) |
| Telephony | Twilio | WhatsApp Messaging + Voice ConversationRelay |

### Phone Numbers

| Number | Purpose | Status |
|---|---|---|
| +15559178507 | Marcela WhatsApp (messaging) | **BLOCKED — Error 63112** (see Critical Issues) |
| +19109944861 | Marcela Voice AI (inbound calls) + Norfolk AI Voice Digest | Voice Digest sender is Offline |
| +15126699705 | Ricardo's personal number | Active |

### Deployment URLs

| Service | URL |
|---|---|
| WhatsApp webhook (Vercel) | `https://marcela-norfolk-ai.vercel.app/webhook` |
| Health check (Vercel) | `https://marcela-norfolk-ai.vercel.app/health` |
| Voice server (Railway) | Configured via `PUBLIC_URL` env var |

---

## Critical Issues (Current)

### WhatsApp Error 63112 — Meta/WABA Disabled

**Status**: UNRESOLVED as of March 2026

All outbound WhatsApp messages from Marcela fail with **Twilio Error 63112**:

> "The Meta and/or WhatsApp Business Accounts connected to this Sender were disabled by Meta or your business verification request is currently pending."

**Key findings from investigation (April 2026)**:

- The Vercel deployment and code are **working correctly** — webhook processes messages, Gemini generates responses, TwiML is returned properly
- Inbound WhatsApp messages ARE received successfully (status: "received")
- Every outbound message fails with error 63112, direction "outbound-api"
- The WhatsApp sender `+15559178507` shows as **Online** with **High** quality rating in Twilio console
- However, **Messaging limits: Unavailable** on the WABA (ID: 446936301829143)
- This is a **Meta/Facebook-side block**, not a code or Twilio issue

**To resolve**: Ricardo must log into Meta Business Suite (business.facebook.com), navigate to Business Settings > WhatsApp Accounts, check the WABA status, and complete business verification or submit an appeal if the account was disabled.

**This cannot be fixed with code changes.** Multiple code-level attempts were already made (see Failed Attempts below).

### Norfolk AI Voice Digest Sender Offline

The second WhatsApp sender `+19109944861` (Norfolk AI Voice Digest) shows **Offline** status in Twilio with **Unknown** quality rating. This number is also the voice line.

---

## File Map

| File | Description |
|---|---|
| `server.py` | WhatsApp-only Flask server (Gemini via direct HTTP, no SDK) |
| `api/index.py` | Vercel serverless entry point — mirrors `server.py` for Vercel deployment |
| `voice_server.py` | Voice + WhatsApp Starlette server (Gemini via google-genai SDK, streaming) |
| `create_elevenlabs_agent.py` | Script to create ElevenLabs ConvAI agent via API (historical) |
| `marcela_agent_config.json` | Agent metadata: IDs, phone numbers, capabilities |
| `prompts/marcela-voice-prompt.txt` | Production voice prompt with call screening logic |
| `prompts/marcela-context.txt` | Background context about Ricardo, Norfolk AI, Super Conversations |
| `marcela-profile.png` | Marcela's WhatsApp profile image |
| `BrandguidelineNorfolkAI.pdf` | Norfolk AI brand guidelines |
| `vercel.json` | Vercel deployment config (routes all to `api/index.py`) |
| `Dockerfile` | Container build for Railway deployment |
| `railway.toml` | Railway deployment config |
| `Procfile` | Process declaration for Railway |
| `requirements.txt` | Python dependencies |
| `runtime.txt` | Python runtime version spec |

---

## Complete Project History

### Phase 1: Initial WhatsApp Agent (March 17, 2026)

**Commit**: `b22d315` — Initial commit

- Built Marcela as a WhatsApp AI agent using **Anthropic Claude** as the LLM and **Twilio Python SDK** for messaging
- Used `+15126699705` (Ricardo's personal number) as the WhatsApp sender
- Basic webhook architecture: receive message → call Claude → send response via Twilio API

### Phase 2: Sender Number Changes (March 18, 2026)

**Commits**: `0082827`, `8f457d1`, `9a9a45b`

- Changed sender from Ricardo's personal number to `+19109944861` (the Twilio voice number)
- Added Vercel serverless deployment config (`vercel.json`, `api/index.py`)
- Later changed sender to `+15559178507` (dedicated WhatsApp Business number)

### Phase 3: Group Chat Features (March 18, 2026)

**Commits**: `4a2ab03`, `57cce5b`

- Added `@Marcela` mention-based trigger for group chats (silent unless called)
- Added slash commands: `/ask`, `/quick`, `/translate`
- Added natural mention triggers (regex-based detection)

### Phase 4: Vercel Compatibility Fixes — FAILED ATTEMPTS (March 18, 2026)

**Commits**: `75142cb`, `25a8b17`, `4f90d01`

This was a series of cascading failures caused by Vercel's serverless environment:

1. **Failed**: Twilio Python SDK caused `httpx` version conflict on Vercel. Tried lazy-init clients and pinning twilio version — did not resolve.
2. **Failed**: Tried replacing both Anthropic and Twilio SDKs with direct HTTP requests — partially worked but Anthropic API still had issues.
3. **Resolution**: Switched entirely from Anthropic Claude to **Google Gemini 2.5 Flash** using direct HTTP requests (no SDK). This eliminated all dependency conflicts on Vercel.

**Lesson learned**: Vercel serverless functions have strict dependency constraints. Avoid heavy SDKs (anthropic, twilio) — use direct HTTP requests instead. The Gemini API is lightweight and works well with simple `requests` calls.

### Phase 5: Error 63112 — TwiML Fix Attempt (March 18, 2026)

**Commit**: `7a60a6c` — "fix: respond via inline TwiML instead of Twilio API to avoid error 63112"

- Outbound WhatsApp messages started failing with error 63112
- **Attempted fix**: Changed from sending responses via Twilio REST API (`send_whatsapp_message()`) to returning inline TwiML responses (`message_twiml()`) from the webhook
- **Result**: DID NOT FIX THE ISSUE. Twilio internally converts TwiML responses to API calls, so the same 63112 error occurs. The error is at the Meta/WABA level, not the Twilio API level.

**Lesson learned**: Error 63112 cannot be fixed with code changes. It means Meta has disabled the WhatsApp Business Account. The fix must happen in Meta Business Suite.

### Phase 6: Voice Agent Development (March 19, 2026)

**Commits**: `2b343e0`, `c02a8f0`, `ec8ee8b`, `da0b88e`, `b8e4378`

- Built Marcela Voice AI Agent using Twilio ConversationRelay + Gemini 2.5 Flash streaming
- Architecture: Caller → Twilio → ConversationRelay (Deepgram STT) → WebSocket → Gemini streaming → WebSocket → ConversationRelay (ElevenLabs TTS) → Caller
- Refactored to single-port architecture (HTTP + WebSocket on same port) for Railway compatibility
- Added Dockerfile for container deployment
- Multiple fixes for form parsing, python-multipart dependency, API key auth, and error handling on Railway

**Failed attempts during voice development**:
- Initially tried separate ports for HTTP (5005) and WebSocket (8765) — failed on Railway which only exposes one port
- Form parsing broke on Railway due to missing `python-multipart` package
- Had to add robust try/except with fallback URL-encoded body parsing

### Phase 7: ElevenLabs ConvAI Agent (March 19, 2026)

**Commit**: `fe4f37f`

- Created an ElevenLabs Conversational AI agent as an alternative/complement to the custom voice server
- Agent ID: `agent_5401km3m8hfrer5rmpetb7wefdyt`
- Uses Qwen3-30B-A3B model (chosen for speed — output tokens matter 50x more than prompt size for latency)
- Voice: Jessica Anne Bogart - Chatty
- Includes simulation tests for call screening scenarios

### Phase 8: Documentation (March 19, 2026)

**Commit**: `1d02950`

- Added initial CLAUDE.md with project learnings
- Updated voice prompt and context files

---

## Prompt Engineering Learnings

### Call Screening Architecture

The voice prompt uses a layered screening system: Always Transfer → Transfer if Qualified → Never Transfer → Borderline. The critical discovery was that without an explicit **priority rule** ("one disqualifying signal overrides all qualifying ones"), the LLM would rationalize transfers for borderline callers who mixed qualifying and disqualifying signals.

### Data Collection Discipline

The agent must be explicitly instructed to collect name, title, company, and email EARLY in the conversation. Without timing instructions, the agent gets engaged in the conversation content and forgets administrative tasks. The prompt now includes: "Never end a call without having collected the caller's email."

### Sales Detection

An explicit step ("Is this person selling something?") is required in the screening flow. The LLM will not reliably infer that a "partnership opportunity" or "collaboration" pitch is actually a sales call without being told to check.

### Conference Contacts

Meeting someone at a conference does NOT make them an existing client. This had to be stated explicitly — the LLM would otherwise treat conference encounters as qualifying relationships.

### Test-Driven Prompt Development

The most effective workflow: write prompt → create simulation tests → run → analyze failures → fix prompt → re-run failing tests. Each iteration improved pass rate from 2/4 to 3/4 to 4/4.

---

## Latency Optimization (Voice)

- Output token reduction has approximately 50x more impact on latency than system prompt size
- ElevenLabs has best-in-class latency at sub-500ms (vs VAPI ~500ms, Retell ~800ms, Bland AI ~800-2500ms)
- Turn detection/endpointing is the highest-impact optimization area
- Keep agent responses to 1-2 sentences per turn
- Streaming token delivery at sentence boundaries produces the most natural speech

---

## Integrations

| Integration | Purpose | Status |
|---|---|---|
| HubSpot (via Zapier) | CRM logging after each call | Configured |
| Gmail (via Zapier) | Follow-up emails on Ricardo's behalf | Configured |
| Google Calendar (via Zapier) | Meeting booking | Needs OAuth reconnection (3 accounts) |
| Slack | High-priority notifications to Ricardo | Configured |

---

## Environment Variables

### WhatsApp (Vercel)

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID: `AC2354928595411f3e4156a44683af210d` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `WHATSAPP_SENDER` | `whatsapp:+15559178507` |

### Voice (Railway)

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_API_KEY` | Twilio API Key (for ConversationRelay) |
| `TWILIO_API_SECRET` | Twilio API Secret |
| `PUBLIC_URL` | Public WSS URL for ConversationRelay |
| `PORT` | Server port (default: 5005) |

---

## Twilio Account Details

| Item | Value |
|---|---|
| Account SID | `AC2354928595411f3e4156a44683af210d` |
| WABA ID | `446936301829143` |
| Messaging Service (Marcela) | `MG5749f41a32f687f44e27d73f4d11baa9` |
| Messaging Service (empty, March 18) | `MG21f0694cd1b2566a13873571d2106728` — created accidentally, has no senders |
| WhatsApp Content Template | `HXf0178fa997208550fc9ea2a64e0b2b91` (norfolk_ai_digest_welcome, approved) |

---

## Key Decisions and Rationale

1. **Gemini over Claude for WhatsApp**: Switched from Anthropic Claude to Gemini 2.5 Flash because Anthropic SDK caused dependency conflicts on Vercel. Gemini works with simple HTTP requests.

2. **Direct HTTP over SDKs**: Both Twilio and Anthropic Python SDKs caused issues on Vercel serverless. Using `requests` library for direct HTTP calls is more reliable in constrained environments.

3. **TwiML over REST API for responses**: The webhook returns inline TwiML `<Response><Message>` instead of using the Twilio REST API to send messages. This was an attempt to avoid error 63112 (did not work — the error is Meta-level, not API-level).

4. **Single-port architecture for voice**: Railway only exposes one port. Refactored from separate Flask (5005) + WebSocket (8765) to unified Starlette server handling both HTTP and WebSocket on the same port.

5. **Qwen3-30B-A3B for ElevenLabs agent**: Chosen over larger models because output token generation speed is the dominant factor in voice latency, not prompt processing speed.

6. **Sentence-boundary streaming**: Voice responses are streamed to ConversationRelay at sentence boundaries (`. `, `! `, `? `) rather than token-by-token, producing more natural-sounding speech.

---

## Pending Work

- **CRITICAL**: Resolve Meta/WABA error 63112 — requires action in Meta Business Suite (business.facebook.com > Business Settings > WhatsApp Accounts)
- Google Calendar OAuth reconnection (3 accounts — Ricardo must do manually)
- Clean up the empty messaging service `MG21f0694cd1b2566a13873571d2106728`
- Bring Norfolk AI Voice Digest sender (`+19109944861`) back online
- Known-numbers spreadsheet (Google Drive)
- Widget deployment to norfolk.ai
- Final end-to-end verification via actual phone call
- A2P Campaign registration for US long code (Twilio is prompting for this)

---

## Common Pitfalls (for Future Agents)

1. **Do NOT try to fix error 63112 with code changes.** It is a Meta/WABA-level block. The WhatsApp Business Account must be unblocked in Meta Business Suite.

2. **Do NOT use Twilio or Anthropic Python SDKs on Vercel.** They cause dependency conflicts. Use direct HTTP requests.

3. **Do NOT use separate ports on Railway.** Only one port is exposed. Use a single-port server (Starlette handles HTTP + WebSocket on one port).

4. **Do NOT forget `python-multipart` in requirements.txt** when using Starlette/FastAPI form parsing.

5. **Do NOT assume TwiML bypasses Twilio API restrictions.** Twilio processes TwiML and sends messages via its internal API — the same restrictions apply.

6. **Do NOT skip early data collection in voice prompts.** Without explicit timing instructions, the LLM forgets to collect caller name/email.

7. **The `send_whatsapp_message()` function in server.py is dead code.** The webhook now uses TwiML responses. The function remains for potential future use but is not called.

8. **Conversation history is in-memory and resets on cold start.** This is acceptable for Vercel (stateless) and Railway (infrequent restarts) but means conversations do not persist across deployments.

---

## Voice AI Community Intelligence

- **Pipecat AI Discord** (17k+ users): Largest open voice AI community
- **Key insight**: Endpointing (turn detection) is the most-discussed optimization challenge across all platforms
- **Platform comparison**: ElevenLabs most stable; VAPI most active dev community; Retell and Bland have more latency complaints
