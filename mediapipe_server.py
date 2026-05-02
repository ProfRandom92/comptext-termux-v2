#!/usr/bin/env python3
"""
MediaPipe LLM Server – Option B Backend
========================================
llama.cpp-kompatible REST API via Google MediaPipe LLM Inference.
Ermöglicht Nutzung von Gemma-Modellen auf Android ohne llama.cpp-Build.

Hinweis: Für MedGemma bevorzuge Option A (llama.cpp via tur-repo).
MediaPipe + Standard-Gemma ist ein Kompromiss ohne medizinisches Training.

Setup:
    pip install mediapipe
    python mediapipe_server.py ~/models/gemma-2b-it.bin --port 8080
"""
from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TriageHandler(BaseHTTPRequestHandler):
    """HTTP-Handler mit llama.cpp-kompatibler /completion API."""

    server: Any  # hat .llm Attribut

    def log_message(self, format: str, *args: Any) -> None:
        logger.debug(format, *args)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json_response({"status": "ok", "backend": "mediapipe"})
        else:
            self._json_response({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        if self.path != "/completion":
            self._json_response({"error": "Not found"}, 404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        prompt = data.get("prompt", "")
        n_predict = data.get("n_predict", 100)

        try:
            result = self.server.llm.generate_response(prompt)
            self._json_response({"content": result, "model": "mediapipe-gemma"})
        except Exception as exc:
            logger.exception("Inferenz-Fehler")
            self._json_response({"error": str(exc)}, 500)

    def _json_response(self, data: dict, code: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_llm(model_path: str, tokenizer_path: str | None = None):
    """Initialisiert MediaPipe LLM mit Gemma-Modell."""
    try:
        from mediapipe.tasks.python.genai import llm_inference as genai
    except ImportError:
        raise ImportError(
            "MediaPipe nicht installiert.\n"
            "Option A (empfohlen): pkg install tur-repo && pkg install llama-cpp\n"
            "Option B: pip install mediapipe"
        )

    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(f"Modell nicht gefunden: {model_path}")

    options = genai.LlmInference.LlmInferenceOptions(
        model_path=str(model_file),
        max_tokens=512,
        top_k=1,
        temperature=0.1,
    )
    return genai.LlmInference.create_from_options(options)


def main() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="MediaPipe LLM Server für CompText")
    parser.add_argument("model", help="Pfad zur .bin-Datei")
    parser.add_argument("--tokenizer", "-t", help="Pfad zum Tokenizer (optional)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", "-p", type=int, default=8080)
    args = parser.parse_args()

    print(f"Initialisiere MediaPipe LLM: {args.model}")
    llm = create_llm(args.model, args.tokenizer)

    server = HTTPServer((args.host, args.port), TriageHandler)
    server.llm = llm  # type: ignore

    print(f"Server läuft auf http://{args.host}:{args.port}")
    print("API: POST /completion (llama.cpp-kompatibel)")
    print("Drücke Ctrl+C zum Beenden")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")


if __name__ == "__main__":
    main()
