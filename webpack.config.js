const path = require('path')

const webpack = require('webpack')

module.exports = {
  devtool: 'source-map',
  entry: {
    vendor: [
    'bulma',
    'chart.js',
    'chartjs-plugin-dragdata',
    'jquery',
    'json5',
    ],
  },

  output: {
    filename: '[name].[chunkhash].js',
    path: path.resolve('./dist/'),
    library: '[name]_lib',
  },
  plugins: [
    new webpack.DllPlugin({
      path: 'dist/[name]-manifest.json',
      name: '[name]_lib',
    }),
  ],
  module: {
      rules: [
        { test: /\.css$/, use: [ 'style-loader', 'css-loader' ] }
      ],
    }
}

