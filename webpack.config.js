const path = require("path");

module.exports = {
  entry: {
    index: "./src/index.js",
    jsonLoader: "./src/jsonLoader.js",
  },
  mode: "production",
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
