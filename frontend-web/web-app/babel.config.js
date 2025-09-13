const isDevelopment = process.env.NODE_ENV === 'development';

module.exports = {
  presets: [
    '@babel/preset-env',
    '@babel/preset-react'
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    ...(isDevelopment ? ['react-refresh/babel'] : [])
  ]
};
