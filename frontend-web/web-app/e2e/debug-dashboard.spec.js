import { test, expect } from '@playwright/test';

test('debug dashboard API calls', async ({ page }) => {
  // Listen for all API requests
  const requests = [];
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      requests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers()
      });
    }
  });

  const responses = [];
  page.on('response', response => {
    if (response.url().includes('/api/')) {
      responses.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText()
      });
    }
  });

  // Go to login page
  await page.goto('http://localhost:3000/login');

  // Enter credentials
  await page.fill('input[type="email"]', 'demo@company.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Login")');

  // Wait for dashboard
  await page.waitForURL('http://localhost:3000/dashboard');

  // Wait for potential API calls
  await page.waitForTimeout(5000);

  console.log('API Requests made:');
  requests.forEach((req, i) => console.log(`${i+1}. ${req.method} ${req.url}`));

  console.log('API Responses received:');
  responses.forEach((res, i) => console.log(`${i+1}. ${res.status} ${res.url}`));

  // Check localStorage for token
  const token = await page.evaluate(() => localStorage.getItem('token'));
  console.log('Token in localStorage:', token ? 'Present' : 'Not found');
});
