module.exports = {
  test: {
    globals: true,
    environment: "jsdom",
    include: ["src/**/__tests__/**/*.test.{js,jsx,ts,tsx}"],
    setupFiles: "./src/setupTests.js",
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/setupTests.js']
    }
  }
}
