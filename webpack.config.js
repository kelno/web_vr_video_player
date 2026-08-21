const path = require("path");
const fs = require("fs");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");

const PROJECT_ROOT = __dirname;
const DIST_DIRECTORY = path.resolve(PROJECT_ROOT, "dist");

function parseIni(contents) {
  const sections = {};
  let currentSection = null;
  for (const rawLine of contents.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith(";") || line.startsWith("#")) {
      continue;
    }
    if (line.startsWith("[") && line.endsWith("]")) {
      currentSection = line.slice(1, -1).trim();
      sections[currentSection] ??= {};
      continue;
    }
    if (currentSection) {
      const separator = line.indexOf("=");
      if (separator !== -1) {
        sections[currentSection][line.slice(0, separator).trim()] = line
          .slice(separator + 1)
          .trim();
      }
    }
  }
  return sections;
}

function readConfig() {
  const configPath = path.resolve(PROJECT_ROOT, "config.ini");
  return fs.existsSync(configPath)
    ? parseIni(fs.readFileSync(configPath, "utf8"))
    : {};
}

function playerConfig(config) {
  const configuredZoom = Number(config.player?.default_sbs_zoom ?? 100);
  return {
    // A bad local setting should not prevent the player from loading. Zero is
    // useful for users who prefer to start with the screen at its base size.
    defaultSbsZoom:
      Number.isFinite(configuredZoom) && configuredZoom >= 0 && configuredZoom <= 180
        ? configuredZoom
        : 100,
  };
}

function urlPrefix(value, fallback) {
  const prefix = value || fallback;
  return `/${prefix.replace(/^\/+|\/+$/g, "")}`;
}

function siteUrlPrefix(value) {
  const prefix = urlPrefix(value, "/");
  return prefix === "/" ? "" : prefix;
}

function joinUrlPrefix(sitePrefix, routePrefix) {
  return `${sitePrefix}${urlPrefix(routePrefix, "/")}`;
}

module.exports = (env) => {
  const isDevelopment = env.development === true;
  const config = readConfig();
  const libraryConfig = config.library ?? {};
  const webConfig = config.web ?? {};
  const sitePrefix = siteUrlPrefix(webConfig.site_url_prefix);
  const assetPublicPath = sitePrefix ? `${sitePrefix}/` : "/";

  const indexConfig = {
    entry: {
      index: "./src/index.js",
    },
    mode: isDevelopment ? "development" : "production",
    devtool: isDevelopment ? "source-map" : false,
    output: {
      filename: "[name].js",
      path: DIST_DIRECTORY,
      // Assets must remain beneath the configured site path when Nginx serves
      // the player from a subpath such as /vr-player/.
      publicPath: assetPublicPath,
      // Production releases are rebuilt from scratch. Development must retain
      // dist/files.json, which is generated independently from source code.
      clean: !isDevelopment,
    },
    module: {
      rules: [
        {
          test: /\.(png|svg|jpg|gif)$/,
          use: ["file-loader"],
        },
      ],
    },
    resolve: {
      alias: {
        three: path.resolve(__dirname, "node_modules/three"),
      },
    },
    plugins: [
      // config.ini is local deployment configuration. Embed only browser-safe
      // player preferences; filesystem paths remain available to Webpack only.
      new webpack.DefinePlugin({
        __PLAYER_CONFIG__: JSON.stringify(playerConfig(config)),
      }),
      new HtmlWebpackPlugin({
        template: "./index.html",
        filename: "index.html",
        favicon: "./favicon.ico",
        inject: "body",
        scriptLoading: "defer",
      }),
    ],
  };

  if (isDevelopment) {
    const staticDirectories = [
      {
        // The development server uses the same self-contained release layout
        // as production. The catalogue generator writes dist/files.json.
        directory: DIST_DIRECTORY,
        publicPath: assetPublicPath,
        watch: false,
      },
    ];
    const addMediaMount = (directory, prefix) => {
      if (directory) {
        staticDirectories.push({
          directory: path.resolve(directory),
          publicPath: prefix,
          watch: false,
        });
      }
    };
    addMediaMount(
      libraryConfig.videos_path,
      joinUrlPrefix(sitePrefix, webConfig.videos_url_prefix || "/media"),
    );
    addMediaMount(
      libraryConfig.thumbnails_path,
      joinUrlPrefix(
        sitePrefix,
        webConfig.thumbnails_url_prefix || "/thumbnails",
      ),
    );

    indexConfig.devServer = {
      host: "0.0.0.0",
      port: 8040,
      server: "https",
      static: staticDirectories,
      devMiddleware: {
        // Static files (including files.json) are read from dist, so write the
        // Webpack output there as well as serving it from memory.
        writeToDisk: true,
        publicPath: assetPublicPath,
      },
    };

    if (sitePrefix) {
      indexConfig.devServer.setupMiddlewares = (middlewares, devServer) => {
        // The terminal prints the server origin, but the player is intentionally
        // hosted below site_url_prefix. Make opening that origin convenient.
        devServer.app.use((request, response, next) => {
          // Express considers /vr-player and /vr-player/ equivalent when
          // matching a route. Check the exact request path to avoid redirecting
          // the destination back to itself.
          if (request.path === "/" || request.path === sitePrefix) {
            response.redirect(302, assetPublicPath);
            return;
          }
          next();
        });
        return middlewares;
      };
    }
  }

  return [indexConfig];
};

// Export the small configuration pieces so their edge cases can be checked
// without creating a Webpack compiler.
module.exports.parseIni = parseIni;
module.exports.playerConfig = playerConfig;
