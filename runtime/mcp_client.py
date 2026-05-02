"""Optionaler Client: sendet komprimierten Output an comptext-mcp-server REST API."""
import urllib.request
import urllib.error
import json
import sys


def send_to_mcp(compressed_text: str, base_url: str = "http://127.0.0.1:8100") -> dict | None:
    """
    POST compressed output to comptext-mcp-server /compress endpoint.
    Falls der Server nicht läuft, wird eine Warnung ausgegeben.
    """
    url = f"{base_url.rstrip('/')}/compress"
    payload = json.dumps({"text": compressed_text, "source": "runtime"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"[comptext-runtime] MCP-Server nicht erreichbar ({base_url}): {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[comptext-runtime] MCP-Fehler: {e}", file=sys.stderr)
        return None
