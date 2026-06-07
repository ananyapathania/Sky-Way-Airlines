"""SkyWay Elite — 3D AI Agent Gradio App."""
import os
from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from agent import AirlineAgent

agent = AirlineAgent()

# ── UI Theme ──────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* ═══════════════════════════════════════════════
   SKYWAY ELITE — Neo-Aviation Cockpit UI
   ═══════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

:root {
    --cyan:    #00f5ff;
    --gold:    #ffd700;
    --navy:    #050a1a;
    --panel:   rgba(0, 20, 50, 0.85);
    --border:  rgba(0, 245, 255, 0.35);
    --glow:    0 0 20px rgba(0, 245, 255, 0.4), 0 0 40px rgba(0, 245, 255, 0.15);
}

/* ── Body & Background ── */
body, .gradio-container {
    background: var(--navy) !important;
    font-family: 'Exo 2', sans-serif !important;
    color: #c8e6ff !important;
}

.gradio-container {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(0,80,160,0.18) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0,200,255,0.10) 0%, transparent 55%),
        linear-gradient(180deg, #020916 0%, #050a1a 100%) !important;
    min-height: 100vh;
}

/* ── CRT Scanline Overlay ── */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.05) 2px,
        rgba(0,0,0,0.05) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ── Header ── */
#header-row {
    background: linear-gradient(135deg, rgba(0,245,255,0.08), rgba(0,80,160,0.15));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 8px;
    box-shadow: var(--glow), inset 0 1px 0 rgba(0,245,255,0.2);
    transform: perspective(800px) rotateX(2deg);
    transition: transform 0.3s ease;
    position: relative;
    overflow: hidden;
}

#header-row::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,245,255,0.06), transparent);
    animation: scanlight 4s ease-in-out infinite;
}

@keyframes scanlight {
    0%   { left: -100%; }
    100% { left: 200%; }
}

/* ── Title ── */
#skyway-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, var(--cyan) 0%, #7df9ff 40%, var(--gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.12em;
    text-shadow: none;
    margin: 0 !important;
}

#skyway-subtitle {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.85rem !important;
    color: rgba(0,245,255,0.65) !important;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 4px !important;
}

/* ── Status Modules ── */
.status-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.status-pill {
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.15em;
    animation: pulse-glow 2.5s ease-in-out infinite;
}

.status-online  { background: rgba(0,255,100,0.12); border: 1px solid rgba(0,255,100,0.5); color: #00ff64; }
.status-engine  { background: rgba(0,245,255,0.10); border: 1px solid var(--border);       color: var(--cyan); }
.status-elite   { background: rgba(255,215,0,0.10);  border: 1px solid rgba(255,215,0,0.4); color: var(--gold); }

@keyframes pulse-glow {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.65; }
}

/* ── Chatbot Panel ── */
#chatbot-panel {
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    background: var(--panel) !important;
    box-shadow: var(--glow) !important;
    backdrop-filter: blur(12px) !important;
    transform: perspective(1200px) rotateX(1deg);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

#chatbot-panel:hover {
    transform: perspective(1200px) rotateX(0deg);
    box-shadow: 0 0 30px rgba(0,245,255,0.5), 0 0 60px rgba(0,245,255,0.2) !important;
}

/* ── Chat Messages ── */
.message.svelte-1pjfiar, .message {
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* User bubble */
.message.user, [data-testid="user"] .message {
    background: linear-gradient(135deg, rgba(0,100,200,0.3), rgba(0,60,130,0.4)) !important;
    border: 1px solid rgba(0,150,255,0.3) !important;
    color: #e0f4ff !important;
}

/* Bot bubble */
.message.bot, [data-testid="bot"] .message {
    background: linear-gradient(135deg, rgba(0,20,60,0.8), rgba(0,40,100,0.6)) !important;
    border: 1px solid var(--border) !important;
    color: #c8e6ff !important;
}

/* ── Input Area ── */
#input-row {
    background: rgba(0,15,40,0.7) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 12px !important;
    backdrop-filter: blur(8px) !important;
    box-shadow: inset 0 1px 0 rgba(0,245,255,0.1) !important;
}

#msg-input textarea {
    background: transparent !important;
    border: none !important;
    color: #c8e6ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 1rem !important;
    caret-color: var(--cyan) !important;
}

#msg-input textarea::placeholder {
    color: rgba(0,245,255,0.35) !important;
}

/* ── Buttons ── */
#send-btn button, #clear-btn button {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    border-radius: 10px !important;
    transition: all 0.25s ease !important;
    border: 1px solid !important;
}

#send-btn button {
    background: linear-gradient(135deg, rgba(0,245,255,0.15), rgba(0,100,200,0.25)) !important;
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
}

#send-btn button:hover {
    background: rgba(0,245,255,0.25) !important;
    box-shadow: 0 0 15px rgba(0,245,255,0.5) !important;
    transform: translateY(-1px) !important;
}

#clear-btn button {
    background: rgba(255,50,80,0.08) !important;
    border-color: rgba(255,80,100,0.4) !important;
    color: rgba(255,120,140,0.8) !important;
}

#clear-btn button:hover {
    background: rgba(255,50,80,0.18) !important;
    box-shadow: 0 0 12px rgba(255,50,80,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── Quick Actions Panel ── */
#quick-panel {
    background: rgba(0,15,40,0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    backdrop-filter: blur(8px) !important;
}

#quick-panel .label {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    color: rgba(0,245,255,0.5) !important;
    text-transform: uppercase !important;
}

/* ── Info Cards ── */
.info-card {
    background: rgba(0,20,55,0.7) !important;
    border: 1px solid rgba(0,245,255,0.15) !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.82rem !important;
    color: rgba(180,220,255,0.8) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

.info-card:hover {
    border-color: rgba(0,245,255,0.4) !important;
    box-shadow: 0 0 12px rgba(0,245,255,0.2) !important;
}

/* ── Tactical Corner Brackets ── */
#chatbot-panel::before, #chatbot-panel::after {
    content: '';
    position: absolute;
    width: 18px; height: 18px;
    border-color: var(--cyan);
    border-style: solid;
    opacity: 0.6;
}

#chatbot-panel::before {
    top: -1px; left: -1px;
    border-width: 2px 0 0 2px;
    border-radius: 4px 0 0 0;
}

#chatbot-panel::after {
    bottom: -1px; right: -1px;
    border-width: 0 2px 2px 0;
    border-radius: 0 0 4px 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: rgba(0,10,30,0.5); }
::-webkit-scrollbar-thumb { background: rgba(0,245,255,0.25); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,245,255,0.45); }
"""

# ── Gradio App ────────────────────────────────────────────────────────────────
TITLE_HTML = """
<div id="header-row">
  <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
    <div>
      <div style="display:flex; align-items:center; gap:14px;">
        <span style="font-size:2rem;">✈️</span>
        <div>
          <p id="skyway-title">SKYWAY ELITE</p>
          <p id="skyway-subtitle">3D Neo-Aviation AI Support Agent</p>
        </div>
      </div>
    </div>
    <div class="status-bar">
      <span class="status-pill status-online">● ONLINE</span>
      <span class="status-pill status-engine">⚡ DUAL ENGINE</span>
      <span class="status-pill status-elite">💎 ELITE CLASS</span>
    </div>
  </div>
</div>
"""

QUICK_ACTIONS = [
    ("✈️ Search Flights", "Search flights from JFK to LHR on 2026-12-20 in business class"),
    ("📡 Flight Status",  "Check status of flight SW202"),
    ("🌍 List Airports",  "Show all supported airports"),
    ("🧳 Baggage Policy", "What is the baggage policy for first class?"),
    ("📋 My Booking",     "Retrieve booking SWAB1234"),
    ("💰 Fare Calculator","Calculate fare for SW101 in business class for 2 seats"),
]

INFO_TEXT = """
**SkyBot** is powered by a dual-engine AI backend:

- 🚀 **Primary:** Groq Llama-3.3 (ultra-fast inference)
- 🧠 **Fallback:** Google Gemini 2.0 Flash

**Supported Routes:**
JFK · LAX · LHR · DXB · SIN · CDG · HND · SYD · ORD · BOM · DEL

**Capabilities:**
✈️ Flight Search | 🎫 Booking | 📡 Status
❌ Cancellation | 🧳 Baggage | 💰 Fares
"""

def _to_legacy(history):
    """Convert Gradio 6 messages-format history to legacy [[user, bot], ...] for agent."""
    legacy = []
    for m in history:
        if m.get("role") == "user":
            legacy.append([m["content"], None])
        elif m.get("role") == "assistant" and legacy:
            legacy[-1][1] = m["content"]
    return legacy

def respond(message, history):
    if not message.strip():
        return history, ""
    reply = agent.chat(message, _to_legacy(history))
    history = history + [
        {"role": "user",      "content": message},
        {"role": "assistant", "content": reply},
    ]
    return history, ""

def clear_chat():
    return [
        {"role": "assistant", "content": "👋 Welcome aboard **SkyWay Elite**! I'm **SkyBot**, your AI travel assistant.\n\nI can help you **search flights**, **book**, **check status**, **manage bookings**, and more.\n\nHow can I assist you today? ✈️"}
    ], ""

def quick_send(msg, history):
    reply = agent.chat(msg, _to_legacy(history))
    return history + [
        {"role": "user",      "content": msg},
        {"role": "assistant", "content": reply},
    ], ""

with gr.Blocks(title="SkyWay Elite | 3D AI Agent") as demo:

    gr.HTML(TITLE_HTML)

    with gr.Row():
        # ── Main Chat Column ──────────────────────────────────
        with gr.Column(scale=7):
            chatbot = gr.Chatbot(
                value=[{"role": "assistant", "content": "👋 Welcome aboard **SkyWay Elite**! I'm **SkyBot**, your AI travel assistant.\n\nI can help you **search flights**, **book**, **check status**, **manage bookings**, and more.\n\nHow can I assist you today? ✈️"}],
                type="messages",
                height=520,
                elem_id="chatbot-panel",
                show_label=False,
                avatar_images=(None, "https://em-content.zobj.net/source/google/387/robot_1f916.png"),
            )

            with gr.Row(elem_id="input-row"):
                msg_input = gr.Textbox(
                    placeholder="⌨️  Type your query (e.g. 'Search JFK to DXB on 2026-11-15')...",
                    show_label=False,
                    scale=8,
                    elem_id="msg-input",
                    lines=1,
                    max_lines=3,
                )
                with gr.Column(scale=1, min_width=90):
                    send_btn  = gr.Button("▶ SEND",  elem_id="send-btn",  variant="primary")
                    clear_btn = gr.Button("✕ CLEAR", elem_id="clear-btn", variant="secondary")

        # ── Sidebar Column ────────────────────────────────────
        with gr.Column(scale=3):
            with gr.Group(elem_id="quick-panel"):
                gr.Markdown("#### 🎯 Quick Actions", elem_classes=["label"])
                for label, cmd in QUICK_ACTIONS:
                    btn = gr.Button(label, size="sm")
                    btn.click(
                        fn=quick_send,
                        inputs=[gr.State(cmd), chatbot],
                        outputs=[chatbot, msg_input]
                    )

            gr.Markdown(INFO_TEXT, elem_classes=["info-card"])

    # ── Event Bindings ──
    send_btn.click(respond,  inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])
    msg_input.submit(respond, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])
    clear_btn.click(clear_chat, outputs=[chatbot, msg_input])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        favicon_path=None,
        css=CUSTOM_CSS,
        theme=gr.themes.Base(),
    )
