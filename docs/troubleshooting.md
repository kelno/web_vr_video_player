# Troubleshooting

If videos or the player do not load, make sure the web-server user (for
example `www-data`) owns or can read the application files, video files, and
thumbnail files.

Also confirm that the Nginx URL paths match `[web]` in `config.ini` and that
the deployed catalogue was generated after the latest build.
