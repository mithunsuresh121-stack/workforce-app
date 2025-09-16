import { test, expect } from '@playwright/test';

test('Check all routes for visibility', async ({ page }) => {
  // Check login page
  await page.goto('http://localhost:3000/login');
  await expect(page.locator('input[type="email"]')).toBeVisible();
  console.log('✅ Login screen visible');

  // Check dashboard (will show login if not authenticated)
  await page.goto('http://localhost:3000/dashboard');
  await expect(page.locator('input[type="email"]')).toBeVisible();
  console.log('✅ Dashboard route shows login (protected)');

  // Check profile route
  await page.goto('http://localhost:3000/profile');
  await expect(page.locator('input[type="email"]')).toBeVisible();
  console.log('✅ Profile route shows login (protected)');

  // Check directory route
  await page.goto('http://localhost:3000/directory');
  await expect(page.locator('input[type="email"]')).toBeVisible();
  console.log('✅ Directory route shows login (protected)');

  // Check tasks route
  await page.goto('http://localhost:3000/tasks');
  await expect(page.locator('input[type="email"]')).toBeVisible();
  console.log('✅ Tasks route shows login (protected)');

  // Check leave route
  await page.goto('http://localhost:3000/leave');
  await expect(page.locator('input[type="email"]')).toBeVisible();
  console.log('✅ Leave route shows login (protected)');

  console.log('📋 Manual QA: Please confirm UI is styled, responsive, and navigation works correctly.');
});
