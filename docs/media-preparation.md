# Prepare media for streaming

## Generate thumbnails

Configure `config.ini`, then run:

```bash
./generate_thumbnails.sh
```

`ffmpeg` and `ffprobe` must be available on `PATH`.

## Make MP4s stream efficiently

Large MP4 files load promptly only when their `moov` metadata atom precedes
the media data. Check a directory without modifying files:

```powershell
python scripts/remux_faststart.py D:\download\my_library --recursive
```

The script reports MP4s as `READY` or `NEEDS REMUX` and also finds MKVs. To
remux safe MP4s in place and replace compatible MKVs with `.mp4`, opt in:

```powershell
python scripts/remux_faststart.py D:\download\my_library --recursive --apply
```

It uses `ffmpeg -c copy -movflags +faststart`, so it rewrites the container
without re-encoding audio or video. An MKV is deleted only after its MP4 output
has been validated, and multiple audio tracks are preserved. MKVs with
incompatible subtitle, attachment, or data streams are skipped and explained.

Add `--keep-original` to retain source MKVs. To deliberately create a
video/audio-only MP4 from incompatible files, use `--force` with `--apply`:

```powershell
python scripts/remux_faststart.py D:\download\my_library --recursive --apply --force
```

`ffmpeg` and `ffprobe` must be available on `PATH`. The script validates the
expected output streams before publishing an output file. Regenerate
`files.json` after MKV conversions so the catalogue uses the new `.mp4` paths.
