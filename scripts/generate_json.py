import os
import json
from datetime import datetime
from collections import defaultdict
import sys
import configparser
from pathlib import Path
from common import is_video_file

# Define the output directory
OUTPUT_DIR = Path(__file__).resolve().parent.parent

if not len(sys.argv) > 1:
    print("Usage: pass config ini file as first parameter, you can force metadata rescan by setting second parameter to true (false by default)\neg.\npython3 generateJson.py config.ini\npython3 generateJson.py config.ini true")
    quit()

configFile = sys.argv[1]

if not os.path.isfile(configFile):
    print("Passed ini file do not exist")
    quit()

config = configparser.ConfigParser()
config.read(configFile)

def clean_filename(filename):
    # Remove common prefixes and file extensions
    prefixes = ('SpankBang.com_', 'vrporncom_', 'WankzVR - ', ' - ')
    for prefix in prefixes:
        if filename.startswith(prefix):
            filename = filename[len(prefix):]

    # Remove file extension
    filename = os.path.splitext(filename)[0]

    # Replace special characters with spaces
    replacements = {'+': ' ', '_': ' ', '__': ' ', '  ': ' '}
    for old, new in replacements.items():
        filename = filename.replace(old, new)

    # Title case except for resolution indicators
    parts = []
    for part in filename.split():
        if part.lower() in ('4k', '1080p', '180', '6k', '1920p'):
            parts.append(part)
        else:
            parts.append(part.title())

    return ' '.join(parts).strip()

def get_file_timestamps(filepath):
    mtime = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(mtime)
    return {
        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "epoch": str(mtime)
    }

def generate_category_entries():
    videos_dir = Path(config['videos']['videos_location']) / config['videos']['videos_folder']
    thumbnails_dir = Path(config['videos']['videos_location']) / config['videos']['thumbnails_folder']
    videos_relative_path = str(config['videos']['videos_relative_path_to_player'])
    category_map = defaultdict(list)

    if not os.path.exists(videos_dir):
        raise FileNotFoundError(f"Videos directory not found at {os.path.abspath(videos_dir)}")

    for root, _, files in os.walk(videos_dir):
        for file in files:
            if is_video_file(file):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=videos_dir)
                rel_dir = os.path.dirname(rel_path)

                timestamps = get_file_timestamps(full_path)

                # Use directory name as category, or "Uncategorized" for root
                category_name = os.path.basename(rel_dir) if rel_dir else "Uncategorized"

                thumbnail_path = (thumbnails_dir / rel_path.replace(os.path.sep, '/')).with_suffix('.jpg')
                thumbnail_exists = thumbnail_path.exists()

                src = f"{videos_relative_path}/{rel_path.replace(os.path.sep, '/')}"
                print(f"Processing file: {file}")
                print(f"Category: {category_name}")
                print(f"src: {src}")
                
                thumb_rel_path = f"{videos_relative_path}/{str(thumbnail_path.relative_to(thumbnails_dir).as_posix())}" if thumbnail_exists else ""
                print(f"Thumbnail path: {thumb_rel_path}")

                entry = {
                    "name": clean_filename(file),
                    "src": src,
                    "thumbnail": thumb_rel_path,
                    "screen_type": "sbs",
                    "date": timestamps["date"],
                    "epoch": timestamps["epoch"]
                }
                category_map[category_name].append(entry)

    return category_map

def main():
    try:
        category_map = generate_category_entries()

        video_data = {
            "videos": [
                {
                    "name": category,
                    "list": sorted(entries, key=lambda x: float(x["epoch"]), reverse=True)
                } for category, entries in sorted(category_map.items())
            ]
        }

        output_file = OUTPUT_DIR / 'files.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=4, ensure_ascii=False)

        print(f"files.json created successfully at {os.path.abspath(output_file)}")
        print(f"Found {len(video_data['videos'])} categories with {sum(len(cat['list']) for cat in video_data['videos'])} total videos")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
