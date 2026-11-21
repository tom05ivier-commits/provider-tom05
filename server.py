# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Tomi vier
# provider-tom05 — OpenAI-compatible provider wrapper.

from __future__ import annotations

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

PORT = int(os.environ.get("TOM05_PROVIDER_PORT", "8772"))
UPSTREAM = os.environ.get("TOM05_UPSTREAM", "http://127.0.0.1:8766/v1/chat/completions").rstrip("/")
UPSTREAM_MODEL = os.environ.get("TOM05_UPSTREAM_MODEL", "hy4-flash-free")
MODEL_ID = "tom05-flash-free"
CTL = int(os.environ.get("TOM05_CTL", "100000000"))


def _send(h: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Content-Length", str(len(data)))
    h.end_headers()
    h.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.rstrip("/")
        if path in ("/health", "/v1/health"):
            _send(self, 200, {"status": "ok", "provider": "tom05", "model": MODEL_ID})
        elif path in ("/v1/models", "/models"):
            _send(self, 200, {"object": "list", "data": [{
                "id": MODEL_ID, "object": "model", "owned_by": "tom05",
                "name": "Tom05 flash Free", "context_length": CTL,
                "declared_only": True,
            }]})
        else:
            _send(self, 404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") not in ("/v1/chat/completions", "/chat/completions"):
            _send(self, 404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            _send(self, 400, {"error": "invalid JSON"})
            return
        if not isinstance(body, dict):
            _send(self, 400, {"error": "invalid body"})
            return
        body["model"] = UPSTREAM_MODEL
        req = urllib.request.Request(
            UPSTREAM,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as res:
                payload = res.read()
                ctype = res.headers.get("Content-Type", "application/json")
        except Exception as exc:  # noqa: BLE001
            _send(self, 502, {"error": "upstream failed", "type": type(exc).__name__})
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
