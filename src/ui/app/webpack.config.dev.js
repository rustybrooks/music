const webpack = require('webpack');
const path = require('path');


module.exports = {
  devtool: 'eval-source-map',

  mode: 'development',
  devServer: {
    inline: true,
    port: '3000',
  },

  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        }
      },
    ],
  },

  entry: './src/index.js',
};
