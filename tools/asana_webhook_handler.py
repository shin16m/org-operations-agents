#!/usr/bin/env python3
"""Asana Webhook handler with SLA metrics (Phase 3 dryrun · Phase 6 SLA).

Receives webhook POSTs and updates suspended sessions.

Usage:
  python tools/asana_webhook_handler.py --port 8766
  python tools/asana_webhook_handler.py --port 8766 --require-secret
  curl http://127.0.0.1:8766/metrics
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import asana_ops_sessions  # noqa: E402

METRICS: dict = {
    "requests_total": 0,
    "webhook_posts": 0,
    "auth_failures": 0,
    "errors": 0,
    "latency_ms": [],
    "started_at": 0.0,
}


def _record_latency(ms: float) -> None:
    METRICS["latency_ms"].append(ms)
    if len(METRICS["latency_ms"]) > 500:
        METRICS["latency_ms"] = METRICS["latency_ms"][-500:]


def _latency_summary() -> dict:
    samples = METRICS["latency_ms"]
    if not samples:
        return {"count": 0, "p50_ms": None, "p95_ms": None, "max_ms": None}
    ordered = sorted(samples)
    n = len(ordered)

    def pct(p: float) -> float:
        idx = min(n - 1, max(0, int(n * p) - 1))
        return round(ordered[idx], 2)

    return {
        "count": n,
        "p50_ms": pct(0.50),
        "p95_ms": pct(0.95),
        "max_ms": round(max(ordered), 2),
    }


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
    require_secret: bool = False

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"webhook {self.address_string()} - {fmt % args}\n")

    def _auth_ok(self) -> bool:
        if not self.secret:
            return not self.require_secret
        return self.headers.get("X-Hook-Secret") == self.secret or self.headers.get(
            "Authorization"
        ) == f"Bearer {self.secret}"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        METRICS["requests_total"] += 1
        path = self.path.rstrip("/")
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/ready":
            self._send_json(200, {"ready": True, "require_secret": self.require_secret})
            return
        if path == "/metrics":
            uptime = round(time.time() - METRICS["started_at"], 1)
            self._send_json(
                200,
                {
                    "uptime_s": uptime,
                    "requests_total": METRICS["requests_total"],
                    "webhook_posts": METRICS["webhook_posts"],
                    "auth_failures": METRICS["auth_failures"],
                    "errors": METRICS["errors"],
                    "latency": _latency_summary(),
                    "sla_targets": {
                        "p95_ms": 2000,
                        "note": "ops: alert when p95_ms > sla for 5m",
                    },
                },
            )
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        METRICS["requests_total"] += 1
        t0 = time.perf_counter()
        if self.path.rstrip("/") != "/webhook":
            self.send_response(404)
            self.end_headers()
            return
        if not self._auth_ok():
            METRICS["auth_failures"] += 1
            self.send_response(401)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            METRICS["errors"] += 1
            self.send_response(400)
            self.end_headers()
            return
        METRICS["webhook_posts"] += 1
        results = []
        try:
            for gid in _extract_completed_task_gids(payload):
                results.append(asana_ops_sessions.handle_task_completed(gid))
        except Exception:  # noqa: BLE001
            METRICS["errors"] += 1
            raise
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        _record_latency(latency_ms)
        summary = _latency_summary()
        print(
            f"WEBHOOK_SLA  latency_ms={latency_ms}  p95={summary.get('p95_ms')}  "
            f"events={len(results)}"
        )
        self._send_json(200, {"ok": True, "results": results, "latency_ms": latency_ms})


def main() -> int:
    p = argparse.ArgumentParser(description="Asana webhook handler with SLA metrics")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--secret", default=os.environ.get("ASANA_WEBHOOK_SECRET"))
    p.add_argument(
        "--require-secret",
        action="store_true",
        help="Reject requests when ASANA_WEBHOOK_SECRET unset (production mode)",
    )
    args = p.parse_args()
    if args.require_secret and not args.secret:
        print("error: --require-secret but ASANA_WEBHOOK_SECRET unset", file=sys.stderr)
        return 2
    WebhookHandler.secret = args.secret
    WebhookHandler.require_secret = args.require_secret
    METRICS["started_at"] = time.time()
    server = HTTPServer((args.host, args.port), WebhookHandler)
    print(
        f"WEBHOOK  listening http://{args.host}:{args.port}/webhook  "
        f"health=/health  metrics=/metrics  require_secret={args.require_secret}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWEBHOOK  stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
