# Web VR video player

A self-hosted WebXR video library for stereoscopic 180° and 360° video, with
an in-headset library browser and playback controls.

This repository began as a fork of
[michal-repo/web_vr_video_player](https://github.com/michal-repo/web_vr_video_player).

## Licenses

### Source code Licensed under MIT License

### Icons are licensed under "Free for commercial use with attribution license"

### Fonts are licensed under the Apache License, Version 2.0.

## Functionality

- Browse video categories generated from the library's directory structure.
- Search and sort the current category.
- Play SBS, top-bottom, 360°, fisheye, and flat video entries defined in
  `files.json`.
- Select a video from the library, then wait for browser media metadata before
  switching into the player.

### Search in current folder

Search will filter current folder with provided phrase.
You can switch folders, search phrase will work until it's cleared.

![Search-box](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_4.png?raw=true)

![Search-box-keyboard](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_4_1.png?raw=true)

### Sorting

Sort by Name or Date, change order ascending/descending.

![Sorting](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_5.png?raw=true)

### Drag in Folders view

You can reposition Folders view by holding trigger and dragging view using bottom bar.

![drag](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_6.png?raw=true)

### Drag in Player view

You can reposition Player and Video Spheres by holding trigger and dragging view using bottom bar.

![drag](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_7.png?raw=true)

Second options is to reposition only Player controls

![drag](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_8.png?raw=true)

_Player controls and spheres will reset to default position on exit from current video playback_

### Gamepad controls

#### Playback control

Thumbstick:

- up/down for zoom (SBS playback starts at a 180° zoom)
- left/right for rewind and fast forward (10 seconds jumps)

_If there are two connected controllers pressing trigger switches active controller._

#### Folders view

Thumbstick:

- left/right for switching pages

## Demo

[on Github Pages](https://michal-repo.github.io/web_vr_video_player/)

## Requirements

- Node.js and npm (needed to install dependencies and build the browser bundle)
- A static web server (needed to load `files.json`; opening `index.html` directly
  from disk will not work)
- Python 3 (needed only to generate `files.json`)
- FFmpeg and FFprobe (optional; needed only to generate thumbnails)

## Running the player

The application is a static web site after it has been built. It has no
application server, database, or Node.js server to run at runtime. A static web
server must serve the repository root, including `index.html`, `dist/`, and the
generated `files.json` file.

### First-time setup

Install the locked dependency versions:

```powershell
npm ci
```

Create `config.ini` from `config.ini.example` and set the paths to the video
library, optional thumbnail library, and this player directory. Then generate
the video catalogue:

```bash
./generate_json.sh
```

The generator writes `files.json` to the repository root. Run it again after
adding, removing, or moving videos. The bundled scripts use Bash; on Windows,
run them from WSL or Git Bash. Alternatively, run the Python generator directly:

```powershell
python scripts/generate_json.py config.ini
```

### Local development

The project does not include a development server, but Webpack can rebuild the
bundle whenever a source file changes. Run this in one terminal:

```powershell
npm run build-dev -- --watch
```

Then serve the repository root from a second terminal:

```powershell
py -m http.server 8000
```

Open `http://localhost:8000` in a desktop browser. On Linux and macOS, use
`python3 -m http.server 8000` instead. Stop the watcher with `Ctrl+C` when you
are finished.

`http://localhost` is suitable for desktop development. To enter immersive VR
from a headset at a LAN address, serve the site over HTTPS with a certificate
trusted by the headset; WebXR is available only in secure contexts.

### Production build and deployment

Create an optimized bundle with:

```powershell
npm run build
```

Deploy the repository root through any static HTTPS web server. Ensure that the
server can read the video and thumbnail paths written to `files.json`, and that
it supports HTTP byte-range requests so video seeking works.

### Extensions

[Extensions](https://github.com/michal-repo/web_vr_video_player_extensions)

## Generating your own JSON file with video sources

The player reads a locally generated `files.json` catalogue. Configure
`config.ini`, then run `generate_json.sh` (or the direct Python command shown
above). The generator creates one category for each video directory and uses
the directory's name as the category label.

Generated entries currently default to `sbs`. To use another projection or
stereo layout, edit the entry's `screen_type` in `files.json` or provide a
catalogue from another source.

## Generating thumbnails

Configure `config.ini`, then generate with `generate_thumbnails.sh`.  
ffmpeg & ffprobe need to be in path.

### Structure for JSON file

```
{
    "videos": [
        {
            "name": "FOLDER_NAME",
            "list": [
                {
                    "name": "FILE NAME DISPLAYED IN UI",
                    "src": "SOURCE URL TO VIDEO FILE",
                    "thumbnail": "SOURCE URL TO THUMBNAIL FILE",
                    "screen_type": "TYPE OF SCREEN",
                    "date": "DATE TIME (Python format: %Y-%m-%d %H:%M:%S)",
                    "epoch": "(Python format: %s)"
                }
            ]
        }
    ]
}
```

#### Screen type

`"screen_type"` can be set to one of values:

`sbs` - Side by Side

`tb` - Top Bottom 180

`360` - Top Bottom 360

`sphere180` - fisheye 180, not VR (one lens)

`sphere360` - fisheye 360, not VR (one lens)

`screen` - normal 2D screen

#### JSON Example

```
{
    "videos": [
        {
            "name": "Music",
            "list": [
                {
                    "name": "K-POP COVER DANCE",
                    "src": "../videos/Music/K-POP%20COVER%20DANCE.mp4",
                    "thumbnail": "../videos/Thumbnails/Music/K-POP%20COVER%20DANCE.jpg",
                    "screen_type": "sbs",
                    "date": "2023-01-10 15:05:50",
                    "epoch": "1673359550.854825"
                },
                {
                    "name": "Live Music at the Miami Beach",
                    "src": "https://10.10.10.12/videos/Music/Live%20Music%20at%20the%20Miami%20Beach.mp4",
                    "thumbnail": "https://10.10.10.12/videos/Thumbnails/Music/Live%20Music%20at%20the%20Miami%20Beach.jpg",
                    "screen_type": "tb",
                    "date": "2022-12-27 21:13:20",
                    "epoch": "1672172000.0444932"
                },
                ....
                ]
        },
        {
            "name": "Nature",
            "list": [
                {
                    "name": "Sunset Baltic in Germany",
                    "src": "../videos/Nature/Sunset%20Baltic%20in%20Germany.mp4",
                    "thumbnail": "../videos/Thumbnails/Nature/Sunset%20Baltic%20in%20Germany.jpg",
                    "screen_type": "sbs",
                    "date": "2023-01-10 15:05:50",
                    "epoch": "1673359550.854825"
                },
                ....
                ]
        },
        {
            "name": "Movies",
            "list": [
                {
                    "name": "The Good the Bad and the Ugly",
                    "src": "../videos/Movies/The%20Good%20the%20Bad%20and%20the%20Ugly.mp4",
                    "thumbnail": "../videos/Thumbnails/Movies/The%20Good%20the%20Bad%20and%20the%20Ugly.jpg",
                    "screen_type": "screen",
                    "frame_height": "720",
                    "frame_width": "1280",
                    "date": "2023-01-10 15:05:50",
                    "epoch": "1673359550.854825"
                },
                ....
                ]
        },
        ....
    ]
}
```

## Troubleshooting

If videos or player can't be loaded make sure that this app files are owned by web server user (eg. www-data) and that web server user can read video and thumbnail files (eg. www-data is owner or permissions for others include read).

## Screenshots

![Print-screen-1](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_1.png?raw=true)

![Print-screen-2](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_2.png?raw=true)

![Print-screen-3](https://github.com/michal-repo/web_vr_video_player/blob/main/examples/Screenshot_VR_player_3.png?raw=true)
