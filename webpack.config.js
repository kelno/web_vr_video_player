const path = require("path");

module.exports = (env) => {
  const isDevelopment = env.development === true;

  const indexConfig = {
    entry: {
      index: "./src/index.js",
    },
    mode: isDevelopment ? "development" : "production",
    devtool: isDevelopment ? "source-map" : false,
    output: {
      filename: "[name].js",
      path: path.resolve(__dirname, "dist"),
      clean: true,
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
  };

  if (isDevelopment) {
    indexConfig.devServer = {
      host: "0.0.0.0",
      port: 8040,
      server: "https",
      static: [
        {
          directory: path.resolve(__dirname),
          publicPath: "/",
          // Webpack already watches imported source files. Watching the whole
          // repository as static content also watches .git/index, which can
          // create a perpetual browser-reload loop during normal Git work.
          // Reload manually after replacing files.json or index.html.
          watch: false,
        },
        {
          // Keep generated ../../download/... catalogue paths working without
          // exposing anything else on the D: drive.
          directory: path.resolve("D:/download"),
          publicPath: "/download",
          watch: false,
        },
      ],
      devMiddleware: {
        // index.html references dist/index.js directly, so preserve that
        // contract instead of requiring a separate development HTML file.
        writeToDisk: true,
      },
    };
  }

  return [indexConfig];
};
