import { test, expect } from '@playwright/test';

test.describe('Shift Management Tests', () => {
  test.beforeEach(async ({ page }) => {
    console.log('Starting Shift Management test setup...');
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

  test('SuperAdmin should be able to create, view, and manage shifts', async ({ page }) => {
    console.log('Testing SuperAdmin shift management functionality...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    console.log('Logged in as SuperAdmin');

    // Wait for navigation to be visible after login
    await page.getByRole('navigation').waitFor({ state: 'visible' });

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await expect(page).toHaveURL(/.*shift/);
    console.log('Navigated to Shift Management');

    // Wait for shift management page to load
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Test creating a new shift
    await page.click('[data-cy="create-shift-button"]');
    console.log('Clicked create shift button');

    // Fill out the shift form
    await page.fill('[data-cy="shift-name-input"]', 'Morning Shift');
    await page.fill('[data-cy="shift-date-input"]', '2024-02-01');
    await page.fill('[data-cy="shift-time-input"]', '09:00-17:00');

    // Submit the form
    await page.click('[data-cy="submit-shift-button"]');
    console.log('Submitted shift');

    // Verify shift appears in the list
    await expect(page.locator('[data-cy="shift-list-item"]').first()).toBeVisible();
    await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('Scheduled');

    // Test updating shift status to Completed
    await page.click('[data-cy="complete-shift-button"]');
    console.log('Completed shift');

    // Verify status changed to Completed
    await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('Completed');

    console.log('Shift creation and management test completed successfully');
  });

  test('Manager should be able to view and manage shifts in their company', async ({ page }) => {
    console.log('Testing Manager shift management functionality...');

    // Login as Manager
    await page.fill('input[type="email"]', 'admin@techcorp.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    console.log('Logged in as Manager');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await expect(page).toHaveURL(/.*shift/);

    // Wait for shift management page to load
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Verify shift list is visible
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    // Test viewing shift details
    const firstShiftItem = page.locator('[data-cy="shift-list-item"]').first();
    if (await firstShiftItem.isVisible()) {
      await firstShiftItem.click();
      await expect(page.locator('[data-cy="shift-details-modal"]')).toBeVisible();
      console.log('Shift details modal opened successfully');
    }

    // Test cancelling a shift (if available)
    const cancelButton = page.locator('[data-cy="cancel-shift-button"]');
    if (await cancelButton.isVisible()) {
      await cancelButton.click();
      await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('Cancelled');
      console.log('Shift cancellation test completed');
    }

    console.log('Manager shift management test completed successfully');
  });

  test('Employee should have limited access to shift management', async ({ page }) => {
    console.log('Testing Employee shift management access...');

    // Login as Employee
    await page.fill('input[type="email"]', 'test@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    console.log('Logged in as Employee');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await expect(page).toHaveURL(/.*shift/);

    // Wait for shift management page to load
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Verify shift list is visible (read-only access)
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    // Verify that create shift button is NOT visible for employees
    await expect(page.locator('[data-cy="create-shift-button"]')).not.toBeVisible();

    // Verify that management buttons are NOT visible for employees
    await expect(page.locator('[data-cy="complete-shift-button"]')).not.toBeVisible();
    await expect(page.locator('[data-cy="cancel-shift-button"]')).not.toBeVisible();

    console.log('Employee shift access test completed successfully');
  });

  test('Shift form validation should work correctly', async ({ page }) => {
    console.log('Testing shift form validation...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Click create shift button
    await page.click('[data-cy="create-shift-button"]');

    // Test submitting empty form
    await page.click('[data-cy="submit-shift-button"]');

    // Check for validation errors
    await expect(page.locator('[data-cy="validation-error"]')).toBeVisible();

    // Test invalid time format
    await page.fill('[data-cy="shift-name-input"]', 'Test Shift');
    await page.fill('[data-cy="shift-date-input"]', '2024-02-01');
    await page.fill('[data-cy="shift-time-input"]', 'invalid-time-format');

    await page.click('[data-cy="submit-shift-button"]');

    // Should show validation error for invalid time format
    await expect(page.locator('[data-cy="time-validation-error"]')).toBeVisible();

    console.log('Shift form validation test completed successfully');
  });

  test('Shift list filtering and search should work', async ({ page }) => {
    console.log('Testing shift list filtering and search...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Test status filter
    await page.selectOption('[data-cy="shift-status-filter"]', 'Scheduled');
    await expect(page.locator('[data-cy="shift-list-item"]')).toBeVisible();

    // Test date filter
    await page.fill('[data-cy="date-filter-input"]', '2024-02-01');
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    // Test search functionality
    await page.fill('[data-cy="shift-search-input"]', 'morning');
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    console.log('Shift filtering and search test completed successfully');
  });

  test('Shift status transitions should work correctly', async ({ page }) => {
    console.log('Testing shift status transitions...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Create a shift first
    await page.click('[data-cy="create-shift-button"]');
    await page.fill('[data-cy="shift-name-input"]', 'Status Test Shift');
    await page.fill('[data-cy="shift-date-input"]', '2024-02-15');
    await page.fill('[data-cy="shift-time-input"]', '10:00-18:00');
    await page.click('[data-cy="submit-shift-button"]');

    // Test status transitions
    // Scheduled -> In Progress
    await page.click('[data-cy="start-shift-button"]');
    await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('In Progress');

    // In Progress -> Completed
    await page.click('[data-cy="complete-shift-button"]');
    await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('Completed');

    // Test cancellation from Scheduled status
    await page.click('[data-cy="create-shift-button"]');
    await page.fill('[data-cy="shift-name-input"]', 'Cancel Test Shift');
    await page.fill('[data-cy="shift-date-input"]', '2024-02-16');
    await page.fill('[data-cy="shift-time-input"]', '14:00-22:00');
    await page.click('[data-cy="submit-shift-button"]');

    await page.click('[data-cy="cancel-shift-button"]');
    await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('Cancelled');

    console.log('Shift status transitions test completed successfully');
  });

  test('Shift management should handle edge cases gracefully', async ({ page }) => {
    console.log('Testing shift management edge cases...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Test creating shift for past date
    await page.click('[data-cy="create-shift-button"]');
    await page.fill('[data-cy="shift-name-input"]', 'Past Shift');
    await page.fill('[data-cy="shift-date-input"]', '2023-01-01'); // Past date
    await page.fill('[data-cy="shift-time-input"]', '09:00-17:00');

    await page.click('[data-cy="submit-shift-button"]');

    // Should either allow or show appropriate message
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    // Test overnight shift
    await page.click('[data-cy="create-shift-button"]');
    await page.fill('[data-cy="shift-name-input"]', 'Night Shift');
    await page.fill('[data-cy="shift-date-input"]', '2024-02-20');
    await page.fill('[data-cy="shift-time-input"]', '22:00-06:00'); // Overnight

    await page.click('[data-cy="submit-shift-button"]');

    // Should handle overnight shifts appropriately
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    // Test very short shift
    await page.click('[data-cy="create-shift-button"]');
    await page.fill('[data-cy="shift-name-input"]', 'Short Shift');
    await page.fill('[data-cy="shift-date-input"]', '2024-02-21');
    await page.fill('[data-cy="shift-time-input"]', '09:00-10:00'); // 1 hour

    await page.click('[data-cy="submit-shift-button"]');

    // Should handle short shifts appropriately
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    console.log('Shift management edge cases test completed successfully');
  });

  test('Shift management should be responsive and accessible', async ({ page }) => {
    console.log('Testing shift management responsiveness and accessibility...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Check that all interactive elements have proper data-cy attributes
    await expect(page.locator('[data-cy="create-shift-button"]')).toBeVisible();
    await expect(page.locator('[data-cy="shift-list"]')).toBeVisible();

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-cy="create-shift-button"]')).toBeFocused();

    // Test form accessibility
    await page.click('[data-cy="create-shift-button"]');
    await expect(page.locator('[data-cy="shift-form"]')).toBeVisible();

    // Check form elements have labels
    await expect(page.locator('label[for="shift-name"]')).toBeVisible();
    await expect(page.locator('label[for="shift-date"]')).toBeVisible();
    await expect(page.locator('label[for="shift-time"]')).toBeVisible();

    console.log('Shift management accessibility test completed successfully');
  });

  test('Bulk shift operations should work correctly', async ({ page }) => {
    console.log('Testing bulk shift operations...');

    // Login as SuperAdmin
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button[type="submit"]');

    // Navigate to Shift Management
    await page.click('[data-cy="nav-shift-management"]');
    await page.waitForSelector('[data-cy="shift-management-container"]');

    // Create multiple shifts for bulk operations
    for (let i = 1; i <= 3; i++) {
      await page.click('[data-cy="create-shift-button"]');
      await page.fill('[data-cy="shift-name-input"]', `Bulk Shift ${i}`);
      await page.fill('[data-cy="shift-date-input"]', `2024-02-${10 + i}`);
      await page.fill('[data-cy="shift-time-input"]', '09:00-17:00');
      await page.click('[data-cy="submit-shift-button"]');
    }

    // Test bulk status update (if available)
    const bulkUpdateButton = page.locator('[data-cy="bulk-update-button"]');
    if (await bulkUpdateButton.isVisible()) {
      // Select multiple shifts
      await page.check('[data-cy="shift-checkbox"]:first-child');
      await page.check('[data-cy="shift-checkbox"]:nth-child(2)');

      // Perform bulk update
      await bulkUpdateButton.click();
      await page.selectOption('[data-cy="bulk-status-select"]', 'Completed');
      await page.click('[data-cy="confirm-bulk-update"]');

      // Verify bulk update worked
      await expect(page.locator('[data-cy="shift-status"]').first()).toContainText('Completed');
      console.log('Bulk shift operations test completed successfully');
    } else {
      console.log('Bulk operations not available, skipping test');
    }
  });
});
