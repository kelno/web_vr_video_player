const path = require("path");
const fs = require("fs");
const HtmlWebpackPlugin = require("html-webpack-plugin");

const PROJECT_ROOT = __dirname;
const DIST_DIRECTORY = path.resolve(PROJECT_ROOT, "dist");

function readVideosConfig() {
  const configPath = path.resolve(PROJECT_ROOT, "config.ini");
  if (!fs.existsSync(configPath)) {
    return {};
  }

  const values = {};
  let inVideosSection = false;
  for (const rawLine of fs.readFileSync(configPath, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith(";") || line.startsWith("#")) {
      continue;
    }
    if (line.startsWith("[") && line.endsWith("]")) {
      inVideosSection = line === "[videos]";
      continue;
    }
    if (inVideosSection) {
      const separator = line.indexOf("=");
      if (separator !== -1) {
        values[line.slice(0, separator).trim()] = line
          .slice(separator + 1)
          .trim();
      }
    }
  }
  return values;
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
  const videosConfig = readVideosConfig();
  const sitePrefix = siteUrlPrefix(videosConfig.site_url_prefix);
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
      videosConfig.videos_path,
      joinUrlPrefix(sitePrefix, videosConfig.videos_url_prefix || "/media"),
    );
    addMediaMount(
      videosConfig.thumbnails_path,
      joinUrlPrefix(
        sitePrefix,
        videosConfig.thumbnails_url_prefix || "/thumbnails",
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
