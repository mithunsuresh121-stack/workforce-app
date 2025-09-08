import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  retries: 1,
  reporter: [['list'], ['html']],
  use: {
    baseURL: 'http://localhost:3001',
    headless: false,
  },
  projects: [
    {
      name: 'Brave',
      use: {
        channel: 'chrome', // Brave uses Chromium base
        launchOptions: {
          executablePath: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
        }
      },
    },
  ],
});
