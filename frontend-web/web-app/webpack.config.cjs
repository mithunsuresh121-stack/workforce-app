const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  mode: 'development',
  entry: './src/index.tsx',
  devtool: 'inline-source-map',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: {
          loader: 'ts-loader',
          options: {
            transpileOnly: true,
          },
        },
        exclude: /node_modules/,
      },
      {
        test: /\.css$/i,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      './App.js': path.resolve(__dirname, 'src/App.tsx'),
      './screens/LoginScreen.js': path.resolve(__dirname, 'src/screens/LoginScreen.tsx'),
      './screens/ProfileScreen.js': path.resolve(__dirname, 'src/screens/ProfileScreen.tsx'),
      './screens/DirectoryScreen.js': path.resolve(__dirname, 'src/screens/DirectoryScreen.tsx'),
      './screens/DashboardScreen.js': path.resolve(__dirname, 'src/screens/DashboardScreen.tsx'),
      './screens/TasksScreen.js': path.resolve(__dirname, 'src/screens/TasksScreen.tsx'),
      './screens/LeaveScreen.js': path.resolve(__dirname, 'src/screens/LeaveScreen.tsx'),
      '../api/userApi.js': path.resolve(__dirname, 'src/api/userApi.ts'),
      '../api/companyApi.js': path.resolve(__dirname, 'src/api/companyApi.ts'),
      '../api/taskApi.js': path.resolve(__dirname, 'src/api/taskApi.ts'),
      '../api/leaveApi.js': path.resolve(__dirname, 'src/api/leaveApi.ts'),
    },
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    compress: true,
    port: 3000,
    historyApiFallback: true,
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
};
