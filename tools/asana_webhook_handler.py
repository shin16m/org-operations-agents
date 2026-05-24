#!/usr/bin/env python3
"""Asana Webhook handler dryrun (Phase 3).

Receives simplified webhook POSTs and updates suspended sessions.

Usage:
  python tools/asana_webhook_handler.py --port 8766
  curl -X POST http://127.0.0.1:8766/webhook -H "Content-Type: application/json" \\
    -d '{"events":[{"action":"changed","resource":{"gid":"SUB_GID","resource_type":"task"},"change":{"field":"completed","action":"changed","new_value":true}}]}'
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import asana_ops_sessions  # noqa: E402


def _extract_completed_task_gids(payload: dict) -> list[str]:
    gids: list[str] = []
    for ev in payload.get("events") or []:
        if ev.get("action") not in ("changed", "added", "deleted"):
            continue
        resource = ev.get("resource") or {}
        if resource.get("resource_type") != "task":
            continue
        change = ev.get("change") or {}
        if change.get("field") == "completed" and change.get("new_value") is True:
            gid = resource.get("gid")
            if gid:
                gids.append(str(gid))
        elif ev.get("action") == "changed" and resource.get("gid"):
            gid = str(resource["gid"])
            if gid not in gids:
                gids.append(gid)
    return gids


class WebhookHandler(BaseHTTPRequestHandler):
    secret: str | None = None

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"webhook {self.address_string()} - {fmt % args}\n")

    def _auth_ok(self) -> bool:
        if not self.secret:
            return True
        return self.headers.get("X-Hook-Secret") == self.secret or self.headers.get(
            "Authorization"
        ) == f"Bearer {self.secret}"

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/webhook":
            self.send_response(404)
            self.end_headers()
            return
        if not self._auth_ok():
            self.send_response(401)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        results = []
        for gid in _extract_completed_task_gids(payload):
            results.append(asana_ops_sessions.handle_task_completed(gid))
        body = json.dumps({"ok": True, "results": results}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    p = argparse.ArgumentParser(description="Asana webhook handler dryrun")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--secret", default=os.environ.get("ASANA_WEBHOOK_SECRET"))
    args = p.parse_args()
    WebhookHandler.secret = args.secret
    server = HTTPServer((args.host, args.port), WebhookHandler)
    print(f"WEBHOOK  listening http://{args.host}:{args.port}/webhook  health=/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWEBHOOK  stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
