import { test, expect } from '@playwright/test';

test('navigation to all pages after login', async ({ page }) => {
  // Go to login page
  await page.goto('http://localhost:3000/login');

  // Enter credentials
  await page.fill('input[type="email"]', 'demo@company.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Login")');

  // Wait for dashboard
  await page.waitForURL('http://localhost:3000/dashboard');

  // Check Dashboard
  await expect(page.locator('h3')).toContainText('Welcome back');

  // Navigate to Profile
  await page.click('a[href="/profile"]');
  await page.waitForURL('http://localhost:3000/profile');
  await expect(page.locator('h3')).toContainText('Profile');

  // Navigate to Directory
  await page.click('a[href="/directory"]');
  await page.waitForURL('http://localhost:3000/directory');
  await expect(page.locator('h3')).toContainText('Directory');

  // Navigate to Tasks
  await page.click('a[href="/tasks"]');
  await page.waitForURL('http://localhost:3000/tasks');
  await expect(page.locator('h3')).toContainText('Tasks');

  // Navigate to Leave
  await page.click('a[href="/leave"]');
  await page.waitForURL('http://localhost:3000/leave');
  await expect(page.locator('h3')).toContainText('Leave');

  // Back to Dashboard
  await page.click('a[href="/dashboard"]');
  await page.waitForURL('http://localhost:3000/dashboard');
  await expect(page.locator('h3')).toContainText('Welcome back');

  // Logout
  await page.click('button:has-text("Logout")');
  await page.waitForURL('http://localhost:3000/login');
  await expect(page.locator('input[type="email"]')).toBeVisible();
});
