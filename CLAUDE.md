# Marcela — Norfolk AI Voice Agent

## Project Overview
Marcela is Ricardo Cidale's personal AI phone assistant, built on ElevenLabs Conversational AI. She handles inbound calls to Norfolk AI, screens callers, answers questions about the company, books meetings, and transfers only genuinely qualified calls to Ricardo.

## Architecture
- **Platform**: ElevenLabs Conversational AI (ConvAI)
- **Agent ID**: `agent_5401km3m8hfrer5rmpetb7wefdyt`
- **Phone**: +1 910 994 4861
- **Voice**: Jessica Anne Bogart - Chatty
- **LLM**: Qwen3-30B-A3B (chosen for speed — output tokens matter 50x more than prompt size for latency)
- **Languages**: English (default), Portuguese, Spanish, Italian

## Key Files
- `marcela-voice-prompt.txt` — The production system prompt (push to ElevenLabs via PATCH API)
- `marcela-context.txt` — Background context about Ricardo, Norfolk AI, and Super Conversations
- `create_elevenlabs_agent.py` — Agent creation script
- `voice_server.py` — Voice server integration
- `server.py` — WhatsApp integration server

## Prompt Engineering Learnings

### Call Screening Architecture
The prompt uses a layered screening system: Always Transfer → Transfer if Qualified → Never Transfer → Borderline. The critical discovery was that without an explicit **priority rule** ("one disqualifying signal overrides all qualifying ones"), the LLM would rationalize transfers for borderline callers who mixed qualifying and disqualifying signals.

### Data Collection Discipline
The agent must be explicitly instructed to collect name, title, company, and email EARLY in the conversation. Without timing instructions, the agent gets engaged in the conversation content and forgets administrative tasks. The prompt now includes: "Never end a call without having collected the caller's email."

### Sales Detection
An explicit step ("Is this person selling something?") is required in the screening flow. The LLM won't reliably infer that a "partnership opportunity" or "collaboration" pitch is actually a sales call without being told to check.

### Conference Contacts
Meeting someone at a conference does NOT make them an existing client. This had to be stated explicitly — the LLM would otherwise treat conference encounters as qualifying relationships.

## Testing

### Simulation Tests (ElevenLabs)
Four simulation tests are attached to the agent:
- **SIM-01**: Cold sales call — full screening and block
- **SIM-02**: C-level exec with urgent need — proper transfer
- **SIM-03**: Borderline call — message taking instead of transfer
- **SIM-04**: General inquiry about Norfolk AI — Marcela handles directly

Tests created via API (`POST /v1/convai/agent-testing/create`) because the UI has form carryover bugs. Tests attached to agent via UI dropdown.

### Test-Driven Prompt Development
The most effective workflow: write prompt → create simulation tests → run → analyze failures → fix prompt → re-run failing tests. Each iteration improved pass rate:
- Run 1: 2/4 pass (SIM-01 transferred a disguised sales call, SIM-03 transferred a borderline caller)
- Run 2: 2/4 pass (SIM-01 timed out, SIM-03 still transferred)
- Run 3: 3/4 pass (SIM-01 fixed by priority rule, SIM-03 still failing on data collection)
- Run 4: SIM-03 re-running with early data collection + end-of-call safeguards

## Latency Optimization
- Output token reduction has ~50x more impact on latency than system prompt size
- ElevenLabs has best-in-class latency at sub-500ms (vs VAPI ~500ms, Retell ~800ms, Bland AI ~800-2500ms)
- Turn detection/endpointing is the highest-impact optimization area
- Keep agent responses to 1-2 sentences per turn

## Integrations (via Zapier MCP)
- **HubSpot**: CRM logging after each call
- **Gmail**: Follow-up emails on Ricardo's behalf
- **Google Calendar**: Meeting booking (needs OAuth reconnection for 3 accounts)
- **Slack**: High-priority notifications to Ricardo

## Pending Work
- Google Calendar OAuth reconnection (3 accounts — Ricardo must do manually)
- Known-numbers spreadsheet (Google Drive)
- Widget deployment to norfolk.ai
- Final end-to-end verification via actual phone call

## Voice AI Community Intelligence
- **Pipecat AI Discord** (17k+ users): Largest open voice AI community
- **Key insight**: Endpointing (turn detection) is the most-discussed optimization challenge across all platforms
- **Platform comparison**: ElevenLabs most stable; VAPI most active dev community; Retell and Bland have more latency complaints
