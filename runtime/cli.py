#!/usr/bin/env python3
"""
comptext-runtime CLI
Usage: echo "<shell output>" | python -m runtime.cli --cmd "git diff"
       python -m runtime.cli --cmd "pytest" --profile dev
"""
import argparse
import sys
from .profiles import load_profile
from .filters.dispatcher import apply_filters
from .metrics import measure_gain, print_gain_banner


def main():
    parser = argparse.ArgumentParser(
        prog="comptext-runtime",
        description="CompText RTK-Layer: compresses shell output before LLM context"
    )
    parser.add_argument("--cmd", default="", help="Original command (used for profile matching)")
    parser.add_argument("--profile", default=None, help="Force a specific profile (dev/med/repo/log)")
    parser.add_argument("--mcp", action="store_true", help="Forward compressed output to comptext-mcp-server")
    parser.add_argument("--mcp-url", default="http://127.0.0.1:8100", help="CompText MCP/REST URL")
    args = parser.parse_args()

    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    profile = load_profile(args.cmd, override=args.profile)
    compressed = apply_filters(raw, profile)

    sys.stdout.write(compressed)

    gain_pct = measure_gain(raw, compressed)
    print_gain_banner(gain_pct, profile.get("name", "?"), file=sys.stderr)

    if args.mcp:
        from .mcp_client import send_to_mcp
        send_to_mcp(compressed, args.mcp_url)


if __name__ == "__main__":
    main()
