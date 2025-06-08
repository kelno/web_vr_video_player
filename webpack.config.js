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
  };

  const jsonLoaderConfig = {
    entry: {
      jsonLoader: "./src/jsonLoader.js",
    },
    mode: isDevelopment ? "development" : "production",
    // devtool: isDevelopment ? "source-map" : false,
    output: {
      filename: "[name].js",
      path: path.resolve(__dirname, "dist"),
      library: {
        type: "module",
      },
    },
    experiments: {
      outputModule: true,
    },
    module: {
      rules: [
        {
          test: /\.(png|svg|jpg|gif)$/,
          use: ["file-loader"],
        },
      ],
    },
  };

  return [indexConfig, jsonLoaderConfig];
};
