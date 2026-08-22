#!/usr/bin/env python3
"""Prepare MP4 and MKV files for responsive browser playback.

The default mode is read-only. MP4 files are checked for fast-start metadata.
MKV files can be remuxed to MP4 with --apply, but only when all media streams
can be preserved. Successful conversions replace their sources by default;
--keep-original retains each source. --force permits a video/audio-only
conversion. No command in this script re-encodes media.
"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from typing import BinaryIO


VIDEO_SUFFIXES = {".mkv", ".mp4"}
MP4_SUBTITLE_CODECS = {"mov_text"}


def find_top_level_boxes(stream: BinaryIO) -> list[tuple[str, int, int]]:
    """Return (type, offset, size) for valid top-level ISO BMFF boxes."""
    boxes: list[tuple[str, int, int]] = []
    stream.seek(0, io.SEEK_END)
    file_size = stream.tell()
    stream.seek(0)

    while stream.tell() < file_size:
        offset = stream.tell()
        header = stream.read(8)
        if len(header) != 8:
            raise ValueError(f"Truncated box header at byte {offset}.")
        size, raw_type = struct.unpack(">I4s", header)
        box_type = raw_type.decode("ascii", errors="replace")
        header_size = 8
        if size == 1:
            extended_size = stream.read(8)
            if len(extended_size) != 8:
                raise ValueError(f"Truncated extended size at byte {offset}.")
            size = struct.unpack(">Q", extended_size)[0]
            header_size = 16
        elif size == 0:
            size = file_size - offset
        if size < header_size or offset + size > file_size:
            raise ValueError(f"Invalid {box_type!r} box size at byte {offset}.")
        boxes.append((box_type, offset, size))
        stream.seek(offset + size)
    return boxes


def needs_faststart(path: Path) -> bool:
    """Return whether an MP4 stores moov after mdat."""
    with path.open("rb") as stream:
        box_types = [box_type for box_type, _, _ in find_top_level_boxes(stream)]
    try:
        return box_types.index("moov") > box_types.index("mdat")
    except ValueError as error:
        raise ValueError("Missing required moov or mdat box.") from error


def probe_streams(path: Path, ffprobe: str) -> list[dict[str, str]]:
    """Return stream types and codecs from ffprobe's JSON output."""
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "stream=codec_type,codec_name", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise ValueError("No media streams found.")
    return streams


def mkv_copy_risks(streams: list[dict[str, str]]) -> list[str]:
    """List source streams that cannot safely be copied into an MP4."""
    risks: list[str] = []
    for stream in streams:
        stream_type = stream.get("codec_type", "unknown")
        codec_name = stream.get("codec_name", "unknown")
        if stream_type in {"video", "audio"}:
            continue
        if stream_type == "subtitle" and codec_name in MP4_SUBTITLE_CODECS:
            continue
        risks.append(f"{stream_type} ({codec_name})")
    return risks


def stream_signature(streams: list[dict[str, str]]) -> list[tuple[str, str]]:
    """Create a stable comparison value for expected media streams."""
    return sorted(
        (stream.get("codec_type", "unknown"), stream.get("codec_name", "unknown"))
        for stream in streams
    )


def remux_to_mp4(
    source: Path,
    output: Path,
    ffmpeg: str,
    ffprobe: str,
    *,
    force: bool = False,
    original_backup: Path | None = None,
) -> None:
    """Stream-copy a file to fast-start MP4 and verify its expected streams."""
    temporary = output.with_name(f".{output.stem}.faststart-tmp{output.suffix}")
    if temporary.exists():
        raise FileExistsError(f"Temporary output already exists: {temporary}")
    input_streams = probe_streams(source, ffprobe)
    stream_map = ["-map", "0:v?", "-map", "0:a?"] if force else ["-map", "0"]
    expected = (
        [stream for stream in input_streams if stream.get("codec_type") in {"video", "audio"}]
        if force else input_streams
    )
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source), *stream_map,
               "-c", "copy", "-movflags", "+faststart", str(temporary)]
    try:
        subprocess.run(command, check=True)
        if needs_faststart(temporary):
            raise RuntimeError("ffmpeg output still needs fast-start remuxing.")
        if stream_signature(probe_streams(temporary, ffprobe)) != stream_signature(expected):
            raise RuntimeError("ffmpeg output did not preserve the expected media streams.")
        if original_backup is not None:
            if original_backup.exists():
                raise FileExistsError(f"Original backup already exists: {original_backup}")
            os.replace(source, original_backup)
        try:
            os.replace(temporary, output)
        except OSError:
            if original_backup is not None and original_backup.exists() and not source.exists():
                os.replace(original_backup, source)
            raise
    finally:
        temporary.unlink(missing_ok=True)


def find_videos(directory: Path, recursive: bool) -> list[Path]:
    """Find MP4 and MKV files, including upper-case extensions."""
    iterator = directory.rglob("*") if recursive else directory.glob("*")
    return sorted(
        (path for path in iterator if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES),
        key=lambda path: str(path).lower(),
    )


def mkv_output_path(path: Path) -> Path:
    """Return the sibling MP4 path produced from an MKV source."""
    return path.with_suffix(".mp4")


def original_backup_path(path: Path) -> Path:
    """Return a retained MP4 source path that is ignored by future scans."""
    return path.with_name(f"{path.name}.original")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing MP4 or MKV files")
    parser.add_argument("--apply", action="store_true", help="Make safe remuxes")
    parser.add_argument("--force", action="store_true", help="For MKVs, copy video/audio only into MP4")
    parser.add_argument(
        "--keep-original",
        action="store_true",
        help="Keep each source; retained MP4s are renamed with a .original suffix",
    )
    parser.add_argument("--recursive", action="store_true", help="Also scan subdirectories")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable to run")
    parser.add_argument("--ffprobe", default="ffprobe", help="ffprobe executable to run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.directory.is_dir():
        print(f"Not a directory: {args.directory}", file=sys.stderr)
        return 2
    if args.force and not args.apply:
        print("--force requires --apply.", file=sys.stderr)
        return 2
    files = find_videos(args.directory, args.recursive)
    if not files:
        print("No MP4 or MKV files found.")
        return 0
    if args.apply and shutil.which(args.ffmpeg) is None:
        print(f"ffmpeg was not found: {args.ffmpeg}", file=sys.stderr)
        return 2
    # A dry-run only probes MKVs, while every actual remux verifies its output.
    requires_ffprobe = args.apply or any(path.suffix.lower() == ".mkv" for path in files)
    if requires_ffprobe and shutil.which(args.ffprobe) is None:
        print(f"ffprobe was not found: {args.ffprobe}", file=sys.stderr)
        return 2

    remuxed = 0
    for path in files:
        if path.suffix.lower() == ".mkv":
            try:
                risks = mkv_copy_risks(probe_streams(path, args.ffprobe))
            except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
                print(f"ERROR  {path}: {error}")
                continue
            output = mkv_output_path(path)
            if output.exists():
                print(f"SKIP OUTPUT EXISTS  {path} -> {output}")
                continue
            if risks and not args.force:
                print(f"SKIP INCOMPATIBLE STREAMS  {path}: {', '.join(risks)}")
                continue
            if not args.apply:
                print(f"NEEDS MP4 REMUX  {path} -> {output}")
                continue
            suffix = " (video/audio only)" if risks else ""
            print(f"REMUXING MKV{suffix}  {path} -> {output}")
            try:
                remux_to_mp4(path, output, args.ffmpeg, args.ffprobe, force=bool(risks))
            except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
                print(f"ERROR  {path}: {error}")
                continue
            remuxed += 1
            if args.keep_original:
                print(f"REMUXED (KEPT SOURCE)  {output}")
                continue
            try:
                path.unlink()
            except OSError as error:
                print(f"WARNING  {output} was created, but could not remove {path}: {error}")
                continue
            print(f"REMUXED (REPLACED SOURCE)  {output}")
            continue

        try:
            requires_remux = needs_faststart(path)
        except (OSError, ValueError) as error:
            print(f"ERROR  {path}: {error}")
            continue
        if not requires_remux:
            print(f"READY  {path}")
            continue
        if not args.apply:
            print(f"NEEDS REMUX  {path}")
            continue
        backup = original_backup_path(path) if args.keep_original else None
        if backup is not None and backup.exists():
            print(f"SKIP ORIGINAL EXISTS  {path} -> {backup}")
            continue
        print(f"REMUXING  {path}")
        try:
            remux_to_mp4(path, path, args.ffmpeg, args.ffprobe, original_backup=backup)
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
            print(f"ERROR  {path}: {error}")
            continue
        remuxed += 1
        if backup is None:
            print(f"REMUXED  {path}")
        else:
            print(f"REMUXED (KEPT SOURCE)  {path}; original at {backup}")

    if args.apply:
        print(f"Remuxed {remuxed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
