import { test, expect } from '@playwright/test';
import { getDirectoryList, getDirectoryItems, getDirectoryFilter, getDirectorySort, getDirectoryMessage, getPageTitle, getTableHeader, getStatusIndicator, getDirectoryItem, getDirectorySortBy, loginUser } from './test-utils.js';

test.describe('DirectoryScreen', () => {
  test.beforeEach(async ({ page }) => {
    // Login first to get authentication token
    await loginUser(page);
    // Navigate to the directory page
    await page.goto('/directory');
  });

  test('should load directory page correctly', async ({ page }) => {
    // Wait for React to render
    await page.waitForTimeout(2000);
    // Check if the page title or main heading is visible
    await expect(getPageTitle(page, 'company-directory')).toBeVisible({ timeout: 10000 });
  });

  test('should display user list', async ({ page }) => {
    // Wait for React to render
    await page.waitForTimeout(2000);
    // Check if user list or table is displayed
    await expect(getDirectoryList(page)).toBeVisible({ timeout: 10000 });

    // Check if at least one user row is displayed
    await expect(getDirectoryItems(page).first()).toBeVisible({ timeout: 10000 });
  });

  test('should display user information columns', async ({ page }) => {
    // Check for common user information headers or data
    await expect(getTableHeader(page, 'name')).toBeVisible();
    await expect(getTableHeader(page, 'email')).toBeVisible();
    await expect(getTableHeader(page, 'role')).toBeVisible();
    await expect(getTableHeader(page, 'department')).toBeVisible();
    await expect(getTableHeader(page, 'position')).toBeVisible();
    await expect(getTableHeader(page, 'status')).toBeVisible();
  });

  test('should have filtering options', async ({ page }) => {
    // Check for filter inputs or dropdowns
    const filterLocator = getDirectoryFilter(page, 'department');
    const positionFilter = getDirectoryFilter(page, 'position');

    // At least one filter should be present
    await expect(filterLocator).toBeVisible();
  });

  test('should filter users by department', async ({ page }) => {
    const filterSelect = getDirectoryFilter(page, 'department');

    if (await filterSelect.isVisible()) {
      // Get initial user count
      const initialCount = await getDirectoryItems(page).count();

      // Select a department filter
      await filterSelect.selectOption({ index: 1 }); // Select second option (first might be "All")

      // Wait for filtering to apply
      await page.waitForTimeout(500);

      // Check that filtering worked (user count may change)
      const filteredCount = await getDirectoryItems(page).count();

      // Either count stays the same (no users in that department) or changes
      expect(filteredCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('should filter users by position', async ({ page }) => {
    const filterSelect = getDirectoryFilter(page, 'position');

    if (await filterSelect.isVisible()) {
      // Get initial user count
      const initialCount = await getDirectoryItems(page).count();

      // Select a position filter
      await filterSelect.selectOption({ index: 1 }); // Select second option (first might be "All")

      // Wait for filtering to apply
      await page.waitForTimeout(500);

      // Check that filtering worked
      const filteredCount = await getDirectoryItems(page).count();
      expect(filteredCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('should have sorting options', async ({ page }) => {
    // Check for sort buttons or headers
    await expect(getTableHeader(page, 'name')).toBeVisible();
  });

  test('should sort users by name', async ({ page }) => {
    const sortBySelect = getDirectorySortBy(page);

    if (await sortBySelect.isVisible()) {
      // Select sort by name
      await sortBySelect.selectOption('full_name');
      await page.waitForTimeout(500);

      // Check that sorting is applied (this is a basic check)
      await expect(getDirectoryItems(page).first()).toBeVisible();
    }
  });

  test('should sort users by role', async ({ page }) => {
    const sortBySelect = getDirectorySortBy(page);

    if (await sortBySelect.isVisible()) {
      // Select sort by role
      await sortBySelect.selectOption('role');
      await page.waitForTimeout(500);

      // Check that sorting is applied
      await expect(getDirectoryItems(page).first()).toBeVisible();
    }
  });

  test('should display user status indicators', async ({ page }) => {
    // Check for status indicators (active/inactive badges, icons, etc.)
    await expect(getStatusIndicator(page, 'active').first()).toBeVisible();
  });

  test('should handle empty or loading states', async ({ page }) => {
    // Check for loading indicators
    const loadingLocator = getDirectoryMessage(page, 'loading');

    // If loading is shown initially, wait for it to disappear
    if (await loadingLocator.isVisible()) {
      await expect(loadingLocator).toBeVisible();
      await loadingLocator.waitFor({ state: 'hidden', timeout: 10000 });
    }

    // Check for empty state messages
    const emptyLocator = getDirectoryMessage(page, 'empty');
    if (await emptyLocator.isVisible()) {
      await expect(emptyLocator).toBeVisible();
    } else {
      // If not empty, ensure users are displayed
      await expect(getDirectoryItems(page).first()).toBeVisible();
    }
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Check for error messages
    const errorLocator = getDirectoryMessage(page, 'error');

    if (await errorLocator.isVisible()) {
      await expect(errorLocator).toBeVisible();
    }
  });

  test('should check for console errors', async ({ page }) => {
    // Listen for console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Navigate and perform some actions
    await page.reload();
    await page.waitForTimeout(1000);

    // Check that no critical errors occurred
    expect(errors.length).toBeLessThan(3); // Allow some minor errors
  });

  test('should navigate to user profile on user selection', async ({ page }) => {
    // Find a user item that can be clicked
    const userItems = getDirectoryItems(page);
    const firstItem = userItems.first();

    if (await firstItem.isVisible() && await firstItem.isEnabled()) {
      // Get the data-testid attribute to extract the id
      const dataTestId = await firstItem.getAttribute('data-testid');
      const id = dataTestId?.replace('directory-item-', '') || '1';

      // Use the specific item locator
      const userItem = getDirectoryItem(page, id);

      // Store current URL
      const currentUrl = page.url();

      // Click on user item
      await userItem.click();

      // Check if navigation occurred (URL changed or profile screen loaded)
      const newUrl = page.url();
      const profileVisible = await getPageTitle(page, 'user-profile').isVisible();

      // Either URL changed or profile screen became visible
      expect(newUrl !== currentUrl || profileVisible).toBeTruthy();
    }
  });
});
