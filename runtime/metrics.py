import sys


def measure_gain(original: str, compressed: str) -> float:
    """Berechnet Token-Ersparnis in Prozent (Zeichen als Proxy)."""
    orig_len = len(original)
    comp_len = len(compressed)
    if orig_len == 0:
        return 0.0
    return max(0.0, (1 - comp_len / orig_len) * 100)


def print_gain_banner(gain_pct: float, profile_name: str, file=None):
    if file is None:
        file = sys.stderr
    bar_len = int(gain_pct / 5)
    bar = "█" * bar_len + "░" * (20 - bar_len)
    print(f"\n╔══ comptext-runtime [{profile_name}] ", file=file)
    print(f"║  Gain: [{bar}] {gain_pct:.1f}% gespart", file=file)
    print(f"╚══════════════════════════════════════", file=file)
