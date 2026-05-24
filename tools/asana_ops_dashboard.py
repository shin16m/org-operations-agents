#!/usr/bin/env python3
"""Ops dashboard MVP — suspended sessions + webhook log (Phase 3).

Usage:
  python tools/asana_ops_dashboard.py --port 8765
  open http://127.0.0.1:8765/
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
import asana_ops_sessions  # noqa: E402

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>org-ops Dashboard (Phase 3 dryrun)</title>
  <style>
    :root { --bg:#0f172a; --card:#1e293b; --text:#e2e8f0; --muted:#94a3b8; --wait:#fbbf24; --ok:#34d399; --line:#334155; }
    body { margin:0; font-family:Segoe UI,Meiryo,sans-serif; background:var(--bg); color:var(--text); }
    header { padding:20px 24px; border-bottom:1px solid var(--line); }
    h1 { margin:0 0 6px; font-size:1.25rem; }
    .meta { color:var(--muted); font-size:.85rem; }
    main { padding:20px 24px; }
    table { width:100%; border-collapse:collapse; font-size:.85rem; }
    th,td { border:1px solid var(--line); padding:8px 10px; text-align:left; }
    th { background:var(--card); }
    .wait { color:var(--wait); font-weight:600; }
    .resumable { color:var(--ok); font-weight:600; }
    a { color:#93c5fd; }
    pre { background:var(--card); padding:12px; border-radius:8px; overflow:auto; font-size:.75rem; }
  </style>
</head>
<body>
  <header>
    <h1>org-ops Dashboard</h1>
    <div class="meta">Phase 3 dryrun · <span id="summary">loading…</span></div>
  </header>
  <main>
    <h2>Sessions</h2>
    <table aria-label="suspended sessions">
      <thead><tr><th>session</th><th>gate</th><th>status</th><th>url</th><th>webhook</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
    <h2>Webhook log</h2>
    <pre id="log"></pre>
  </main>
  <script>
    async function refresh() {
      const [s, l] = await Promise.all([
        fetch('/api/sessions').then(r => r.json()),
        fetch('/api/webhook-log').then(r => r.json()),
      ]);
      const wait = s.filter(x => x.status === 'wait').length;
      const resume = s.filter(x => x.status === 'resumable').length;
      document.getElementById('summary').textContent =
        `WAIT ${wait} · RESUME ${resume} · webhook events ${l.length}`;
      document.getElementById('rows').innerHTML = s.map(row => `
        <tr>
          <td>${row.session_id || ''}</td>
          <td>${row.gate_kind || ''}</td>
          <td class="${row.status === 'resumable' ? 'resumable' : 'wait'}">${row.status.toUpperCase()}</td>
          <td>${row.approval_url ? `<a href="${row.approval_url}" target="_blank">Open Asana</a>` : ''}</td>
          <td>${row.webhook_resumed_at || '—'}</td>
        </tr>`).join('') || '<tr><td colspan="5">No suspended sessions</td></tr>';
      document.getElementById('log').textContent = JSON.stringify(l, null, 2);
    }
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>
"""


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


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"dashboard {self.address_string()} - {fmt % args}\n")

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/":
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif path == "/api/sessions":
            body = json.dumps(sessions_payload(), ensure_ascii=False).encode("utf-8")
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
    p = argparse.ArgumentParser(description="org-ops dashboard MVP")
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
