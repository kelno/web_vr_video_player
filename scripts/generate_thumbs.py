import os
import configparser
import subprocess
from pathlib import Path
from common import is_video_file

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '../config.ini')
print(f"Reading config from: {config_path}")
config.read(config_path)

videos_path = Path(config['videos']['videos_path'])
thumbnails_path = Path(config['videos']['thumbnails_path'])

print(f"Videos path: {videos_path}")
print(f"Thumbnails path: {thumbnails_path}")

# Create folder tree for Thumbnails
print("Creating thumbnail folder structure...")
for dirpath, dirnames, filenames in os.walk(videos_path):
    rel_dir = os.path.relpath(dirpath, videos_path)
    thumb_dir = thumbnails_path / rel_dir
    if not thumb_dir.exists():
        print(f"Creating directory: {thumb_dir}")
    thumb_dir.mkdir(parents=True, exist_ok=True)

# Find video files and generate Thumbnails
print("Searching for video files and generating thumbnails...")
for dirpath, dirnames, filenames in os.walk(videos_path):
    rel_dir = os.path.relpath(dirpath, videos_path)
    thumb_dir = thumbnails_path / rel_dir
    for filename in filenames:
        if is_video_file(filename):
            video_file = Path(dirpath) / filename
            thumb_file = Path(thumb_dir / filename).with_suffix(".jpg")
            if not thumb_file.exists():
                print(f"Generating thumbnail for: {video_file}")
                result = subprocess.run([
                    "ffmpeg",
                    "-loglevel", "panic",
                    "-nostdin",
                    "-ss", "20",
                    "-i", str(video_file),
                    "-filter:v", "crop=in_w/2:in_h:0:0,scale=512:-1",
                    "-vframes", "1",
                    "-q:v", "2",
                    str(thumb_file),
                    "-y"
                ])
                if result.returncode == 0:
                    print(f"Thumbnail saved to: {thumb_file}")
                else:
                    print(f"Failed to generate thumbnail for: {video_file}")
            else:
                print(f"Thumbnail already exists for: {video_file}")
                
print("All done!")
