const webpack = require('webpack');
const config = {
        devtool: 'eval-source-map',
 entry: __dirname + '/static/js/index.jsx',
 output:{
  path: __dirname + '/dist',
  filename: 'bundle.js',
},
 resolve: {
  extensions: ['.js','.jsx','.css']
 },
 module: {
  rules: [
  {
   test: /\.jsx?/,
   loader: 'babel-loader',
   exclude: /node_modules/
   },
   {
         test: /\.css$/,
         loader: 'style-loader!css-loader?modules'
  }]
 }
};
module.exports = config;
