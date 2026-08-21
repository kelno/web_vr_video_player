# Catalogue and video formats

The player reads a locally generated `files.json` catalogue. Configure
`config.ini`, then run `generate_json.sh` or:

```powershell
python scripts/generate_json.py config.ini
```

The generator creates one category for each video directory and uses the
directory name as its label. Generated entries default to `sbs`. To use another
projection or stereo layout, edit an entry’s `screen_type` in `files.json`, or
provide a catalogue from another source.

## Catalogue structure

```json
{
  "videos": [
    {
      "name": "Music",
      "list": [
        {
          "name": "K-POP COVER DANCE",
          "src": "/vr-player/media/Music/K-POP%20COVER%20DANCE.mp4",
          "thumbnail": "/vr-player/thumbnails/Music/K-POP%20COVER%20DANCE.jpg",
          "screen_type": "sbs",
          "date": "2023-01-10 15:05:50",
          "epoch": "1673359550.854825"
        }
      ]
    }
  ]
}
```

Each category has a display `name` and a `list` of videos. `src` and
`thumbnail` must be browser-accessible URLs. `date` and `epoch` support date
sorting. Flat videos can additionally supply `frame_height` and `frame_width`.

## Screen types

| Value | Layout |
| --- | --- |
| `sbs` | Side-by-side 180° |
| `tb` | Top-bottom 180° |
| `360` | Top-bottom 360° |
| `sphere180` | Single-lens fisheye 180°, not VR |
| `sphere360` | Single-lens fisheye 360°, not VR |
| `screen` | Normal 2D screen |
