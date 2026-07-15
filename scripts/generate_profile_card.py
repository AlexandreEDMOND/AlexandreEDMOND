#!/usr/bin/env python3
"""Generate the light and dark SVG cards displayed in the profile README."""

from __future__ import annotations

import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


USERNAME = "AlexandreEDMOND"
ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
API_URL = "https://api.github.com"

PROFILE_ROWS = [
    ("Title", "AI Engineer / Robot Learning / Embodied AI"),
    ("Location", "Paris, France"),
    ("AI.Interests", "Robot Learning, RL, Vision, LLM Agents"),
    ("Languages.Programming", "Python, C++, SQL, Bash, JavaScript"),
    ("Languages.AI", "PyTorch, Transformers, OpenCV, NumPy"),
    ("Engineering", "MLOps, FastAPI, Docker, GitHub Actions"),
    ("Robotics", "Pepper, EMG, ManiSkill, DIY Robotics"),
    ("Languages.Real", "French, English"),
]

CURRENT_ROWS = [
    ("Current.Work", "Imitation Learning, Embodied AI, Open ML"),
    ("Current.Project", "ManiSkill Imitation Learning Lab"),
]

PROJECT_ROWS = [
    ("Projects.Robotics", "ManiSkill Lab, TonySpark"),
    ("Projects.RL", "numpy-rl-racer, zero_to_skyjo"),
    ("Projects.AI", "flechebench, TTS-GAN"),
]

ROBOT_ART = [
    "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
    "░░░░░░░░░░░░░░░░░░░▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
    "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
    "░░░░░░░░░░░░░░░░░░░░▒░░░░░▒▒▒░▒▒░░░░░░░░░░░░░░░░░░",
    "░░░░░░░░░░░░░░░░░░░▒▓▓███▓▓▒▓▓▒▒▒░░░░░░░░░░░░░░░░░",
    "░░░░░░░░░░░░░░░░▒▒▓▓▓███████▓▓▓▓░░░░░░░░░░░░░░░░░░",
    "▒▒▒▒▒▒▒▒▒▒░░▒▒░▒▓███▒▒▒▒▒▒▓███▓▓▓▒▒▒░░░░░░░░░░░░░░",
    "▒▒▒▒▒▒▒▒▒░░░░▒░░▓██▓▒▒▒▒▒▒▓▓▓▓███▓▒░░░░░░░░░░░░░░░",
    "▓▓▓▓▓▓▓▓▒▒▒░▒▓▒▒▓██▓▒▒▓▓░░▒▓▓▓▓███▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░",
    "▒▒▒▒▒▒▒▒▒▒░░░▒▒▒▓██▒░░░▒░░▒▒░░░█▓▓▒▓▓▓▓▓▓▒▒▒▒▒▒░░░",
    "▓▓▓▓▓▓▓▓▓▒░░░▓▓▓▓▓▓▓░░▒▒▒▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒",
    "▓▓▓▓▓▓▓▓▓▒░░▒▓▓▓▓▓▒░░░▒▒▒▒▓▓▒▒░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒",
    "▓▓▓▓▓▓▓▓▓▒░░▒▓▓▓▓▓▒▓▓▒▒▒▒▒▒▒▒▒░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒",
    "▓▓▓▓▓▓▓▓▓▒░░▒▓▓▓▓▓▒▒▓▒▒▒▒▒▒▒▒▒░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░░",
    "▓▓▓▓▓▓███▓▒▒▓▓▓▓▓▓▒▓▓▒▒▒▓▓▓▓▓▒▒▓██▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒",
    "▒▓▓▒▒▓██▓▒░░▒▓▓▓▓▓▒▓█▓▒▒░▒▒▒▒▒█▓▓█▓▓▓▓▓▓▓▓▒▓▓▓▒░░░",
    "▒▓▓▒▒▓▓▓▓▒░░▒▓▓▒▒▓▒▓██▒▒▒▒▒▒▒▓███▓▒▒▒▒▒▒▒▒▒▒▒▒▓▒░░",
    "▒▓▓▒▒▒▒▒▒▒░░▒▓▓▒▒▓████▓▒▒▒▒▒▓█████▓▒▒▓▓▓▓▓▓▓▓▒▒▒▒▓",
    "▒▒▒▒▒▒▒▒▒▒░░▒▓█████████▓▒▒▒██████████▓░▒▓▓▓▓▒░▒▒██",
    "▒▒▒▒▒▒▒▒▓▓▒▒▓▓██████████▓▓████████████▓▓▓▒▒▒░▒▒▓██",
    "▒▒▒▒▒▒▓█████████████████▓▓████████████████▓▒░▒▓▓██",
    "▒▒▒▒▒▓██████████████████████████████████████▓░▒▓██",
    "▓▓▓▓▓███████████████████▓████████████████████▓▒▒▒▓",
    "▒▒▒▒▒█████████████████████████████████████████░░░░",
    "░░░░▒█████████████████████████████████████████▒░░░",
    "▒▒▒▒▓█████████████████████████████████████████▒▒▒▒",
    "▒▒▒▒▒█████████████████████████████████████████▒░░░",
]

THEMES = {
    "dark": {
        "background": "#161b22",
        "text": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "muted": "#616e7f",
    },
    "light": {
        "background": "#f6f8fa",
        "text": "#24292f",
        "key": "#953800",
        "value": "#0a3069",
        "muted": "#c2cfde",
    },
}

API_ERRORS = (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError)


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def request_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-card",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_repositories(token: str | None) -> list[dict[str, Any]]:
    repositories: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = request_json(
            f"{API_URL}/users/{USERNAME}/repos?per_page=100&page={page}", token
        )
        if not isinstance(payload, list):
            raise ValueError("GitHub returned an invalid repository response")
        repositories.extend(repo for repo in payload if isinstance(repo, dict))
        if len(payload) < 100:
            return repositories
        page += 1


def twelve_months_ago() -> str:
    today = datetime.now(timezone.utc).date()
    try:
        start = today.replace(year=today.year - 1)
    except ValueError:
        start = today.replace(year=today.year - 1, day=28)
    return start.isoformat()


def fetch_commit_count(token: str | None) -> int:
    parameters = urlencode(
        {
            "q": f"author:{USERNAME} author-date:>={twelve_months_ago()}",
            "per_page": 1,
        }
    )
    payload = request_json(f"{API_URL}/search/commits?{parameters}", token)
    if payload.get("incomplete_results"):
        raise ValueError("GitHub returned incomplete commit search results")
    return int(payload["total_count"])


def fetch_stats() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN") or None
    stats = {"repos": "N/A", "stars": "N/A", "commits": "N/A", "followers": "N/A"}

    try:
        user = request_json(f"{API_URL}/users/{USERNAME}", token)
        stats["repos"] = str(int(user["public_repos"]))
        stats["followers"] = str(int(user["followers"]))
    except API_ERRORS as error:
        print(f"User statistics unavailable: {error}", file=sys.stderr)

    try:
        repositories = fetch_repositories(token)
        stats["stars"] = str(
            sum(int(repo.get("stargazers_count", 0)) for repo in repositories)
        )
    except API_ERRORS as error:
        print(f"Repository statistics unavailable: {error}", file=sys.stderr)

    try:
        stats["commits"] = str(fetch_commit_count(token))
    except API_ERRORS as error:
        print(f"Commit statistics unavailable: {error}", file=sys.stderr)

    return stats


def render_data_row(label: str, value: str, y: int) -> str:
    dots = "." * max(2, 20 - len(label))
    return (
        f'  <text x="350" y="{y}"><tspan class="muted">. </tspan>'
        f'<tspan class="key">{escape(label)}</tspan>:'
        f'<tspan class="muted"> {dots} </tspan>'
        f'<tspan class="value">{escape(value)}</tspan></text>'
    )


def render_section(title: str, y: int) -> str:
    rule = "-" * max(3, 61 - len(title))
    return f'  <text x="350" y="{y}">- {escape(title)} {rule}</text>'


def render_stats(stats: dict[str, str]) -> list[str]:
    return [
        '  <text x="350" y="470"><tspan class="muted">. </tspan>'
        '<tspan class="key">Repos</tspan>:<tspan class="muted"> ........ </tspan>'
        f'<tspan class="value">{escape(stats["repos"])}</tspan>'
        '<tspan>  |  </tspan><tspan class="key">Stars</tspan>:'
        '<tspan class="muted"> ........... </tspan>'
        f'<tspan class="value">{escape(stats["stars"])}</tspan></text>',
        '  <text x="350" y="494"><tspan class="muted">. </tspan>'
        '<tspan class="key">Commits.12mo</tspan>:<tspan class="muted"> ... </tspan>'
        f'<tspan class="value">{escape(stats["commits"])}</tspan>'
        '<tspan>  |  </tspan><tspan class="key">Followers</tspan>:'
        '<tspan class="muted"> ....... </tspan>'
        f'<tspan class="value">{escape(stats["followers"])}</tspan></text>',
    ]


def render_card(theme_name: str, stats: dict[str, str]) -> str:
    theme = THEMES[theme_name]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="530" '
        'viewBox="0 0 1000 530" role="img" aria-labelledby="title desc">',
        "  <title id=\"title\">Alexandre Edmond - AI Engineer profile</title>",
        "  <desc id=\"desc\">Neofetch-style profile with an original ASCII robot and GitHub statistics.</desc>",
        "  <style>",
        "    text { font-family: Consolas, 'Liberation Mono', Menlo, monospace; font-size: 15.5px; white-space: pre; fill: %s; }"
        % theme["text"],
        "    .ascii { fill: %s; font-size: 10px; }" % theme["text"],
        "    .key { fill: %s; }" % theme["key"],
        "    .value { fill: %s; }" % theme["value"],
        "    .muted { fill: %s; }" % theme["muted"],
        "  </style>",
        f'  <rect width="1000" height="530" rx="15" fill="{theme["background"]}"/>',
    ]

    for index, art_line in enumerate(ROBOT_ART):
        lines.append(
            f'  <text x="10" y="{28 + index * 11}" class="ascii">{escape(art_line)}</text>'
        )

    lines.append(render_section("alexandre@edmond", 30))
    for index, (label, value) in enumerate(PROFILE_ROWS):
        lines.append(render_data_row(label, value, 56 + index * 21))

    lines.append(render_section("Current", 242))
    for index, (label, value) in enumerate(CURRENT_ROWS):
        lines.append(render_data_row(label, value, 268 + index * 22))

    lines.append(render_section("Selected Projects", 332))
    for index, (label, value) in enumerate(PROJECT_ROWS):
        lines.append(render_data_row(label, value, 358 + index * 22))

    lines.append(render_section("GitHub Stats", 442))
    lines.extend(render_stats(stats))
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_if_changed(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        print(f"Unchanged: {path.relative_to(ROOT)}")
        return
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Updated: {path.relative_to(ROOT)}")


def main() -> None:
    stats = fetch_stats()
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    write_if_changed(ASSET_DIR / "dark_mode.svg", render_card("dark", stats))
    write_if_changed(ASSET_DIR / "light_mode.svg", render_card("light", stats))


if __name__ == "__main__":
    main()
