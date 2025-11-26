module.exports = {
  presets: ['react-app'],
  overrides: [
    {
      test: ['./src/__tests__'],
      presets: ['@babel/preset-env', '@babel/preset-react'],
    },
  ],
};
