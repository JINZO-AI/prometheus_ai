"""
PROMETHEUS AI v13.0 — Production Web Server
Full SaaS backend: chat, file upload, history, outputs, settings, export
"""
import os, sys, json, time, uuid, base64, re, io
from pathlib import Path
from datetime import datetime
from flask import (Flask, request, jsonify, render_template,
                   send_from_directory, abort, Response, send_file)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(32)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

# ── Directories ─────────────────────────────────────────────────────────────
for d in ["outputs", "built_agents", "prometheus_memory", "core_versions", "uploads"]:
    Path(d).mkdir(exist_ok=True)

TASKS_FILE   = Path("prometheus_memory/tasks.json")
SETTINGS_FILE = Path("prometheus_memory/settings.json")

# ── Data helpers ─────────────────────────────────────────────────────────────
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

# ── Agent singleton ──────────────────────────────────────────────────────────
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

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".txt", ".csv", ".py", ".json"}

# ════════════════════════════════════════════════════════════════════════════
# ROUTES — Pages
# ════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    html = Path("templates/index.html").read_text(encoding="utf-8")
    return Response(html, mimetype="text/html")

@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory("outputs", filename)

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory("uploads", filename)

# ════════════════════════════════════════════════════════════════════════════
# ROUTES — API
# ════════════════════════════════════════════════════════════════════════════
@app.route("/api/status")
def api_status():
    key = os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY", "")
    settings = load_settings()
    return jsonify({
        "groq_key_set": bool(key),
        "agent_available": True,
        "model": "llama-3.3-70b-versatile",
        "version": "13.0",
        "username": settings.get("username", "Prometheus User"),
        "plan": settings.get("plan", "Free"),
    })

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "GET":
        return jsonify(load_settings())
    data = request.get_json() or {}
    settings = load_settings()
    settings.update({k: v for k, v in data.items()
                     if k in ["theme", "username", "plan", "model", "max_retries"]})
    save_settings(settings)
    return jsonify({"ok": True, "settings": settings})

@app.route("/api/stats")
def api_stats():
    tasks   = load_tasks()
    success = sum(1 for t in tasks if t.get("success"))
    imgs    = list(Path("outputs").glob("*.png"))
    agents  = list(Path("built_agents").glob("*.py"))
    mem_file = Path("prometheus_memory/solutions.json")
    cached = 0
    if mem_file.exists():
        try: cached = len(json.loads(mem_file.read_text()))
        except: pass
    return jsonify({
        "total_tasks":      len(tasks),
        "success_rate":     round(success / max(len(tasks), 1) * 100),
        "images_generated": len(imgs),
        "agents_built":     len(agents),
        "memory_cached":    cached,
    })

@app.route("/api/history")
def api_history():
    tasks = load_tasks()
    q     = request.args.get("q", "").lower().strip()
    mode  = request.args.get("mode", "").strip()
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))

    if q:
        tasks = [t for t in tasks if q in (
            (t.get("goal","") + t.get("output","") + t.get("type","")).lower())]
    if mode and mode != "all":
        tasks = [t for t in tasks if t.get("type","") == mode]

    tasks_rev = list(reversed(tasks))
    total     = len(tasks_rev)
    start     = (page - 1) * limit
    paged     = tasks_rev[start: start + limit]
    return jsonify({"tasks": paged, "total": total, "page": page})

@app.route("/api/history/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t.get("id") != task_id]
    save_tasks(tasks)
    return jsonify({"ok": True})

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    save_tasks([])
    return jsonify({"ok": True})

@app.route("/api/outputs")
def api_outputs():
    imgs = sorted(Path("outputs").glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    txts = sorted(Path("outputs").glob("*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)
    files = []
    for f in imgs[:30]:
        files.append({"name": f.name, "url": f"/outputs/{f.name}", "type": "image",
                      "size": f.stat().st_size,
                      "ts": datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d %H:%M")})
    for f in txts[:15]:
        files.append({"name": f.name, "url": f"/outputs/{f.name}", "type": "text",
                      "size": f.stat().st_size,
                      "ts": datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d %H:%M")})
    return jsonify({"files": files})

@app.route("/api/outputs/<filename>", methods=["DELETE"])
def delete_output(filename):
    p = Path("outputs") / filename
    if p.exists() and p.suffix in {".png", ".txt"}:
        p.unlink()
        return jsonify({"ok": True})
    return jsonify({"error": "File not found"}), 404

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"File type {ext} not allowed"}), 400
    safe = f"{uuid.uuid4().hex[:8]}_{re.sub(r'[^a-zA-Z0-9._-]','_',f.filename)}"
    dest = Path("uploads") / safe
    f.save(str(dest))
    return jsonify({"ok": True, "filename": safe, "url": f"/uploads/{safe}", "original": f.filename})

# ════════════════════════════════════════════════════════════════════════════
# ROUTES — Chat
# ════════════════════════════════════════════════════════════════════════════
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data    = request.get_json() or {}
    message = (data.get("message") or "").strip()
    mode    = data.get("mode", "execute")
    attachments = data.get("attachments", [])  # list of uploaded filenames

    if not message:
        return jsonify({"error": "No message"}), 400

    key = os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY", "")
    if not key:
        return jsonify({
            "reply": ("⚠️ **No Groq API key configured.**\n\n"
                      "Add your free key to `.env`:\n```\nGROQ_KEY=gsk_your_key_here\n```\n"
                      "Get it free at [console.groq.com/keys](https://console.groq.com/keys)"),
            "type": "error", "success": False, "images": [], "task_id": None,
        })

    task_id = str(uuid.uuid4())[:8]
    started = datetime.now().isoformat()

    # Append attachment context to message if any
    full_message = message
    if attachments:
        ctx_parts = []
        for fn in attachments:
            fp = Path("uploads") / fn
            if fp.exists() and fp.suffix in {".txt", ".csv", ".py", ".json"}:
                try:
                    text = fp.read_text(encoding="utf-8", errors="replace")[:3000]
                    ctx_parts.append(f"[FILE: {fn}]\n{text}")
                except: pass
        if ctx_parts:
            full_message = message + "\n\nATTACHED FILES:\n" + "\n\n".join(ctx_parts)

    handlers = {"research": _research, "build": _build_agent}
    handler  = handlers.get(mode, _execute)
    return handler(full_message, task_id, started, message)


def _execute(full_message, task_id, started, display_msg):
    import io as _io
    from contextlib import redirect_stdout
    agent = get_agent()
    if not agent:
        return jsonify({"reply": "❌ Agent could not initialize. Check GROQ_KEY.", "type": "error", "success": False, "images": [], "task_id": task_id})

    buf = _io.StringIO(); success = False
    try:
        with redirect_stdout(buf):
            success = agent.execute(full_message)
        output = buf.getvalue()
    except Exception as e:
        output = str(e); success = False

    imgs = sorted(Path("outputs").glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    recent_imgs = [f"/outputs/{f.name}" for f in imgs[:4]]
    clean_out   = _clean_stdout(output)

    icon  = "✅" if success else "❌"
    reply = f"{icon} **Task {'completed' if success else 'failed'}**\n\n"
    if clean_out:
        reply += f"```\n{clean_out[:2000]}\n```"
    if not success and not clean_out:
        reply += "The task could not be completed. Try rephrasing your request."

    _save_task(task_id, display_msg, "execute", success, clean_out, recent_imgs, started)
    return jsonify({"reply": reply, "type": "execute", "success": success,
                    "images": recent_imgs, "task_id": task_id})


def _research(full_message, task_id, started, display_msg):
    import io as _io
    from contextlib import redirect_stdout
    agent = get_agent()
    if not agent:
        return jsonify({"reply": "❌ Agent not available.", "type": "error", "success": False, "images": [], "task_id": task_id})

    buf = _io.StringIO(); answer = ""
    try:
        with redirect_stdout(buf):
            answer = agent.research_mode(full_message) or ""
    except Exception as e:
        answer = str(e)

    txt_files = sorted(Path("outputs").glob("research_*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)
    dl = f"\n\n📄 [Download report](/outputs/{txt_files[0].name})" if txt_files else ""
    reply = f"🔬 **Research: {display_msg}**\n\n{answer}{dl}"

    _save_task(task_id, display_msg, "research", True, answer[:500], [], started)
    return jsonify({"reply": reply, "type": "research", "success": True, "images": [], "task_id": task_id})


def _build_agent(full_message, task_id, started, display_msg):
    import io as _io
    from contextlib import redirect_stdout
    agent = get_agent()
    if not agent:
        return jsonify({"reply": "❌ Agent not available.", "type": "error", "success": False, "images": [], "task_id": task_id})

    path = None
    try:
        buf = _io.StringIO()
        with redirect_stdout(buf):
            path = agent.build(full_message)
    except Exception as e:
        pass

    if path:
        try: preview = Path(path).read_text(encoding="utf-8")[:800]
        except: preview = ""
        reply = (f"🤖 **Agent built:** `{display_msg}`\n\n"
                 f"**File:** `{path}`\n\n"
                 f"**Run:** `python {path}`\n\n"
                 f"**Preview:**\n```python\n{preview}\n...\n```")
        success = True
    else:
        reply   = f"❌ Could not build agent for `{display_msg}`. Try a more specific description."
        success = False

    _save_task(task_id, display_msg, "build", success, str(path) if path else "", [], started)
    return jsonify({"reply": reply, "type": "build", "success": success, "images": [], "task_id": task_id})


def _save_task(task_id, goal, type_, success, output, images, started):
    tasks = load_tasks()
    tasks.append({"id": task_id, "goal": goal, "type": type_,
                  "success": success, "output": output[:500],
                  "images": images, "ts": started})
    save_tasks(tasks)


def _clean_stdout(text: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    lines = text.split("\n")
    skip = re.compile(r"^\[(GROQ|EXEC|REPAIR|TEMPLATE|MEM|TYPE|TASK|OK|IMAGES|BUILDER|RESEARCH|SUCCESS|FAILED)\]")
    return "\n".join(l for l in lines if not skip.match(l)).strip()


# ════════════════════════════════════════════════════════════════════════════
# ROUTES — Export
# ════════════════════════════════════════════════════════════════════════════
@app.route("/api/export/history")
def export_history():
    tasks = load_tasks()
    fmt   = request.args.get("format", "json")
    if fmt == "csv":
        lines = ["id,goal,type,success,ts"]
        for t in tasks:
            lines.append(f'"{t.get("id","")}",'
                         f'"{t.get("goal","").replace(chr(34),chr(39))}",'
                         f'"{t.get("type","")}",'
                         f'"{t.get("success","")}",'
                         f'"{t.get("ts","")}"')
        return Response("\n".join(lines), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=prometheus_history.csv"})
    return Response(json.dumps(tasks, indent=2), mimetype="application/json",
                    headers={"Content-Disposition": "attachment;filename=prometheus_history.json"})

@app.route("/api/chat/share", methods=["POST"])
def share_chat():
    data    = request.get_json() or {}
    content = data.get("content", "")
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname   = f"shared_chat_{ts}.txt"
    (Path("outputs") / fname).write_text(content, encoding="utf-8")
    return jsonify({"ok": True, "url": f"/outputs/{fname}", "filename": fname})


# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"""
╔══════════════════════════════════════════════════════╗
║      PROMETHEUS AI  v13.0  —  Production Edition     ║
╠══════════════════════════════════════════════════════╣
║  Web UI:    http://localhost:{port:<24}║
║  Network:   http://0.0.0.0:{port:<25}║
║  API key:   console.groq.com/keys                    ║
╚══════════════════════════════════════════════════════╝
""")
    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
