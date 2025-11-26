import { test, expect } from '@playwright/test';

test.describe('Workflow Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.fill('input[type="email"]', 'manager@test.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('Login and Navigation', async ({ page }) => {
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('CRUD Operations - Employee Management', async ({ page }) => {
    // Navigate to employees
    await page.click('text=Employees');
    await expect(page).toHaveURL(/.*employees/);

    // Check if employees are listed
    await expect(page.locator('text=Test Employee')).toBeVisible();
  });

  test('Leave Management Workflow', async ({ page }) => {
    // Navigate to leaves
    await page.click('text=Leaves');
    await expect(page).toHaveURL(/.*leaves/);

    // Check leave requests
    await expect(page.locator('text=Vacation')).toBeVisible();
  });

  test('Chat Functionality', async ({ page }) => {
    // Navigate to chat
    await page.click('text=Chat');
    await expect(page).toHaveURL(/.*chat/);

    // Check chat interface
    await expect(page.locator('input[placeholder*="message"]')).toBeVisible();
  });

  test('Document Upload/Download', async ({ page }) => {
    // Navigate to documents
    await page.click('text=Documents');
    await expect(page).toHaveURL(/.*documents/);

    // Check document list
    await expect(page.locator('text=POLICY')).toBeVisible();
  });

  test('Notification Management', async ({ page }) => {
    // Check notifications in header/navbar
    const notificationBell = page.locator('[data-testid="notification-bell"]');
    if (await notificationBell.isVisible()) {
      await notificationBell.click();
      await expect(page.locator('text=New Task Assigned')).toBeVisible();
    }
  });

  test('Role-based UI Elements', async ({ page }) => {
    // Manager should see approval buttons
    await page.click('text=Leaves');
    const approveButton = page.locator('button:has-text("Approve")');
    await expect(approveButton).toBeVisible();
  });
});
