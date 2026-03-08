<div align="center">

<!-- ANIMATED BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0085FF,100:9360FF&height=200&section=header&text=PROMETHEUS%20AI&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=Open-source%20AI%20agent%20for%20code%2C%20research%20%26%20automation&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>

<!-- ANIMATED TYPING SUBTITLE -->
[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Inter&weight=600&size=22&duration=3000&pause=1000&color=0085FF&center=true&vCenter=true&width=600&lines=Run+Python+simulations+in+plain+English;Research+any+topic+with+web+search;Build+%26+run+automated+AI+agents;Powered+by+Groq+%E2%80%94+completely+free)](https://git.io/typing-svg)

<br/>

<!-- BADGES -->
[![Python](https://img.shields.io/badge/Python_3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq_Llama_3.3_70B-0085FF?style=for-the-badge&logo=lightning&logoColor=white)](https://console.groq.com)
[![License](https://img.shields.io/badge/MIT_License-9360FF?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/JINZO-AI/prometheus_ai?style=for-the-badge&color=FFD700&logo=github)](https://github.com/JINZO-AI/prometheus_ai/stargazers)
[![Forks](https://img.shields.io/github/forks/JINZO-AI/prometheus_ai?style=for-the-badge&color=10B981&logo=github)](https://github.com/JINZO-AI/prometheus_ai/network)

<br/>

> **A production-grade AI agent web app that runs locally, costs nothing to operate,**  
> **and handles code execution, research, and automated agent generation — all from one clean UI.**

<br/>

</div>

---

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0085FF,100:9360FF&height=3&section=header" width="100%"/>

## What it does

<table>
<tr>
<td align="center" width="25%">
<br/>
<img src="https://img.shields.io/badge/⚡-Execute-0085FF?style=for-the-badge" /><br/><br/>
Describe any computation in plain English. The agent writes Python, runs it, and returns results with charts.
<br/><br/>
</td>
<td align="center" width="25%">
<br/>
<img src="https://img.shields.io/badge/🔬-Research-9360FF?style=for-the-badge" /><br/><br/>
Ask any question. Real-time web search via DuckDuckGo, synthesized by Groq into a structured answer.
<br/><br/>
</td>
<td align="center" width="25%">
<br/>
<img src="https://img.shields.io/badge/🤖-Build_Agent-10B981?style=for-the-badge" /><br/><br/>
Describe a Python agent. Get a standalone script you can run directly from the UI or download.
<br/><br/>
</td>
<td align="center" width="25%">
<br/>
<img src="https://img.shields.io/badge/📎-File_Analysis-F59E0B?style=for-the-badge" /><br/><br/>
Attach PDFs, CSVs, or Python files. Content is extracted and sent as context to the AI.
<br/><br/>
</td>
</tr>
</table>

<br/>

**Built-in simulations, ready to run in one click:**

| Simulation | What it does |
|-----------|-------------|
| Monte Carlo | Portfolio simulation with volatility modeling |
| Fibonacci | Sequence generation with golden ratio convergence chart |
| Physics | Projectile motion with trajectory visualization |
| Compound Interest | Long-term growth chart with monthly contributions |

---

## Quick Start

> Get the app running in under 5 minutes.

**Step 1 — Get your free Groq API key**

Go to [console.groq.com/keys](https://console.groq.com/keys), sign up, and create a key. It's free — no credit card.

**Step 2 — Clone and install**

```bash
git clone https://github.com/JINZO-AI/prometheus_ai.git
cd prometheus_ai
```

```bash
# Windows
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Step 3 — Configure**

```bash
cp .env.example .env
# Open .env — add your key on line 1:
GROQ_KEY=gsk_xxxxxxxxxxxxxxxx
```

**Step 4 — Run**

```bash
# Windows
.venv\Scripts\python.exe app.py

# Mac / Linux
python app.py
```

Open **[http://localhost:5000](http://localhost:5000)**

---

## Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar          │  Chat Area              │  Right Panel  │
│                   │                         │               │
│  Navigation       │  Welcome screen or      │  Live task    │
│  Quick tasks      │  conversation history   │  history      │
│  Search           │                         │  Chart gallery│
│  Theme toggle     │  ─────────────────────  │               │
│                   │  Input bar:             │  Stats:       │
│                   │  [Attach] [Voice]        │  Tasks        │
│                   │  [Execute|Research|      │  Success rate │
│                   │   Build Agent]  [Send]  │  Charts       │
└─────────────────────────────────────────────────────────────┘
```

Three input modes selectable from the bottom bar. Attach files, use voice input (Chrome/Edge), and export your full task history as JSON or CSV.

---

## Project Structure

```
prometheus_ai/
│
├── app.py                  # Flask server — all API routes
├── my_agent.py             # AI engine — Groq, code execution, research
├── requirements.txt
├── .env.example
│
├── templates/
│   └── index.html          # Full web UI (single file, zero build step required)
│
├── outputs/                # Generated charts (.png) and research reports (.txt)
├── built_agents/           # Python scripts created by Build Agent mode
├── uploads/                # User file attachments (PDF, CSV, TXT, etc.)
│
└── prometheus_memory/
    ├── tasks.json          # Full task history
    └── solutions.json      # Cached solutions
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Server health, Groq key status |
| `POST` | `/api/chat` | Main endpoint — `mode`: `execute` / `research` / `build` |
| `POST` | `/api/upload` | Upload a file attachment |
| `POST` | `/api/run-agent` | Execute a built agent script server-side |
| `GET` | `/api/history` | Task history with `?q=` search and `?mode=` filter |
| `DELETE` | `/api/history/<id>` | Delete one task |
| `POST` | `/api/history/clear` | Wipe all history |
| `GET` | `/api/outputs` | List generated files |
| `DELETE` | `/api/outputs/<filename>` | Delete a generated file |
| `GET` | `/api/stats` | Task counts, success rate, chart count |
| `GET/POST` | `/api/settings` | Read or update user settings |
| `GET` | `/api/export/history` | Export history — `?format=json` or `?format=csv` |

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_KEY` | Yes | — | Groq API key |
| `GROQ_API_KEY` | Alternative | — | Same as above — either works |
| `PORT` | No | `5000` | Server port |
| `FLASK_DEBUG` | No | `false` | Enable Flask debug mode |

---

## Optional: PDF Support

```bash
pip install pypdf
```

Without this, attached PDFs will show a notice instead of extracted text.

---

## Limitations

- Generated code runs as your local user — no sandboxing. Review scripts before running.
- No streaming — responses arrive after the agent finishes processing.
- Voice input requires Chrome or Edge (Web Speech API limitation).
- Task history is local — stored in `prometheus_memory/tasks.json`.

---

## Contributing

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/prometheus_ai.git

# 2. Create a branch
git checkout -b feature/what-you-are-adding

# 3. Commit
git commit -m "feat: describe your change clearly"

# 4. Push and open a PR
git push origin feature/what-you-are-adding
```

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:9360FF,100:0085FF&height=100&section=footer" width="100%"/>

**Built on the Groq API · Runs fully local · No subscription required**

[![GitHub](https://img.shields.io/badge/github-JINZO--AI/prometheus__ai-181717?style=for-the-badge&logo=github)](https://github.com/JINZO-AI/prometheus_ai)

</div>
