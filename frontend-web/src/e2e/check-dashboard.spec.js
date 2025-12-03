import { test, expect } from '@playwright/test';

test('check dashboard content', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('http://localhost:3000/dashboard');

  // Check if dashboard content is loaded
  await expect(page.locator('h3').filter({ hasText: 'Welcome back' })).toBeVisible();

  // Check for key dashboard elements
  await expect(page.locator('text=Profile')).toBeVisible();
  await expect(page.locator('text=Directory')).toBeVisible();
  await expect(page.locator('text=Tasks')).toBeVisible();
});
