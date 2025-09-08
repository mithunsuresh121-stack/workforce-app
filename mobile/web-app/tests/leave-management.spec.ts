import { test, expect } from '@playwright/test';

test.describe('Leave Management Tests', () => {
  test.beforeEach(async ({ page }) => {
    console.log('Starting Leave Management test setup...');
    // Navigate to the login page
    await page.goto('http://localhost:3000/login');
    console.log('Navigated to login page');
  });

  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status !== testInfo.expectedStatus) {
      await page.screenshot({ path: `test-results/${testInfo.title}.png`, fullPage: true });
      console.error(`❌ Test failed: ${testInfo.title}`);
    }
  });

  test('SuperAdmin should be able to create, view, and approve leave requests', async ({ page }) => {
    console.log('Testing SuperAdmin leave management functionality...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    console.log('Logged in as SuperAdmin');

    // Wait for navigation to be visible after login
    await page.getByRole('navigation').waitFor({ state: 'visible' });

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await expect(page).toHaveURL(/.*leave/);
    console.log('Navigated to Leave Management');

    // Wait for leave management page to load
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Test creating a new leave request
    await page.click('[data-cy="create-leave-button"]');
    console.log('Clicked create leave button');

    // Fill out the leave request form
    await page.selectOption('[data-cy="leave-type-select"]', 'Vacation');
    await page.fill('[data-cy="start-date-input"]', '2024-02-01');
    await page.fill('[data-cy="end-date-input"]', '2024-02-05');
    await page.fill('[data-cy="leave-reason-textarea"]', 'Family vacation request');

    // Submit the form
    await page.click('[data-cy="submit-leave-button"]');
    console.log('Submitted leave request');

    // Verify leave appears in the list
    await expect(page.locator('[data-cy="leave-list-item"]').first()).toBeVisible();
    await expect(page.locator('[data-cy="leave-status"]').first()).toContainText('Pending');

    // Test approving the leave request
    await page.click('[data-cy="approve-leave-button"]');
    console.log('Approved leave request');

    // Verify status changed to Approved
    await expect(page.locator('[data-cy="leave-status"]').first()).toContainText('Approved');

    console.log('Leave creation and approval test completed successfully');
  });

  test('Manager should be able to view and manage leave requests in their company', async ({ page }) => {
    console.log('Testing Manager leave management functionality...');

    // Login as Manager
    await page.fill('input[type="email"]', 'admin@techcorp.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    console.log('Logged in as Manager');

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await expect(page).toHaveURL(/.*leave/);

    // Wait for leave management page to load
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Verify leave list is visible
    await expect(page.locator('[data-cy="leave-list"]')).toBeVisible();

    // Test viewing leave details
    const firstLeaveItem = page.locator('[data-cy="leave-list-item"]').first();
    if (await firstLeaveItem.isVisible()) {
      await firstLeaveItem.click();
      await expect(page.locator('[data-cy="leave-details-modal"]')).toBeVisible();
      console.log('Leave details modal opened successfully');
    }

    // Test rejecting a leave request (if available)
    const rejectButton = page.locator('[data-cy="reject-leave-button"]');
    if (await rejectButton.isVisible()) {
      await rejectButton.click();
      await expect(page.locator('[data-cy="leave-status"]').first()).toContainText('Rejected');
      console.log('Leave rejection test completed');
    }

    console.log('Manager leave management test completed successfully');
  });

  test('Employee should be able to create leave requests but not approve them', async ({ page }) => {
    console.log('Testing Employee leave management functionality...');

    // Login as Employee
    await page.fill('input[type="email"]', 'test@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    console.log('Logged in as Employee');

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await expect(page).toHaveURL(/.*leave/);

    // Wait for leave management page to load
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Verify create leave button is visible
    await expect(page.locator('[data-cy="create-leave-button"]')).toBeVisible();

    // Test creating a leave request
    await page.click('[data-cy="create-leave-button"]');

    // Fill out the form
    await page.selectOption('[data-cy="leave-type-select"]', 'Sick Leave');
    await page.fill('[data-cy="start-date-input"]', '2024-02-10');
    await page.fill('[data-cy="end-date-input"]', '2024-02-10');
    await page.fill('[data-cy="leave-reason-textarea"]', 'Feeling unwell');

    // Submit the form
    await page.click('[data-cy="submit-leave-button"]');

    // Verify leave appears in the list
    await expect(page.locator('[data-cy="leave-list-item"]')).toBeVisible();

    // Verify that approval/rejection buttons are NOT visible for employees
    await expect(page.locator('[data-cy="approve-leave-button"]')).not.toBeVisible();
    await expect(page.locator('[data-cy="reject-leave-button"]')).not.toBeVisible();

    console.log('Employee leave creation test completed successfully');
  });

  test('Leave form validation should work correctly', async ({ page }) => {
    console.log('Testing leave form validation...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Click create leave button
    await page.click('[data-cy="create-leave-button"]');

    // Test submitting empty form
    await page.click('[data-cy="submit-leave-button"]');

    // Check for validation errors
    await expect(page.locator('[data-cy="validation-error"]')).toBeVisible();

    // Test invalid date range (end before start)
    await page.selectOption('[data-cy="leave-type-select"]', 'Vacation');
    await page.fill('[data-cy="start-date-input"]', '2024-02-10');
    await page.fill('[data-cy="end-date-input"]', '2024-02-05'); // End before start

    await page.click('[data-cy="submit-leave-button"]');

    // Should show validation error for invalid date range
    await expect(page.locator('[data-cy="date-validation-error"]')).toBeVisible();

    console.log('Leave form validation test completed successfully');
  });

  test('Leave list filtering and search should work', async ({ page }) => {
    console.log('Testing leave list filtering and search...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Test status filter
    await page.selectOption('[data-cy="status-filter"]', 'Pending');
    await expect(page.locator('[data-cy="leave-list-item"]')).toBeVisible();

    // Test leave type filter
    await page.selectOption('[data-cy="type-filter"]', 'Vacation');
    await expect(page.locator('[data-cy="leave-list"]')).toBeVisible();

    // Test search functionality
    await page.fill('[data-cy="search-input"]', 'vacation');
    await expect(page.locator('[data-cy="leave-list"]')).toBeVisible();

    console.log('Leave filtering and search test completed successfully');
  });

  test('Leave management should handle edge cases gracefully', async ({ page }) => {
    console.log('Testing leave management edge cases...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Test creating leave for past date
    await page.click('[data-cy="create-leave-button"]');
    await page.selectOption('[data-cy="leave-type-select"]', 'Personal Leave');
    await page.fill('[data-cy="start-date-input"]', '2023-01-01'); // Past date
    await page.fill('[data-cy="end-date-input"]', '2023-01-02');
    await page.fill('[data-cy="leave-reason-textarea"]', 'Past leave test');

    await page.click('[data-cy="submit-leave-button"]');

    // Should either allow or show appropriate message
    await expect(page.locator('[data-cy="leave-list"]')).toBeVisible();

    // Test very long leave request
    await page.click('[data-cy="create-leave-button"]');
    await page.selectOption('[data-cy="leave-type-select"]', 'Extended Leave');
    await page.fill('[data-cy="start-date-input"]', '2024-03-01');
    await page.fill('[data-cy="end-date-input"]', '2024-05-01'); // 2 months
    await page.fill('[data-cy="leave-reason-textarea"]', 'Extended leave test');

    await page.click('[data-cy="submit-leave-button"]');

    // Should handle long leave requests appropriately
    await expect(page.locator('[data-cy="leave-list"]')).toBeVisible();

    console.log('Leave management edge cases test completed successfully');
  });

  test('Leave management should be responsive and accessible', async ({ page }) => {
    console.log('Testing leave management responsiveness and accessibility...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Leave Management
    await page.click('[data-cy="nav-leave-management"]');
    await page.waitForSelector('[data-cy="leave-management-container"]');

    // Check that all interactive elements have proper data-cy attributes
    await expect(page.locator('[data-cy="create-leave-button"]')).toBeVisible();
    await expect(page.locator('[data-cy="leave-list"]')).toBeVisible();

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-cy="create-leave-button"]')).toBeFocused();

    // Test form accessibility
    await page.click('[data-cy="create-leave-button"]');
    await expect(page.locator('[data-cy="leave-form"]')).toBeVisible();

    // Check form elements have labels
    await expect(page.locator('label[for="leave-type"]')).toBeVisible();
    await expect(page.locator('label[for="start-date"]')).toBeVisible();
    await expect(page.locator('label[for="end-date"]')).toBeVisible();

    console.log('Leave management accessibility test completed successfully');
  });
});
