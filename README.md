<div align="center">

# 🤖 LIEBERT

**Autonomous AI Desktop Agent — Controlled via Telegram**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org)
[![Gemini](https://img.shields.io/badge/Gemini-API-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-22C55E?style=for-the-badge)]()

<br/>

*Control your computer from anywhere. LIEBERT sees your screen, runs commands,*
*searches the web, watches through your camera, and moves your mouse — all from Telegram.*

<br/>

[**Getting Started**](#-getting-started) · [**Commands**](#-command-reference) · [**Mouse & Keyboard**](#%EF%B8%8F-mouse--keyboard-experimental) · [**Roadmap**](#-roadmap)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [File Structure](#-file-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Telegram Bot Setup](#telegram-bot-setup)
  - [Configuration](#configuration)
- [Command Reference](#-command-reference)
  - [Bot Commands](#bot-commands)
  - [AI Command System](#ai-command-system)
  - [Internet & Research](#-internet--research)
  - [Terminal & Files](#-terminal--files)
  - [Vision & Camera](#-vision--camera)
  - [Mouse & Keyboard](#%EF%B8%8F-mouse--keyboard-experimental)
- [How It Works](#-how-it-works)
- [Memory System](#-memory-system)
- [Security](#-security)
- [API Compatibility](#-api-compatibility)
- [Roadmap](#-roadmap)

---

## 🧩 Overview

LIEBERT is a **personal AI agent framework** that runs on your computer and takes orders from your phone via Telegram. It's not just a chatbot — it can actually *do things*:

| Capability | Description |
|---|---|
| 🖥️ **See your screen** | Takes screenshots and analyzes them with AI vision |
| 📷 **Watch your camera** | Captures webcam frames and describes what it sees |
| 💻 **Run terminal commands** | Executes cmd/PowerShell with user approval |
| 🌐 **Search the web** | DuckDuckGo-powered research |
| 🖱️ **Control mouse & keyboard** | Clicks, drags, types — full UI automation *(experimental)* |
| 🧠 **Remember things** | Persistent memory and user profile across sessions |
| 🔑 **Multi-API support** | Rotate between multiple API keys to stay within free tier limits |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           YOUR PHONE (Telegram)         │
│         "Summarize my desktop"          │
└───────────────────┬─────────────────────┘
                    │ message
                    ▼
┌─────────────────────────────────────────┐
│              main.py                    │
│   Bot handler · AI loop · Router        │
└──────┬──────┬──────┬──────┬─────┬───────┘
       │      │      │      │     │
       ▼      ▼      ▼      ▼     ▼
  terminal  gorsel  mouse  hafiza internet
  .py       .py     .py    .py    .py
       │      │      │      │     │
       └──────┴──────┴──────┴─────┘
                    │
                    ▼
         ┌──────────────────┐
         │   Gemini API     │
         │ (OpenAI-compat.) │
         └──────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           YOUR PHONE (Telegram)         │
│  📸 screenshot · 📟 logs · ✅ result    │
└─────────────────────────────────────────┘
```

### The Agent Loop

When the AI includes a `[[[COMMAND: parameter]]]` tag in its response, the system:

1. Detects and extracts the command
2. Executes the corresponding action
3. Sends the result back to the AI as a system report
4. The AI decides what to do next

This loop repeats until the task is complete (max 7 iterations).

---

## 📁 File Structure

```
LIEBERT/
│
├── 📄 main.py              ← Entry point. Bot, AI loop, command router
├── 🖱️  mouse.py             ← Mouse & keyboard control (experimental)
├── 💻 terminal.py          ← Shell command executor + persistent log
├── 📷 gorsel.py            ← Screenshot, webcam, image analysis
├── 🧠 hafiza.py            ← Conversation memory & user profile
├── 🌐 internet.py          ← DuckDuckGo web search
├── 🔗 web_araci.py         ← Browser control
│
├── 🔑 APIs.json            ← API keys (auto-created on first run)
├── 💾 hafiza.json          ← Conversation history (auto-created)
├── 👤 profil.json          ← User profile (auto-created)
├── 📋 komutlar.json        ← Terminal command audit log (auto-created)
│
└── 📦 requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11.x**
- A [Telegram account](https://telegram.org)
- A [Gemini API key](https://ai.google.dev) (free tier works)

### Installation

```bash
git clone https://github.com/yourusername/liebert.git
cd liebert
pip install -r requirements.txt
```

**requirements.txt:**
```
python-telegram-bot>=20.0
openai>=1.14.0
duckduckgo-search>=5.0.0
Pillow>=10.2.0
opencv-python>=4.9.0
python-docx>=1.1.0
PyPDF2>=3.0.0
pyautogui
pyperclip
```

### Telegram Bot Setup

**Step 1 — Create your bot:**
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the **token** you receive

**Step 2 — Get your Telegram user ID:**
1. Send any message to your new bot
2. Open this URL in your browser (replace `<TOKEN>`):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. Find `"from": {"id": 123456789}` — that number is your ID

### Configuration

**Step 1 — Set up your API keys** by creating `APIs.json`:
```json
{
    "aktif_api": "",
    "api_listesi": {
        "API_1": "YOUR_GEMINI_API_KEY_HERE",
        "API_2": "YOUR_SECOND_KEY_HERE"
    }
}
```
> 💡 Add as many keys as you want. Switch between them live with `/api`.

**Step 2 — Edit `main.py`** and fill in the placeholders at the top:
```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
AUTHORIZED_ID  = 123456789  # Your Telegram user ID
```

**Step 3 — Run:**
```bash
python main.py
```

You should see:
```
LIEBERT Telegram Bot başlatılıyor...
Bot çalışıyor. Telegram'dan /start yaz.
```

Open Telegram, send `/start` to your bot, select an API key, and you're live.

---

## 📖 Command Reference

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Launch LIEBERT and select an API key |
| `/api` | Switch API key on the fly |
| `/durum` | Status report: active API, message count, screen size |
| `/sifirla` | Reset current session (does not wipe disk memory) |

---

### AI Command System

You talk to LIEBERT in natural language. When it needs to take action, it uses internal commands formatted as `[[[COMMAND: parameter]]]`. You don't type these — the AI does.

---

### 📡 Internet & Research

```
[[[INTERNET_ARA: "search query here"]]]
```

Searches DuckDuckGo and returns a summary of results.

```
Example: "What's the latest news on AI?"
→ [[[INTERNET_ARA: "AI news 2025"]]]
```

---

### 💻 Terminal & Files

```
[[[TERMINAL: command here]]]
```

> ⚠️ Every terminal command requires **your explicit approval** via an inline Telegram button before execution.

```powershell
# Examples
[[[TERMINAL: dir C:\Users\YourName\Desktop]]]
[[[TERMINAL: powershell Get-Process | Sort-Object CPU -Descending | Select -First 10]]]
[[[TERMINAL: echo Hello World > test.txt]]]
```

All executed commands are permanently logged to `komutlar.json`.

---

### 📷 Vision & Camera

**Screenshot + AI analysis:**
```
[[[MASAUSTU_BAK: "What windows are currently open?"]]]
[[[MASAUSTU_BAK: "Where is the Save button? Give me its coordinates."]]]
```

**Webcam capture + analysis:**
```
[[[KAMERA_BAK: "What's on my desk right now?"]]]
```

**Analyze an existing image file:**
```
[[[GORSEL_ANALIZ: "C:\path\to\image.png" ::: "What does this diagram show?"]]]
```

All images are sent to your Telegram chat before analysis so you can see exactly what the AI is looking at.

---

## 🖱️ Mouse & Keyboard *(Experimental)*

> ⚠️ **These features are experimental.** Behavior may be unpredictable on some systems.
> Requires: `pip install pyautogui pyperclip`
> Safety net: moving the mouse to the **top-left corner (0,0)** will immediately halt all automation.

---

### Mouse Click

```
[[[MOUSE_TIKLA: x ::: y ::: BUTTON]]]
```

| Button | Action |
|---|---|
| `LEFT` | Left click *(default if omitted)* |
| `RIGHT` | Right click — opens context menu |
| `DOUBLE` | Double click — opens files and folders |

```
[[[MOUSE_TIKLA: 500 ::: 300 ::: LEFT]]]
[[[MOUSE_TIKLA: 500 ::: 300 ::: RIGHT]]]
[[[MOUSE_TIKLA: 500 ::: 300 ::: DOUBLE]]]
[[[MOUSE_TIKLA: 500 ::: 300]]]            ← defaults to LEFT
```

---

### Mouse Drag

```
[[[MOUSE_SUR: x1 ::: y1 ::: x2 ::: y2 ::: BUTTON]]]
```

Holds the specified button down and drags from `(x1, y1)` to `(x2, y2)`.
Use cases: moving files, adjusting sliders, selecting text.

```
[[[MOUSE_SUR: 100 ::: 200 ::: 500 ::: 200 ::: LEFT]]]
```

---

### Mouse Position Check (Calibration)

```
[[[MOUSE_BAK: "I was aiming for the Save button — did I land on it?"]]]
```

Takes a screenshot and marks the last mouse action:
- 🟥 **Red square** — click location / drag start point
- 🟧 **Orange square** — drag end point
- 🟡 **Yellow line** — drag path

The image is sent to Telegram with a coordinate report. Use this for verification after precise operations — not after every click.

---

### Keyboard — Type Text

```
[[[KLAVYE_YAZ: "Hello, this is LIEBERT typing."]]]
```

Uses clipboard paste internally to support Turkish and special characters.

---

### Keyboard — Key Combinations

```
[[[KLAVYE_TUS: "combination"]]]
```

```
[[[KLAVYE_TUS: "enter"]]]
[[[KLAVYE_TUS: "ctrl+c"]]]          ← Copy
[[[KLAVYE_TUS: "ctrl+v"]]]          ← Paste
[[[KLAVYE_TUS: "ctrl+z"]]]          ← Undo
[[[KLAVYE_TUS: "ctrl+s"]]]          ← Save
[[[KLAVYE_TUS: "alt+f4"]]]          ← Close window
[[[KLAVYE_TUS: "win+d"]]]           ← Show desktop
[[[KLAVYE_TUS: "ctrl+shift+t"]]]    ← Reopen closed tab
[[[KLAVYE_TUS: "tab"]]]
[[[KLAVYE_TUS: "escape"]]]
[[[KLAVYE_TUS: "delete"]]]
```

---

### Typical Automation Workflows

<details>
<summary><b>📌 Click a button on screen</b></summary>

```
You:     "Click the Save button"

LIEBERT: [[[MASAUSTU_BAK: "Where is the Save button? Give me its coordinates."]]]
         → "Save button found at approximately (456, 312)"
         [[[MOUSE_TIKLA: 456 ::: 312 ::: LEFT]]]
         [[[MOUSE_BAK: "Did I click the Save button correctly?"]]]
         → Sends marked screenshot to Telegram
```
</details>

<details>
<summary><b>📌 Type into a text editor</b></summary>

```
[[[MOUSE_TIKLA: 640 ::: 400 ::: LEFT]]]    ← focus the editor
[[[KLAVYE_TUS: "ctrl+a"]]]                 ← select all
[[[KLAVYE_YAZ: "New content goes here"]]]  ← type
[[[KLAVYE_TUS: "ctrl+s"]]]                 ← save
```
</details>

<details>
<summary><b>📌 Right-click context menu</b></summary>

```
[[[MOUSE_TIKLA: 234 ::: 567 ::: RIGHT]]]
[[[MASAUSTU_BAK: "What options are in the context menu?"]]]
→ "Options: Open, Copy, Delete, Properties at (234, 590)"
[[[MOUSE_TIKLA: 234 ::: 590 ::: LEFT]]]
```
</details>

<details>
<summary><b>📌 Drag and drop a file</b></summary>

```
[[[MASAUSTU_BAK: "Where is the file and the target folder?"]]]
→ "File at (200, 300), target folder at (500, 300)"
[[[MOUSE_SUR: 200 ::: 300 ::: 500 ::: 300 ::: LEFT]]]
[[[MOUSE_BAK: "Did the file land in the right folder?"]]]
```
</details>

---

## ⚙️ How It Works

### Command Parsing

LIEBERT uses a regex-based command parser looking for `[[[COMMAND: parameter]]]` patterns in AI responses. Multiple commands can appear in a single response and are executed sequentially.

### Agent Loop (max 7 iterations)

```
User message
    ↓
AI generates response
    ↓
Parser finds commands → executes them
    ↓
Results sent back to AI as "SYSTEM REPORT"
    ↓
AI decides next step → loop continues
    ↓
No more commands → final response to user
```

### Terminal Safety

Every terminal command triggers a Telegram inline keyboard:

```
⚡ Critical Operation
┌─────────────────────────────┐
│  dir C:\Users\...           │
│  Run this command?          │
│  [✅ Approve]  [❌ Reject]  │
└─────────────────────────────┘
```

The AI loop is paused (via `threading.Event`) until you respond.

---

## 🧠 Memory System

| File | Contents | Limit |
|---|---|---|
| `hafiza.json` | Last N conversation messages | 20 messages (configurable) |
| `profil.json` | User profile: name, city, preferences | Unlimited keys |
| `komutlar.json` | Terminal command audit log | Never deleted |

The AI can update the profile mid-conversation:
```
[[[BILGI_EKLE: {"name": "Alex", "city": "Istanbul", "prefers": "dark mode"}]]]
```

Profile data is injected into every session's system prompt automatically.

---

## 🔒 Security

- **Allowlist-only:** Only your Telegram user ID can send commands. All other users get an `⛔ Unauthorized` response.
- **Terminal approval:** Every shell command requires explicit confirmation before execution.
- **Mouse actions:** Execute without confirmation — stay present when running automation tasks.
- **FailSafe:** `pyautogui.FAILSAFE = True` — drag mouse to top-left corner to immediately stop all automation.
- **Local only:** No cloud storage. All data stays on your machine.
- **Audit log:** Every terminal command is timestamped and logged to `komutlar.json`.

---

## 🔌 API Compatibility

LIEBERT uses the OpenAI-compatible API format. Change `BASE_URL` and `MODEL_NAME` in `main.py` to switch providers:

| Provider | BASE_URL | MODEL_NAME |
|---|---|---|
| **Gemini** *(default)* | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-flash-latest` |
| **OpenAI** | *(remove base_url)* | `gpt-4o` |
| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| **Ollama** | `http://localhost:11434/v1` | `llama3` |

Multi-key rotation is built in — add as many keys as you want to `APIs.json` and switch between them live with `/api`.

---

## 🗺️ Roadmap

- [x] Telegram bot integration
- [x] Terminal control with approval gate
- [x] Screenshot & webcam capture
- [x] AI vision analysis
- [x] Web search
- [x] Persistent memory & user profile
- [x] Multi-API key support
- [x] Mouse click, drag, double-click, right-click *(experimental)*
- [x] Keyboard typing & key combinations *(experimental)*
- [x] Mouse position calibration overlay *(experimental)*
- [ ] Mouse scroll wheel
- [ ] Multi-monitor support
- [ ] Scheduled tasks ("summarize news every morning at 9am")
- [ ] File transfer via Telegram (send/receive files)
- [ ] Webhook mode (replace polling)
- [ ] Swarm engine (parallel multi-agent task execution)

---

## 📝 Notes

- LIEBERT only controls the machine it runs on.
- Gemini free tier has rate limits — add multiple keys and use the rotation feature.
- Be present at your computer when using mouse/keyboard automation — the AI can misread coordinates.
- The `FAILSAFE` is your emergency stop: move the mouse to the top-left corner instantly.

---

<div align="center">

Built with Python · Powered by Gemini · Controlled via Telegram

*Personal project — use responsibly.*

</div>
