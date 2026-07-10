#!/usr/bin/env python3
"""Generate the SVG cards displayed in the profile README."""

from __future__ import annotations

import html
import json
import os
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USERNAME = "AlexandreEDMOND"
ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
API_URL = "https://api.github.com"

PROFILE_ROWS = [
    ("Title", "AI Engineer | Robot Learning | Embodied AI"),
    ("Location", "Paris, France"),
    ("Languages.Programming", "Python, C++, SQL, Bash, JavaScript"),
    ("Languages.AI", "PyTorch, Transformers, OpenCV, NumPy"),
    ("AI.Interests", "Robot Learning, Reinforcement Learning, Computer Vision, LLM Agents"),
    ("Engineering", "MLOps, FastAPI, Docker, GitHub Actions"),
    ("Robotics", "Pepper, EMG Interfaces, ManiSkill, DIY Robotics"),
    ("Current.Work", "Imitation Learning, Embodied AI, Open-Source ML"),
    ("Current.Project", "ManiSkill Imitation Learning Lab"),
    ("Languages.Real", "French, English"),
]

ROBOT_ART = [
    "       .--------.",
    "      /  o    o  \\",
    "     |     __     |",
    "     |   .----.   |",
    " .---|   | AE |   |---.",
    "/    |   '----'   |    \\",
    "\\___/------------\\___/",
    "     /_|________|_\\",
    "      _/ /    \\ \\_",
    "     /__/      \\__\\",
]

STYLE = """
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace; }
    .muted { fill: #86909c; }
    .label { fill: #79c7ff; }
    .value { fill: #e6edf3; }
    .accent { fill: #ff9d4d; }
    .green { fill: #7ee787; }
    .violet { fill: #c297ff; }
    .leader { stroke: #4b5563; stroke-width: 1; stroke-dasharray: 2 5; }
""".strip()


def escape(value: object) -> str:
    """Escape every value before it enters SVG text."""
    return html.escape(str(value), quote=True)


def request_json(
    url: str,
    token: str | None,
    *,
    data: dict[str, Any] | None = None,
) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-card",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if data is not None:
        body = json.dumps(data, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=body, headers=headers)
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


def fetch_contributions(token: str) -> tuple[int, int]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        start = now.replace(year=now.year - 1)
    except ValueError:
        start = now.replace(year=now.year - 1, day=28)
    variables = {
        "login": USERNAME,
        "from": start.isoformat().replace("+00:00", "Z"),
        "to": now.isoformat().replace("+00:00", "Z"),
    }
    query = """
      query($login: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $login) {
          contributionsCollection(from: $from, to: $to) {
            contributionCalendar { totalContributions }
            totalCommitContributions
          }
        }
      }
    """
    payload = request_json(
        f"{API_URL}/graphql", token, data={"query": query, "variables": variables}
    )
    if payload.get("errors"):
        raise ValueError(payload["errors"][0].get("message", "GraphQL query failed"))
    collection = payload["data"]["user"]["contributionsCollection"]
    return (
        int(collection["contributionCalendar"]["totalContributions"]),
        int(collection["totalCommitContributions"]),
    )


def fetch_stats() -> list[tuple[str, str]]:
    token = os.environ.get("GITHUB_TOKEN") or None
    values: dict[str, str] = {
        "Public repos": "Unavailable",
        "Stars received": "Unavailable",
        "Followers": "Unavailable",
        "Contributions / 12 mo": "Unavailable",
        "Commits / 12 mo": "Unavailable",
    }

    try:
        user = request_json(f"{API_URL}/users/{USERNAME}", token)
        values["Public repos"] = str(int(user["public_repos"]))
        values["Followers"] = str(int(user["followers"]))
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as error:
        print(f"User statistics unavailable: {error}", file=sys.stderr)

    try:
        repositories = fetch_repositories(token)
        values["Stars received"] = str(
            sum(int(repo.get("stargazers_count", 0)) for repo in repositories)
        )
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as error:
        print(f"Repository statistics unavailable: {error}", file=sys.stderr)

    if token:
        try:
            contributions, commits = fetch_contributions(token)
            values["Contributions / 12 mo"] = str(contributions)
            values["Commits / 12 mo"] = str(commits)
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as error:
            print(f"GraphQL statistics unavailable: {error}", file=sys.stderr)
    else:
        print(
            "GITHUB_TOKEN is not set; contribution statistics use explicit fallback values.",
            file=sys.stderr,
        )

    return list(values.items())


def svg_start(width: int, height: int, description: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "  <title id=\"title\">Alexandre Edmond - AI Engineer profile</title>",
        f'  <desc id="desc">{escape(description)}</desc>',
        "  <style>",
        STYLE,
        "  </style>",
        f'  <rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="14" fill="#0d1117" stroke="#30363d" stroke-width="2"/>',
        '  <rect x="11" y="11" width="{}" height="44" rx="13" fill="#161b22"/>'.format(
            width - 22
        ),
        '  <path d="M11 42V55H{}V42" fill="#161b22"/>'.format(width - 11),
        '  <circle cx="34" cy="33" r="6" fill="#ff7b72"/>',
        '  <circle cx="54" cy="33" r="6" fill="#d29922"/>',
        '  <circle cx="74" cy="33" r="6" fill="#3fb950"/>',
        f'  <text x="{width / 2:g}" y="38" text-anchor="middle" class="mono muted" font-size="13">alexandre@github: ~</text>',
    ]


def render_robot(x: int, y: int, line_height: int, font_size: int) -> list[str]:
    return [
        f'  <text x="{x}" y="{y + index * line_height}" class="mono green" font-size="{font_size}">{escape(art_line)}</text>'
        for index, art_line in enumerate(ROBOT_ART)
    ]


def render_desktop(stats: list[tuple[str, str]]) -> str:
    width, height = 1200, 620
    lines = svg_start(
        width,
        height,
        "Terminal-style profile card with an ASCII robot, engineering focus, and GitHub statistics.",
    )
    lines.extend(
        [
            '  <line x1="365" y1="76" x2="365" y2="414" stroke="#30363d"/>',
            '  <text x="395" y="88" class="mono accent" font-size="24" font-weight="700">Alexandre Edmond</text>',
            '  <text x="395" y="110" class="mono violet" font-size="14">@AlexandreEDMOND</text>',
        ]
    )
    lines.extend(render_robot(45, 135, 26, 16))

    row_y = 143
    for label, value in PROFILE_ROWS:
        lines.extend(
            [
                f'  <text x="395" y="{row_y}" class="mono label" font-size="14">{escape(label)}</text>',
                f'  <line x1="570" y1="{row_y - 4}" x2="600" y2="{row_y - 4}" class="leader"/>',
                f'  <text x="610" y="{row_y}" class="mono value" font-size="13.5">{escape(value)}</text>',
            ]
        )
        row_y += 27

    lines.extend(
        [
            '  <line x1="35" y1="431" x2="1165" y2="431" stroke="#30363d"/>',
            '  <text x="40" y="463" class="mono green" font-size="16" font-weight="700">GitHub Stats</text>',
        ]
    )
    tile_width = 210
    for index, (label, value) in enumerate(stats):
        x = 40 + index * 225
        value_size = 25 if value == "Unavailable" else 30
        lines.extend(
            [
                f'  <rect x="{x}" y="480" width="{tile_width}" height="100" rx="6" fill="#161b22" stroke="#30363d"/>',
                f'  <text x="{x + 15}" y="509" class="mono muted" font-size="13">{escape(label)}</text>',
                f'  <text x="{x + 15}" y="553" class="mono accent" font-size="{value_size}" font-weight="700">{escape(value)}</text>',
            ]
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_mobile(stats: list[tuple[str, str]]) -> str:
    wrapped_rows = [
        (label, textwrap.wrap(value, width=57, break_long_words=False))
        for label, value in PROFILE_ROWS
    ]
    extra_lines = sum(len(value_lines) - 1 for _, value_lines in wrapped_rows)
    width, height = 600, 1080 + extra_lines * 20
    lines = svg_start(
        width,
        height,
        "Mobile terminal-style profile card with an ASCII robot, engineering focus, and GitHub statistics.",
    )
    lines.extend(render_robot(28, 82, 19, 12))
    lines.extend(
        [
            '  <text x="292" y="105" class="mono accent" font-size="23" font-weight="700">Alexandre Edmond</text>',
            '  <text x="292" y="132" class="mono violet" font-size="15">@AlexandreEDMOND</text>',
            '  <text x="292" y="168" class="mono value" font-size="15">AI Engineer</text>',
            '  <text x="292" y="191" class="mono value" font-size="15">Robot Learning</text>',
            '  <text x="292" y="214" class="mono value" font-size="15">Embodied AI</text>',
            '  <line x1="28" y1="278" x2="572" y2="278" stroke="#30363d"/>',
        ]
    )

    row_y = 309
    for label, value_lines in wrapped_rows:
        lines.extend(
            [
                f'  <text x="34" y="{row_y}" class="mono label" font-size="15">{escape(label)}</text>',
                f'  <line x1="230" y1="{row_y - 5}" x2="560" y2="{row_y - 5}" class="leader"/>',
            ]
        )
        for index, value_line in enumerate(value_lines):
            lines.append(
                f'  <text x="52" y="{row_y + 23 + index * 20}" class="mono value" font-size="15">{escape(value_line)}</text>'
            )
        row_y += 48 + (len(value_lines) - 1) * 20

    stats_y = row_y + 11
    lines.extend(
        [
            f'  <line x1="28" y1="{stats_y}" x2="572" y2="{stats_y}" stroke="#30363d"/>',
            f'  <text x="34" y="{stats_y + 32}" class="mono green" font-size="17" font-weight="700">GitHub Stats</text>',
        ]
    )
    tile_y = stats_y + 50
    positions = [
        (34, tile_y),
        (306, tile_y),
        (34, tile_y + 75),
        (306, tile_y + 75),
        (34, tile_y + 150),
    ]
    for (label, value), (x, y) in zip(stats, positions):
        tile_width = 532 if (x, y) == positions[-1] else 260
        lines.extend(
            [
                f'  <rect x="{x}" y="{y}" width="{tile_width}" height="62" rx="6" fill="#161b22" stroke="#30363d"/>',
                f'  <text x="{x + 12}" y="{y + 24}" class="mono muted" font-size="12">{escape(label)}</text>',
                f'  <text x="{x + 12}" y="{y + 49}" class="mono accent" font-size="19" font-weight="700">{escape(value)}</text>',
            ]
        )
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
    write_if_changed(ASSET_DIR / "profile-terminal.svg", render_desktop(stats))
    write_if_changed(ASSET_DIR / "profile-terminal-mobile.svg", render_mobile(stats))


if __name__ == "__main__":
    main()
