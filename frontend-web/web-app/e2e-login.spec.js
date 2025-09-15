import { test, expect } from '@playwright/test';

test('login → dashboard → logout flow', async ({ page }) => {
  // Go to login page
  await page.goto('http://localhost:3000/login');

  // Check login page loads (look for email input)
  await expect(page.locator('input[type="email"]')).toBeVisible();

  // Enter credentials (replace with real valid test creds)
  await page.fill('input[type="email"]', 'test_employee@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Login")');

  // Verify dashboard loads
  await page.waitForURL('http://localhost:3000/dashboard');
  await expect(page.locator('h1')).toContainText('Dashboard');

  // Logout
  await page.click('button:has-text("Logout")');

  // Verify redirect to login
  await page.waitForURL('http://localhost:3000/login');
  await expect(page.locator('input[type="email"]')).toBeVisible();
});
