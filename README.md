
### Kelno's fork notes
Forked from https://github.com/michal-repo/web_vr_video_player  
Readme has been updated to reflect changes.  

#### Changes
- Misc changes to file loading, trying to make it more reliable. It's still a mess but it works for me now.  
- Cleaned up build system.  
- Rewritten the generation scripts and related config. Some previous features dropped for now.  
- The files generation script will auto generate categories based on the directories the videos are in.  
- Changed default zoom to 180 for SBS.  

---

# Web VR video player for 180° videos.

## If you liked it you can support my work
[!["Buy Me A Coffee"](https://raw.githubusercontent.com/michal-repo/random_stuff/refs/heads/main/bmac_small.png)](https://buymeacoffee.com/michaldev)

## Licenses

### Source code Licensed under MIT License

### Icons are licensed under "Free for commercial use with attribution license"

### Fonts are licensed under the Apache License, Version 2.0.

## Functionality
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

*Player controls and spheres will reset to default position on exit from current video playback*
### Gamepad controls
#### Playback control
Thumbstick: 
- up/down for zoom
- left/right for rewind and fast forward (10 seconds jumps)

*If there are two connected controllers pressing trigger switches active controller.*

#### Folders view
Thumbstick: 
- left/right for switching pages

## Demo
[on Github Pages](https://michal-repo.github.io/web_vr_video_player/)

## Requirements

- Web server configured for https (WebXR requires https)
- Python 3
- (optional) FFMPEG, to generate thumbnails

## Setup

### Using JSON solution and provided Python scripts

- Copy `config.ini.example` to `config.ini`
- Edit `config.ini`
- Edit `config.ini` providing correct paths
    All those paths need to be accessible on the same partition. You can use symlink to help that if needed.

(needs reimplementation) Script can set screen type based on file name. Add one of following at the end of file name: `_TB` (Top-Bottom), `_SCREEN`. Default screen type is Side-by-Side.

Supported tags:

- `_SCREEN` - normal 2D screen
- `_SBS` - Side by Side
- `_TB` - Top Bottom 180
- `_360` - Top Bottom 360
- `_2D_180` - fisheye 180, not VR (one lens)
- `_2D_360` - fisheye 360, not VR (one lens)

### Extensions

[Extensions](https://github.com/michal-repo/web_vr_video_player_extensions)

## Generating your own JSON file with video sources

Player is using locally stored "files.json" with video sources.  
To use the included generation script, Configure `config.ini`, then generate with `generate_json.sh`.  
The files generation script will auto generate categories based on the directories the videos are in.

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

## Building

### Development mode

```
npm install
npm run build-dev
```

### Production mode

```
npm install
npm run build
```
