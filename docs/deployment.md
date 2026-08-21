# Deploy with Nginx

The application is a static website after building. There is no application
server, database, or Node.js server at runtime. `dist/` is the complete player
release: HTML, browser bundle, assets, and generated catalogue.

Create an optimized bundle:

```powershell
npm run build
```

Then generate the catalogue, because the build clears old output:

```powershell
python scripts/generate_json.py config.ini
```

Deploy the resulting `dist/` directory as a single unit. Configure Nginx to
serve it at the configured site path and map `/media/` and `/thumbnails/` to
the actual library directories. Nginx must be able to read those directories
and support HTTP byte-range requests for video seeking.

Use [nginx.conf.example](nginx.conf.example) as the site configuration
starting point. Its paths must match `[web]` in `config.ini`.
