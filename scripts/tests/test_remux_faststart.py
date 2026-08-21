import io
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from remux_faststart import (
    find_top_level_boxes,
    find_videos,
    mkv_copy_risks,
    mkv_output_path,
    needs_faststart,
)


def box(box_type: bytes, payload: bytes = b"") -> bytes:
    return struct.pack(">I4s", len(payload) + 8, box_type) + payload


class FaststartTests(unittest.TestCase):
    def test_reads_top_level_boxes(self):
        stream = io.BytesIO(box(b"ftyp") + box(b"moov") + box(b"mdat", b"video"))
        self.assertEqual(
            [box_type for box_type, _, _ in find_top_level_boxes(stream)],
            ["ftyp", "moov", "mdat"],
        )

    def test_detects_metadata_after_media_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "late.mp4"
            path.write_bytes(box(b"ftyp") + box(b"mdat", b"video") + box(b"moov"))
            self.assertTrue(needs_faststart(path))

    def test_accepts_metadata_before_media_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ready.mp4"
            path.write_bytes(box(b"ftyp") + box(b"moov") + box(b"mdat", b"video"))
            self.assertFalse(needs_faststart(path))

    def test_finds_mp4_and_mkv_files_case_insensitively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "video.MP4").touch()
            (root / "video.mkv").touch()
            (root / "notes.txt").touch()
            self.assertEqual(
                [path.name for path in find_videos(root, recursive=False)],
                ["video.mkv", "video.MP4"],
            )

    def test_safe_mkv_remux_allows_multiple_audio_tracks(self):
        streams = [
            {"codec_type": "video", "codec_name": "h264"},
            {"codec_type": "audio", "codec_name": "aac"},
            {"codec_type": "audio", "codec_name": "aac"},
        ]
        self.assertEqual(mkv_copy_risks(streams), [])

    def test_safe_mkv_remux_rejects_subtitles_and_attachments(self):
        streams = [
            {"codec_type": "video", "codec_name": "h264"},
            {"codec_type": "subtitle", "codec_name": "ass"},
            {"codec_type": "attachment", "codec_name": "ttf"},
        ]
        self.assertEqual(
            mkv_copy_risks(streams),
            ["subtitle (ass)", "attachment (ttf)"],
        )

    def test_mkv_output_keeps_original_source(self):
        self.assertEqual(mkv_output_path(Path("clip.mkv")), Path("clip.mp4"))
