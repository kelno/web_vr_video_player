import configparser
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generate_json import generate_category_entries, join_url_prefix, url_for_file, write_catalogue


class GenerateCatalogueTests(unittest.TestCase):
    def test_url_for_file_uses_url_prefix_not_project_path(self):
        self.assertEqual(
            url_for_file("/media", Path("New folder/video #1.mp4")),
            "/media/New%20folder/video%20%231.mp4",
        )

    def test_url_for_file_rejects_relative_prefix(self):
        with self.assertRaises(ValueError):
            url_for_file("media", Path("video.mp4"))

    def test_joins_media_route_under_site_subpath(self):
        self.assertEqual(join_url_prefix("/vr-player", "/media"), "/vr-player/media")
        self.assertEqual(join_url_prefix("/", "/media"), "/media")

    def test_generates_media_and_thumbnail_urls_from_configured_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            videos = root / "unrelated-video-location"
            thumbnails = root / "thumbnail-location"
            (videos / "Category").mkdir(parents=True)
            (thumbnails / "Category").mkdir(parents=True)
            (videos / "Category" / "VR test.mp4").touch()
            (thumbnails / "Category" / "VR test.jpg").touch()
            config = configparser.ConfigParser()
            config["videos"] = {
                "videos_path": str(videos),
                "thumbnails_path": str(thumbnails),
                "site_url_prefix": "/vr-player",
                "videos_url_prefix": "/media",
                "thumbnails_url_prefix": "/thumbnails",
            }

            categories = generate_category_entries(config["videos"])
            entry = categories["Category"][0]
            self.assertEqual(entry["src"], "/vr-player/media/Category/VR%20test.mp4")
            self.assertEqual(entry["thumbnail"], "/vr-player/thumbnails/Category/VR%20test.jpg")

    def test_writes_catalogue_to_requested_release_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dist" / "files.json"
            count = write_catalogue({"!Uncategorized": []}, output)
            self.assertEqual(count, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"videos": [{"name": "!Uncategorized", "list": []}]})
