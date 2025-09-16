import { test, expect } from '@playwright/test';

test.describe('Comprehensive Workforce App Testing', () => {
  test('login → dashboard → all routes navigation flow', async ({ page }) => {
    // Go to login page
    await page.goto('http://localhost:3000/login');

    // Check login page loads with all elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button:has-text("Login")')).toBeVisible();
    await expect(page.locator('text=Workforce App')).toBeVisible();

    // Enter credentials (using demo user from backend logs)
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');

    // Verify dashboard loads
    await page.waitForURL('http://localhost:3000/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('text=Welcome back')).toBeVisible();

    // Test navigation to Profile
    await page.click('a[href="/profile"]');
    await page.waitForURL('http://localhost:3000/profile');
    await expect(page.locator('text=Profile')).toBeVisible();

    // Test navigation to Directory
    await page.click('a[href="/directory"]');
    await page.waitForURL('http://localhost:3000/directory');
    await expect(page.locator('text=Directory')).toBeVisible();

    // Test navigation to Tasks
    await page.click('a[href="/tasks"]');
    await page.waitForURL('http://localhost:3000/tasks');
    await expect(page.locator('text=Tasks')).toBeVisible();

    // Test navigation to Leave
    await page.click('a[href="/leave"]');
    await page.waitForURL('http://localhost:3000/leave');
    await expect(page.locator('text=Leave')).toBeVisible();

    // Test navigation back to Dashboard
    await page.click('a[href="/dashboard"]');
    await page.waitForURL('http://localhost:3000/dashboard');
    await expect(page.locator('text=Welcome back')).toBeVisible();

    // Logout
    await page.click('button:has-text("Logout")');

    // Verify redirect to login
    await page.waitForURL('http://localhost:3000/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('protected routes redirect to login when not authenticated', async ({ page }) => {
    // Try to access dashboard without login
    await page.goto('http://localhost:3000/dashboard');
    await page.waitForURL('http://localhost:3000/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Try to access profile without login
    await page.goto('http://localhost:3000/profile');
    await page.waitForURL('http://localhost:3000/login');

    // Try to access directory without login
    await page.goto('http://localhost:3000/directory');
    await page.waitForURL('http://localhost:3000/login');

    // Try to access tasks without login
    await page.goto('http://localhost:3000/tasks');
    await page.waitForURL('http://localhost:3000/login');

    // Try to access leave without login
    await page.goto('http://localhost:3000/leave');
    await page.waitForURL('http://localhost:3000/login');
  });

  test('UI responsiveness and styling checks', async ({ page }) => {
    // Login first
    await page.goto('http://localhost:3000/login');
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('http://localhost:3000/dashboard');

    // Check dashboard layout and components
    await expect(page.locator('.grid')).toBeVisible(); // KPI cards grid
    await expect(page.locator('canvas')).toHaveCount(2); // Two charts

    // Check sidebar navigation
    await expect(page.locator('nav')).toBeVisible();

    // Check footer
    await expect(page.locator('footer')).toBeVisible();

    // Test mobile responsiveness (set viewport to mobile size)
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.grid')).toBeVisible(); // Should still be visible on mobile
  });
});
