---
title: SkyWay Elite 3D AI Agent
emoji: ✈️
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# ✈️ SkyWay Elite: ULTRA 3D AI Support Agent

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-6.0-orange.svg)](https://gradio.app/)
[![AI Engine](https://img.shields.io/badge/AI_Engine-Gemini_/_Groq-blueviolet.svg)](https://groq.com/)

**SkyWay Elite** is a production-grade, multi-modal AI chatbot designed for high-end airline support. It features a stunning **3D Neo-Aviation Cockpit** interface and is powered by a dual-engine AI backend (Gemini 2.0 & Groq Llama 3.3) with advanced function calling capabilities.

## 🚀 Key Features

### 💎 Elite 3D Dashboard
- **Perspective UI**: A cockpit dashboard with 3D perspective transforms (`rotateX`/`rotateY`) that react to hover.
- **Glassmorphism**: High-end blur effects, neon-cyan glowing borders, and luxury 3D depth.
- **Micro-Animations**: CRT scanline overlays, tactical corner brackets, and pulsating status modules.
- **Dribbble Aesthetic**: Custom dark-navy tech palette inspired by world-class UI designs.

### 🧠 Dual-Engine Intelligence
- **Groq Integration**: Powered by Llama 3.3 for ultra-fast (near-instant) inference and tool calling.
- **Gemini Fallback**: Seamless integration with Google Gemini 2.0 Flash.
- **Autonomous Function Calling**: The agent can autonomously interact with the airline grid to:
    - ✈️ **Search Trajectory**: Find flights across global nodes.
    - 🎫 **Sync Booking**: Retrieve and manage elite reservations.
    - 📡 **Node Telemetry**: Check real-time flight status and gate info.
    - 🌍 **Station Logs**: Access airport registries.
    - 🧳 **Policy Inquiry**: Fetch baggage and fare rules.

### 🛡️ Robust Architecture
- **Safe Mode**: Automatic fallback to rule-based logic if API limits are hit.
- **Local Grid Sync**: Serves premium assets locally to ensure 100% uptime.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aaditya-990/SkyWay-Elite-3D-AI-Agent.git
   cd SkyWay-Elite-3D-AI-Agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   ```

4. **Launch the Engine:**
   ```bash
   python app.py
   ```

## 🌍 Supported Grid Nodes
- **North America**: JFK, LAX, ORD
- **Europe**: LHR, CDG
- **Asia**: DXB, SIN, HND, BOM, DEL
- **Oceania**: SYD

---
*Developed with ❤️ for the future of aviation support.*
