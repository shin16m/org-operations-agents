#!/usr/bin/env python3
"""Ops dashboard — sessions · org-os queue · webhook log (Phase 3 + B2).

Usage:
  python tools/asana_ops_dashboard.py --port 8765
  open http://127.0.0.1:8765/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
for p in (str(TOOLS), str(ASANA_OPT), str(ORG_OS_SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
import asana_ops_sessions  # noqa: E402
from org_os.env import load_dotenv  # noqa: E402
from org_os.queue import ready_queue, wait_list  # noqa: E402

DEFAULT_RUNNER_LOG = ROOT / "output/platform/runner-watch.log"

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>org-ops Dashboard</title>
  <style>
    :root { --bg:#0f172a; --card:#1e293b; --text:#e2e8f0; --muted:#94a3b8; --wait:#fbbf24; --ok:#34d399; --ready:#60a5fa; --line:#334155; }
    body { margin:0; font-family:Segoe UI,Meiryo,sans-serif; background:var(--bg); color:var(--text); }
    header { padding:20px 24px; border-bottom:1px solid var(--line); }
    h1 { margin:0 0 6px; font-size:1.25rem; }
    h2 { font-size:1rem; margin:24px 0 8px; }
    .meta { color:var(--muted); font-size:.85rem; }
    main { padding:20px 24px; }
    table { width:100%; border-collapse:collapse; font-size:.85rem; margin-bottom:8px; }
    th,td { border:1px solid var(--line); padding:8px 10px; text-align:left; }
    th { background:var(--card); }
    .wait { color:var(--wait); font-weight:600; }
    .resumable { color:var(--ok); font-weight:600; }
    .ready { color:var(--ready); font-weight:600; }
    a { color:#93c5fd; }
    pre { background:var(--card); padding:12px; border-radius:8px; overflow:auto; font-size:.75rem; max-height:200px; }
  </style>
</head>
<body>
  <header>
    <h1>org-ops Dashboard</h1>
    <div class="meta" id="summary">loading…</div>
  </header>
  <main>
    <h2>Queue — READY</h2>
    <table aria-label="ready queue">
      <thead><tr><th>epic</th><th>name</th><th>os_state</th><th>link</th></tr></thead>
      <tbody id="ready-rows"></tbody>
    </table>
    <h2>Queue — WAITING</h2>
    <table aria-label="wait queue">
      <thead><tr><th>epic</th><th>name</th><th>reason</th><th>link</th></tr></thead>
      <tbody id="wait-rows"></tbody>
    </table>
    <h2>Sessions</h2>
    <table aria-label="suspended sessions">
      <thead><tr><th>session</th><th>gate</th><th>status</th><th>url</th><th>webhook</th></tr></thead>
      <tbody id="session-rows"></tbody>
    </table>
    <h2>Runner log (tail)</h2>
    <pre id="runner-log"></pre>
    <h2>Webhook log</h2>
    <pre id="webhook-log"></pre>
  </main>
  <script>
    function epicLink(gid) {
      return gid ? `<a href="https://app.asana.com/0/0/${gid}" target="_blank">${gid}</a>` : '';
    }
    async function refresh() {
      const [ready, wait, sessions, runner, webhook] = await Promise.all([
        fetch('/api/queue/ready').then(r => r.json()),
        fetch('/api/queue/wait').then(r => r.json()),
        fetch('/api/sessions').then(r => r.json()),
        fetch('/api/runner-log?lines=40').then(r => r.json()),
        fetch('/api/webhook-log').then(r => r.json()),
      ]);
      const waitS = sessions.filter(x => x.status === 'wait').length;
      const resume = sessions.filter(x => x.status === 'resumable').length;
      document.getElementById('summary').textContent =
        `READY ${(ready.rows||[]).length} · WAIT ${(wait.rows||[]).length} · ` +
        `sessions WAIT ${waitS} RESUME ${resume} · project ${ready.project || wait.project || '—'}`;
      document.getElementById('ready-rows').innerHTML = (ready.rows || []).map(row => `
        <tr>
          <td>${epicLink(row.epic_gid)}</td>
          <td>${(row.name || '').slice(0,60)}</td>
          <td class="ready">${row.os_state || 'Ready'}</td>
          <td>${row.permalink_url ? `<a href="${row.permalink_url}" target="_blank">Asana</a>` : ''}</td>
        </tr>`).join('') || '<tr><td colspan="4">No READY epics</td></tr>';
      document.getElementById('wait-rows').innerHTML = (wait.rows || []).map(row => `
        <tr>
          <td>${epicLink(row.epic_gid)}</td>
          <td>${(row.name || '').slice(0,60)}</td>
          <td class="wait">${row.suspend_reason || '—'}</td>
          <td>${row.permalink_url ? `<a href="${row.permalink_url}" target="_blank">Asana</a>` : ''}</td>
        </tr>`).join('') || '<tr><td colspan="4">No WAITING epics</td></tr>';
      document.getElementById('session-rows').innerHTML = sessions.map(row => `
        <tr>
          <td>${row.session_id || ''}</td>
          <td>${row.gate_kind || ''}</td>
          <td class="${row.status === 'resumable' ? 'resumable' : 'wait'}">${row.status.toUpperCase()}</td>
          <td>${row.approval_url ? `<a href="${row.approval_url}" target="_blank">Open</a>` : ''}</td>
          <td>${row.webhook_resumed_at || '—'}</td>
        </tr>`).join('') || '<tr><td colspan="5">No suspended sessions</td></tr>';
      document.getElementById('runner-log').textContent = (runner.lines || []).join('\\n') || '(no runner log)';
      document.getElementById('webhook-log').textContent = JSON.stringify(webhook, null, 2);
    }
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>
"""


def _resolve_project() -> str | None:
    load_dotenv()
    for key in ("ASANA_PROJECT_ID", "ASANA_PROJECT_GID", "ASANA_PROJECT"):
        val = os.getenv(key, "").strip()
        if val:
            return val
    return None


def sessions_payload() -> list[dict]:
    load_env_from_dotfile()
    try:
        token = get_token()
    except Exception:
        token = ""
    rows = []
    for session in asana_ops_sessions.load_suspended_sessions():
        if token:
            row = asana_ops_sessions.check_session_status(session, token)
        else:
            row = {
                "session_id": session.get("session_id"),
                "status": "resumable" if session.get("webhook_resumed_at") else "wait",
                "gate_kind": session.get("gate_kind"),
                "approval_url": session.get("approval_url"),
                "webhook_resumed_at": session.get("webhook_resumed_at"),
            }
        rows.append(row)
    return rows


def queue_ready_payload() -> dict:
    project = _resolve_project()
    if not project:
        return {"project": None, "rows": [], "error": "ASANA_PROJECT_ID unset"}
    try:
        return {"project": project, "rows": ready_queue(project)}
    except Exception as exc:
        return {"project": project, "rows": [], "error": str(exc)}


def queue_wait_payload() -> dict:
    project = _resolve_project()
    if not project:
        return {"project": None, "rows": [], "error": "ASANA_PROJECT_ID unset"}
    try:
        return {"project": project, "rows": wait_list(project)}
    except Exception as exc:
        return {"project": project, "rows": [], "error": str(exc)}


def runner_log_payload(*, max_lines: int = 50) -> dict:
    override = os.getenv("ORG_OPS_RUNNER_LOG", "").strip()
    path = Path(override) if override else DEFAULT_RUNNER_LOG
    if not path.is_file():
        return {"path": str(path), "lines": [], "exists": False}
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = text[-max(1, max_lines) :]
    return {"path": str(path), "lines": tail, "exists": True}


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"dashboard {self.address_string()} - {fmt % args}\n")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path == "/":
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif path == "/api/sessions":
            body = json.dumps(sessions_payload(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif path == "/api/queue/ready":
            body = json.dumps(queue_ready_payload(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif path == "/api/queue/wait":
            body = json.dumps(queue_wait_payload(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif path == "/api/runner-log":
            lines = int((qs.get("lines") or ["50"])[0])
            body = json.dumps(runner_log_payload(max_lines=lines), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif path == "/api/webhook-log":
            body = json.dumps(asana_ops_sessions.read_webhook_log(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    p = argparse.ArgumentParser(description="org-ops dashboard — sessions + org-os queue")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    server = HTTPServer((args.host, args.port), DashboardHandler)
    print(f"DASHBOARD  http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDASHBOARD  stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
