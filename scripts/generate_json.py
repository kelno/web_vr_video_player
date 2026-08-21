#!/usr/bin/env python3
"""Generate the player catalogue inside the self-contained dist directory."""

from __future__ import annotations

import argparse
import configparser
from collections import defaultdict
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote

from common import is_video_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "dist" / "files.json"


def clean_filename(filename: str) -> str:
    """Turn a source filename into a readable library label."""
    prefixes = ("SpankBang.com_", "vrporncom_", "WankzVR - ", " - ")
    for prefix in prefixes:
        if filename.startswith(prefix):
            filename = filename[len(prefix) :]
    filename = os.path.splitext(filename)[0]
    for old, new in {"+": " ", "_": " ", "__": " ", "  ": " "}.items():
        filename = filename.replace(old, new)
    return " ".join(
        part if part.lower() in {"4k", "1080p", "180", "6k", "1920p"} else part.title()
        for part in filename.split()
    ).strip()


def get_file_timestamps(filepath: Path) -> dict[str, str]:
    """Return display and sorting timestamps for a source media file."""
    mtime = filepath.stat().st_mtime
    return {
        "date": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "epoch": str(mtime),
    }


def url_for_file(prefix: str, relative_path: Path) -> str:
    """Join a configured URL prefix to a safely escaped library-relative path."""
    if not prefix.startswith("/"):
        raise ValueError(f"URL prefix must start with '/': {prefix}")
    return f"{prefix.rstrip('/')}/{quote(relative_path.as_posix(), safe='/')}"


def join_url_prefix(site_prefix: str, route_prefix: str) -> str:
    """Put a media route under the player site path, including root sites."""
    if not site_prefix.startswith("/") or not route_prefix.startswith("/"):
        raise ValueError("URL prefixes must start with '/'.")
    site = site_prefix.rstrip("/")
    route = route_prefix.rstrip("/")
    return f"{site}{route}" or "/"


def load_config(config_path: Path) -> configparser.ConfigParser:
    """Read and validate the separate local-library and web configuration."""
    config = configparser.ConfigParser()
    if not config.read(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    for section_name in ("library", "web"):
        if section_name not in config:
            raise ValueError(f"Configuration must contain a [{section_name}] section.")
    section = config["library"]
    for option in ("videos_path", "thumbnails_path"):
        if not section.get(option):
            raise ValueError(f"Missing required [library] value: {option}")
    return config


def generate_category_entries(config: configparser.ConfigParser) -> dict[str, list[dict[str, str]]]:
    """Build category entries using media roots and server URL prefixes only."""
    library = config["library"]
    web = config["web"]
    videos_dir = Path(library["videos_path"])
    thumbnails_dir = Path(library["thumbnails_path"])
    site_url_prefix = web.get("site_url_prefix", "/")
    videos_url_prefix = join_url_prefix(site_url_prefix, web.get("videos_url_prefix", "/media"))
    thumbnails_url_prefix = join_url_prefix(
        site_url_prefix, web.get("thumbnails_url_prefix", "/thumbnails")
    )
    if not videos_dir.is_dir():
        raise FileNotFoundError(f"Videos directory not found: {videos_dir}")

    category_map: dict[str, list[dict[str, str]]] = defaultdict(list)
    for root, _, files in os.walk(videos_dir):
        root_path = Path(root)
        for filename in files:
            if not is_video_file(filename):
                continue
            video_path = root_path / filename
            relative_path = video_path.relative_to(videos_dir)
            thumbnail_path = (thumbnails_dir / relative_path).with_suffix(".jpg")
            category_name = root_path.name if root_path != videos_dir else "!Uncategorized"
            entry = {
                "name": clean_filename(filename),
                "src": url_for_file(videos_url_prefix, relative_path),
                "thumbnail": (
                    url_for_file(thumbnails_url_prefix, relative_path.with_suffix(".jpg"))
                    if thumbnail_path.exists()
                    else ""
                ),
                "screen_type": "sbs",
                **get_file_timestamps(video_path),
            }
            category_map[category_name].append(entry)
    return category_map


def write_catalogue(category_map: dict[str, list[dict[str, str]]], output_path: Path) -> int:
    """Write sorted catalogue data and return the number of video entries."""
    video_data = {
        "videos": [
            {"name": category, "list": sorted(entries, key=lambda item: float(item["epoch"]), reverse=True)}
            for category, entries in sorted(category_map.items())
        ]
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(video_data, indent=4, ensure_ascii=False), encoding="utf-8")
    return sum(len(category["list"]) for category in video_data["videos"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to config.ini")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Catalogue output path (default: {DEFAULT_OUTPUT_PATH})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        category_map = generate_category_entries(load_config(args.config))
        video_count = write_catalogue(category_map, args.output)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"files.json created at {args.output.resolve()}")
    print(f"Found {len(category_map)} categories with {video_count} total videos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
