import { test, expect } from '@playwright/test';

test('login → dashboard → logout flow', async ({ page }) => {
  // Go to root page first (SPA routing)
  await page.goto('http://localhost:3000/');

  // Wait for the app to load and navigate to login
  await page.waitForSelector('input[type="email"]', { state: 'visible' });

  // Check login page loads (look for email input)
  await expect(page.locator('input[type="email"]')).toBeVisible();

  // Enter credentials (replace with real valid test creds)
  await page.fill('input[type="email"]', 'demo@company.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Login")', { force: true });

  // Wait a bit for the login to process
  await page.waitForTimeout(2000);

  // Check if there's an error message
  const errorElement = page.locator('text=Invalid credentials');
  if (await errorElement.isVisible()) {
    console.log('Login failed with invalid credentials');
    throw new Error('Login failed');
  }

  // Check if we're still on login page
  if (page.url().includes('/login')) {
    console.log('Still on login page, login may have failed');
    throw new Error('Still on login page');
  }

  // Verify dashboard loads
  await page.waitForURL('http://localhost:3000/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' }).first()).toBeVisible();

  // Test navigation to Profile
  await page.click('text=Profile');
  await page.waitForURL('http://localhost:3000/profile');
  await expect(page.locator('h3:has-text("Profile")')).toBeVisible();

  // Test navigation to Directory
  await page.click('text=Directory');
  await page.waitForURL('http://localhost:3000/directory');
  await expect(page.locator('h3:has-text("Directory")')).toBeVisible();

  // Test navigation to Tasks
  await page.click('text=Tasks');
  await page.waitForURL('http://localhost:3000/tasks');
  await expect(page.locator('h3:has-text("Tasks")')).toBeVisible();

  // Test navigation to Leave
  await page.click('text=Leave');
  await page.waitForURL('http://localhost:3000/leave');
  await expect(page.locator('h3:has-text("Leave")')).toBeVisible();

  // Back to Dashboard
  await page.click('text=Dashboard');
  await page.waitForURL('http://localhost:3000/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' }).first()).toBeVisible();

  // Logout
  await page.click('button:has-text("Logout")');

  // Verify redirect to login
  await page.waitForURL('http://localhost:3000/login');
  await expect(page.locator('input[type="email"]')).toBeVisible();
});
