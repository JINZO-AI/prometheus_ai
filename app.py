"""
PROMETHEUS AI — Production Web Server
Full-stack AI agent: execute code, research topics, build & run agents
"""
import os, sys, json, uuid, re, io, subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(32)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

for d in ["outputs", "built_agents", "prometheus_memory", "core_versions", "uploads"]:
    Path(d).mkdir(exist_ok=True)

TASKS_FILE    = Path("prometheus_memory/tasks.json")
SETTINGS_FILE = Path("prometheus_memory/settings.json")
ALLOWED_EXT   = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf",
                 ".txt", ".csv", ".py", ".json", ".md"}

def load_tasks():
    if TASKS_FILE.exists():
        try: return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        except: pass
    return []

def save_tasks(tasks):
    try: TASKS_FILE.write_text(json.dumps(tasks[-500:], indent=2), encoding="utf-8")
    except: pass

def load_settings():
    defaults = {"theme": "light", "model": "llama-3.3-70b-versatile",
                "max_retries": 3, "username": "Prometheus User", "plan": "Free"}
    if SETTINGS_FILE.exists():
        try:
            s = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            defaults.update(s)
        except: pass
    return defaults

def save_settings(data):
    try: SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except: pass

def extract_file_text(filepath: Path) -> str:
    ext = filepath.suffix.lower()
    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(filepath))
            return "\n".join(p.extract_text() or "" for p in reader.pages[:20])[:6000]
        except Exception: pass
        try:
            import PyPDF2
            with open(filepath, "rb") as f:
                r = PyPDF2.PdfReader(f)
                return "\n".join(p.extract_text() or "" for p in r.pages[:20])[:6000]
        except Exception: pass
        try:
            from pdfminer.high_level import extract_text
            return (extract_text(str(filepath)) or "")[:6000]
        except Exception: pass
        return "[PDF attached — install 'pypdf' for text extraction: pip install pypdf]"
    if ext in {".txt", ".md", ".csv", ".py", ".json"}:
        try: return filepath.read_text(encoding="utf-8", errors="replace")[:6000]
        except: return ""
    return ""

_agent_instance = None
def get_agent():
    global _agent_instance
    if _agent_instance is None:
        try:
            import my_agent
            _agent_instance = my_agent.PrometheusAgent()
        except Exception as e:
            print(f"[WARN] Agent init: {e}")
    return _agent_instance

# ── Pages ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return Response(Path("templates/index.html").read_text(encoding="utf-8"),
                    mimetype="text/html")

@app.route("/outputs/<path:filename>")
def serve_output(filename): return send_from_directory("outputs", filename)

@app.route("/uploads/<path:filename>")
def serve_upload(filename): return send_from_directory("uploads", filename)

@app.route("/built_agents/<path:filename>")
def serve_agent(filename): return send_from_directory("built_agents", filename)

# ── API ───────────────────────────────────────────────────────────────────────
@app.route("/api/status")
def api_status():
    key = os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY", "")
    s   = load_settings()
    return jsonify({"groq_key_set": bool(key), "agent_available": True,
                    "model": "llama-3.3-70b-versatile", "version": "1.0.0",
                    "username": s.get("username", "Prometheus User"),
                    "plan": s.get("plan", "Free")})

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "GET": return jsonify(load_settings())
    data = request.get_json() or {}
    s = load_settings()
    for k in ["theme", "username", "plan", "model", "max_retries"]:
        if k in data: s[k] = data[k]
    save_settings(s)
    return jsonify({"ok": True, "settings": s})

@app.route("/api/stats")
def api_stats():
    tasks  = load_tasks()
    ok     = sum(1 for t in tasks if t.get("success"))
    imgs   = list(Path("outputs").glob("*.png"))
    agents = list(Path("built_agents").glob("*.py"))
    cached = 0
    mem = Path("prometheus_memory/solutions.json")
    if mem.exists():
        try: cached = len(json.loads(mem.read_text()))
        except: pass
    return jsonify({"total_tasks": len(tasks),
                    "success_rate": round(ok / max(len(tasks), 1) * 100),
                    "images_generated": len(imgs),
                    "agents_built": len(agents),
                    "memory_cached": cached})

@app.route("/api/history")
def api_history():
    tasks = load_tasks()
    q     = request.args.get("q", "").lower().strip()
    mode  = request.args.get("mode", "").strip()
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    if q:
        tasks = [t for t in tasks
                 if q in (t.get("goal","") + t.get("output","") + t.get("type","")).lower()]
    if mode and mode != "all":
        tasks = [t for t in tasks if t.get("type","") == mode]
    rev = list(reversed(tasks))
    return jsonify({"tasks": rev[(page-1)*limit:page*limit], "total": len(rev), "page": page})

@app.route("/api/history/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    save_tasks([t for t in load_tasks() if t.get("id") != task_id])
    return jsonify({"ok": True})

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    save_tasks([])
    return jsonify({"ok": True})

@app.route("/api/outputs")
def api_outputs():
    files = []
    for f in sorted(Path("outputs").glob("*.png"),
                    key=lambda x: x.stat().st_mtime, reverse=True)[:30]:
        files.append({"name": f.name, "url": f"/outputs/{f.name}", "type": "image",
                      "size": f.stat().st_size,
                      "ts": datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d %H:%M")})
    for f in sorted(Path("outputs").glob("*.txt"),
                    key=lambda x: x.stat().st_mtime, reverse=True)[:15]:
        files.append({"name": f.name, "url": f"/outputs/{f.name}", "type": "text",
                      "size": f.stat().st_size,
                      "ts": datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d %H:%M")})
    return jsonify({"files": files})

@app.route("/api/outputs/<filename>", methods=["DELETE"])
def delete_output(filename):
    p = Path("outputs") / filename
    if p.exists() and p.suffix in {".png", ".txt"}:
        p.unlink(); return jsonify({"ok": True})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/agents")
def api_agents():
    agents = []
    for f in sorted(Path("built_agents").glob("*.py"),
                    key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        agents.append({"name": f.name, "url": f"/built_agents/{f.name}",
                       "size": f.stat().st_size,
                       "ts": datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d %H:%M")})
    return jsonify({"agents": agents})

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files: return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    if not f.filename: return jsonify({"error": "Empty filename"}), 400
    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"File type '{ext}' not allowed"}), 400
    safe = f"{uuid.uuid4().hex[:8]}_{re.sub(r'[^a-zA-Z0-9._-]','_', f.filename)}"
    dest = Path("uploads") / safe
    f.save(str(dest))
    preview = ""
    try: preview = extract_file_text(dest)[:300]
    except: pass
    return jsonify({"ok": True, "filename": safe, "url": f"/uploads/{safe}",
                    "original": f.filename, "preview": preview, "ext": ext})

# ── Chat ──────────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data        = request.get_json() or {}
    message     = (data.get("message") or "").strip()
    mode        = data.get("mode", "execute")
    attachments = data.get("attachments", [])

    if not message: return jsonify({"error": "No message"}), 400

    key = os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY", "")
    if not key:
        return jsonify({
            "reply": "**No Groq API key found.**\n\nAdd `GROQ_KEY=gsk_xxx` to your `.env` file.\nGet a free key at [console.groq.com/keys](https://console.groq.com/keys)",
            "type": "error", "success": False, "images": [], "task_id": None, "agent_file": None
        })

    task_id = str(uuid.uuid4())[:8]
    started = datetime.now().isoformat()

    # Build message with file content appended
    full_message = message
    attach_names = []
    if attachments:
        parts = []
        for fn in attachments:
            fp = Path("uploads") / fn
            if not fp.exists(): continue
            # Recover original name (strip uuid prefix e.g. "a1b2c3d4_name.pdf")
            original = "_".join(fn.split("_")[1:]) if "_" in fn else fn
            text = extract_file_text(fp)
            attach_names.append(original)
            if text:
                parts.append(f"=== FILE: {original} ===\n{text}\n=== END ===")
            else:
                parts.append(f"=== FILE: {original} (image/binary — no text) ===")
        if parts:
            full_message = message + "\n\n" + "\n\n".join(parts)

    handlers = {"research": _research, "build": _build_agent}
    return handlers.get(mode, _execute)(full_message, task_id, started, message, attach_names)


def _execute(full_msg, task_id, started, display, attach_names=None):
    from contextlib import redirect_stdout
    agent = get_agent()
    if not agent:
        return jsonify({"reply": "Agent could not initialize. Check GROQ_KEY.",
                        "type": "error", "success": False, "images": [], "task_id": task_id, "agent_file": None})
    buf = io.StringIO(); success = False
    try:
        with redirect_stdout(buf): success = agent.execute(full_msg)
        output = buf.getvalue()
    except Exception as e: output = str(e)

    imgs = sorted(Path("outputs").glob("*.png"),
                  key=lambda f: f.stat().st_mtime, reverse=True)
    recent_imgs = [f"/outputs/{f.name}" for f in imgs[:4]]
    clean = _clean(output)

    icon  = "✅" if success else "❌"
    reply = f"{icon} **{'Done' if success else 'Failed'}**\n\n"
    if attach_names: reply += f"📎 *Files: {', '.join(attach_names)}*\n\n"
    if clean: reply += f"```\n{clean[:3000]}\n```"
    elif not success: reply += "Could not complete task. Try rephrasing."

    _save(task_id, display, "execute", success, clean, recent_imgs, started)
    return jsonify({"reply": reply, "type": "execute", "success": success,
                    "images": recent_imgs, "task_id": task_id, "agent_file": None})


def _research(full_msg, task_id, started, display, attach_names=None):
    from contextlib import redirect_stdout
    agent = get_agent()
    if not agent:
        return jsonify({"reply": "Agent not available.", "type": "error",
                        "success": False, "images": [], "task_id": task_id, "agent_file": None})
    buf = io.StringIO(); answer = ""
    try:
        with redirect_stdout(buf): answer = agent.research_mode(full_msg) or ""
    except Exception as e: answer = str(e)

    txts  = sorted(Path("outputs").glob("research_*.txt"),
                   key=lambda f: f.stat().st_mtime, reverse=True)
    dl    = f"\n\n📄 [Download report](/outputs/{txts[0].name})" if txts else ""
    extra = f"\n\n📎 *Files: {', '.join(attach_names)}*" if attach_names else ""
    reply = f"🔬 **Research: {display}**{extra}\n\n{answer}{dl}"

    _save(task_id, display, "research", True, answer[:500], [], started)
    return jsonify({"reply": reply, "type": "research", "success": True,
                    "images": [], "task_id": task_id, "agent_file": None})


def _build_agent(full_msg, task_id, started, display, attach_names=None):
    from contextlib import redirect_stdout
    agent = get_agent()
    if not agent:
        return jsonify({"reply": "Agent not available.", "type": "error",
                        "success": False, "images": [], "task_id": task_id, "agent_file": None})
    path = None
    try:
        with redirect_stdout(io.StringIO()): path = agent.build(full_msg)
    except Exception: pass

    if path:
        try: preview = Path(path).read_text(encoding="utf-8")[:1500]
        except: preview = ""
        fname = Path(path).name
        reply = (f"🤖 **Agent created:** `{display}`\n\n"
                 f"**Saved to:** `{path}`\n\n"
                 f"```python\n{preview}\n```")
        _save(task_id, display, "build", True, path, [], started)
        return jsonify({"reply": reply, "type": "build", "success": True,
                        "images": [], "task_id": task_id, "agent_file": fname})

    _save(task_id, display, "build", False, "", [], started)
    return jsonify({"reply": f"Could not build agent for `{display}`. Be more specific.",
                    "type": "build", "success": False, "images": [],
                    "task_id": task_id, "agent_file": None})


@app.route("/api/run-agent", methods=["POST"])
def run_agent():
    data     = request.get_json() or {}
    filename = (data.get("filename") or "").strip()
    if not filename or "/" in filename or "\\" in filename:
        return jsonify({"ok": False, "output": "Invalid filename"}), 400
    agent_path = Path("built_agents") / filename
    if not agent_path.exists():
        return jsonify({"ok": False, "output": "Agent file not found"}), 404
    venv_py = Path(".venv/Scripts/python.exe")
    python  = str(venv_py) if venv_py.exists() else sys.executable
    try:
        result = subprocess.run([python, str(agent_path)],
                                capture_output=True, text=True,
                                timeout=60, cwd=str(Path.cwd()))
        out     = (result.stdout + result.stderr).strip() or "(no output)"
        return jsonify({"ok": result.returncode == 0, "output": out[:3000],
                        "returncode": result.returncode})
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "output": "Agent timed out after 60 seconds."})
    except Exception as e:
        return jsonify({"ok": False, "output": f"Run error: {e}"})


def _save(task_id, goal, type_, success, output, images, started):
    tasks = load_tasks()
    tasks.append({"id": task_id, "goal": goal, "type": type_,
                  "success": success, "output": str(output)[:500],
                  "images": images, "ts": started})
    save_tasks(tasks)

def _clean(text: str) -> str:
    text  = re.sub(r"\x1b\[[0-9;]*m", "", text)
    skip  = re.compile(r"^\[(GROQ|EXEC|REPAIR|TEMPLATE|MEM|TYPE|TASK|OK|IMAGES|BUILDER|RESEARCH|SUCCESS|FAILED)\]")
    return "\n".join(l for l in text.split("\n") if not skip.match(l)).strip()


# ── Export ────────────────────────────────────────────────────────────────────
@app.route("/api/export/history")
def export_history():
    tasks = load_tasks()
    fmt   = request.args.get("format", "json")
    if fmt == "csv":
        lines = ["id,goal,type,success,ts"] + [
            ','.join([f'"{t.get("id","")}"',
                      f'"{t.get("goal","").replace(chr(34),chr(39))}"',
                      f'"{t.get("type","")}"',
                      f'"{t.get("success","")}"',
                      f'"{t.get("ts","")}"'])
            for t in tasks]
        return Response("\n".join(lines), mimetype="text/csv",
                        headers={"Content-Disposition":
                                 "attachment;filename=prometheus_history.csv"})
    return Response(json.dumps(tasks, indent=2), mimetype="application/json",
                    headers={"Content-Disposition":
                             "attachment;filename=prometheus_history.json"})

@app.route("/api/chat/share", methods=["POST"])
def share_chat():
    data  = request.get_json() or {}
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"chat_{ts}.txt"
    (Path("outputs") / fname).write_text(data.get("content",""), encoding="utf-8")
    return jsonify({"ok": True, "url": f"/outputs/{fname}"})


if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG","false").lower() == "true"
    print(f"""
╔══════════════════════════════════════════════╗
║          PROMETHEUS AI — Production          ║
╠══════════════════════════════════════════════╣
║  Open: http://localhost:{port:<21}║
╚══════════════════════════════════════════════╝
""")
    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
