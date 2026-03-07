# 🔥 PROMETHEUS AI — v12.0 Groq Edition

> Self-improving AI agent with a beautiful web UI, powered entirely by **Groq** (free).  
> One API key. Zero paid tiers needed.

![PROMETHEUS AI](https://img.shields.io/badge/Groq-Llama_3.3_70B-0085FF?style=for-the-badge&logo=lightning&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-090B1E?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-F9FAFC?style=for-the-badge&logo=flask&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-9360FF?style=for-the-badge)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Chat** | Run any Python task with full web UI |
| 📊 **4 Simulation Templates** | Monte Carlo, Fibonacci, Physics, Compound Interest |
| 🔬 **Deep Research** | Web search + AI synthesis |
| 🤖 **Build Agents** | Generate specialized Python sub-agents |
| 🧠 **Persistent Memory** | Never repeat the same computation twice |
| 🎨 **Beautiful UI** | Script.io-inspired dark/light design |
| 📱 **Responsive** | Works on desktop, tablet, mobile |
| ⚡ **Groq-Only** | Free, fast, no other API keys needed |

---

## 🚀 Quick Setup

### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/prometheus-ai.git
cd prometheus-ai
```

### Step 2 — Get your FREE Groq API key

1. Go to **[console.groq.com/keys](https://console.groq.com/keys)**
2. Sign up (free) → Create API Key
3. Copy the key (starts with `gsk_...`)

### Step 3 — Configure

```bash
cp .env.example .env
# Edit .env and add your key:
# GROQ_KEY=gsk_xxxxxxxxxxxxxxxxxx
```

### Step 4 — Run setup

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

Or manually:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5 — Launch

```bash
python app.py
```

Open **[http://localhost:5000](http://localhost:5000)** 🎉

---

## 🖥️ Web UI Guide

### Chat Modes

| Mode | How to use | Example |
|------|-----------|---------|
| ⚡ **Execute** | Run Python code tasks | `Monte Carlo simulation $10k portfolio` |
| 🔬 **Research** | Web search + AI synthesis | `What is the Riemann Hypothesis?` |
| 🤖 **Build Agent** | Generate a Python agent file | `a stock price visualizer agent` |

### Navigation

- **AI Chat** — Main chat interface
- **History** — All past tasks with search/filter
- **Outputs** — All generated charts and reports
- **Quick Tasks** — One-click pre-built simulations

---

## 🔧 CLI Mode

You can also use the agent directly from the command line:

```bash
# Activate venv first
source .venv/bin/activate

# Demo task
python my_agent.py

# Custom task
python my_agent.py --goal "Plot first 30 prime numbers"

# Research
python my_agent.py --research "What is quantum entanglement?"

# Build a sub-agent
python my_agent.py --build "stock price visualization agent"

# Interactive mode
python my_agent.py -i
```

---

## 📁 Project Structure

```
prometheus-ai/
├── app.py                 # Flask web server (all API routes)
├── my_agent.py            # Prometheus AI engine (Groq-powered)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── setup.sh               # Linux/Mac setup
├── setup.bat              # Windows setup
├── templates/
│   └── index.html         # Full web UI (single file)
├── outputs/               # Generated charts & research reports
├── built_agents/          # AI-generated sub-agent scripts
├── prometheus_memory/     # Persistent solution cache (JSON)
└── core_versions/         # Agent version history
```

---

## 🐙 GitHub Setup Guide

### Push to a new GitHub repo

```bash
# 1. Create a new repo on github.com (don't add README/gitignore — we have them)

# 2. Initialize git in your project folder
cd prometheus-ai
git init
git add .
git commit -m "feat: PROMETHEUS AI v12.0 — Groq Edition"

# 3. Add your GitHub remote (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/prometheus-ai.git

# 4. Push
git branch -M main
git push -u origin main
```

### Replace existing repo

```bash
# If you already have a repo and want to replace it:
git init
git add .
git commit -m "feat: PROMETHEUS AI v12.0 — complete rewrite"
git remote add origin https://github.com/JINZO-AI/prometheus-ai.git
git branch -M main
git push -u origin main --force   # ⚠️ force-push replaces everything
```

---

## ✅ How to Test

### Test 1 — App starts correctly
```bash
python app.py
# Should print:
# ╔═══════════════════════════════════╗
# ║  PROMETHEUS AI v12.0 — Groq      ║
# ║  http://localhost:5000            ║
# ╚═══════════════════════════════════╝
```

### Test 2 — API status
```bash
curl http://localhost:5000/api/status
# Expected: {"groq_key_set": true, "agent_available": true, ...}
```

### Test 3 — Monte Carlo simulation
In the web UI:
1. Select mode **⚡ Execute**
2. Type: `Monte Carlo simulation of $10,000 portfolio`
3. Press Enter
4. Should complete in ~5 seconds with a chart

### Test 4 — Research mode
1. Select mode **🔬 Research**
2. Type: `What is the Fibonacci sequence?`
3. Should return a well-structured text answer

### Test 5 — CLI test
```bash
python my_agent.py --goal "First 20 Fibonacci numbers"
# Should print the sequence and save a chart to outputs/
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_KEY` | ✅ Yes | Your Groq API key from console.groq.com |
| `PORT` | Optional | Web server port (default: 5000) |
| `FLASK_DEBUG` | Optional | Enable debug mode (`true`/`false`) |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  <strong>Built with Groq Llama 3.3 70B</strong><br/>
  Free AI API · No credit card needed<br/>
  <a href="https://console.groq.com/keys">Get your free Groq key →</a>
</div>
