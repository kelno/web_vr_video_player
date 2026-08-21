# Get started

## Requirements

- Node.js and npm to install dependencies and build the browser bundle.
- A static web server: opening `index.html` directly from disk cannot load `files.json`.
- Python 3 to generate `files.json`.
- FFmpeg and FFprobe, only when generating thumbnails or preparing media.

## First-time setup

Install the locked dependency versions:

```powershell
npm ci
```

Create `config.ini` from `config.ini.example`. Set local video and thumbnail
library paths, the player site path (for example `/vr-player`), and the media
URL prefixes Nginx exposes below it. In `[player]`, `default_sbs_zoom` accepts
0 through 180 and defaults to 100. The project’s own filesystem path is not
part of this configuration.

Generate the catalogue:

```bash
./generate_json.sh
```

The generator writes `dist/files.json`. Run it after adding, removing, or
moving videos. The shell scripts use Bash; on Windows use WSL or Git Bash.
Alternatively run the generator directly:

```powershell
python scripts/generate_json.py config.ini
```

`[library]` holds local filesystem paths used by the Python tooling and the
development server; `[web]` defines browser and Nginx URL paths; `[player]`
contains browser-safe player preferences. Configurations using `[videos]` must
move local paths to `[library]` and URL prefixes to `[web]`.

## Local development

Run the HTTPS development server from the repository root:

```powershell
npm run dev
```

It rebuilds on source changes and serves the player at port 8040. It reads the
media paths and URL prefixes from `config.ini`, so local playback uses the same
site and media URL contract as Nginx. Open the configured site path after the
printed desktop or LAN URL (for example `/vr-player/`). Stop it with `Ctrl+C`.

Webpack generates a self-signed development certificate. In a headset, open
the printed HTTPS URL and accept its one-time certificate warning before
entering WebXR.

For production build and serving instructions, see [Deploy with Nginx](deployment.md).
