#!/usr/bin/env python3
"""Generate the minimal profile card used by the README."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"

THEMES = {
    "dark": {"background": "#161b22", "text": "#f0f6fc", "muted": "#8b949e", "accent": "#58a6ff"},
    "light": {"background": "#f6f8fa", "text": "#1f2328", "muted": "#656d76", "accent": "#0969da"},
}


def render_card(theme: dict[str, str]) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260" role="img" aria-labelledby="title desc">
  <title id="title">Alexandre Edmond</title>
  <desc id="desc">AI Engineer focused on robotics and embodied AI, based in Paris.</desc>
  <rect width="1000" height="260" rx="16" fill="{theme["background"]}"/>
  <circle cx="92" cy="130" r="42" fill="none" stroke="{theme["accent"]}" stroke-width="2"/>
  <path d="M72 130h40M92 110v40" stroke="{theme["accent"]}" stroke-width="2" stroke-linecap="round"/>
  <text x="174" y="107" fill="{theme["text"]}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="40" font-weight="700">Alexandre Edmond</text>
  <text x="174" y="151" fill="{theme["text"]}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="23">AI Engineer · Robotics &amp; Embodied AI</text>
  <text x="174" y="190" fill="{theme["muted"]}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="18">Paris, France</text>
</svg>
'''


def main() -> None:
    ASSET_DIR.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        (ASSET_DIR / f"{name}_mode.svg").write_text(render_card(theme), encoding="utf-8")


if __name__ == "__main__":
    main()
