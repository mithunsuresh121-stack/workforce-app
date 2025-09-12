import { test, expect } from '@playwright/test';
import {
  getProfileInput,
  getProfileButton,
  getProfileMessage,
  getPageTitle,
  getSuccessMessage,
  loginUser,
} from './test-utils.js';

test.describe('ProfileScreen', () => {
  test.beforeEach(async ({ page }) => {
    // Capture console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await loginUser(page);
    await page.goto('/profile');

    // Log any console errors after navigation
    if (errors.length > 0) {
      console.log('Console errors:', errors);
    }
  });

  test('should load profile page correctly', async ({ page }) => {
    try {
      // Wait for page to load
      await page.waitForLoadState('networkidle');

      // Debug: Log page content
      const pageContent = await page.content();
      console.log('Page content length:', pageContent.length);
      console.log('Page title:', await page.title());

      // Debug: Check if the element exists at all
      const elementExists = await page.locator('[data-testid="page-title-user-profile"]').count() > 0;
      console.log('Page title element exists:', elementExists);

      // Debug: Check all data-testid elements on the page
      const allDataTestIds = await page.locator('[data-testid]').all();
      console.log('All data-testid elements:', await Promise.all(allDataTestIds.map(async (el) => await el.getAttribute('data-testid'))));

      await expect(getPageTitle(page, 'user-profile')).toBeVisible({ timeout: 10000 });
    } catch (error) {
      await page.screenshot({ path: 'profile-page-error.png', fullPage: true });
      console.log('Screenshot saved: profile-page-error.png');
      throw error;
    }
  });

  test('should display user profile information', async ({ page }) => {
    await expect(getProfileInput(page, 'full-name')).toBeVisible();
    await expect(getProfileInput(page, 'department')).toBeVisible();
    await expect(getProfileInput(page, 'position')).toBeVisible();
    await expect(getProfileInput(page, 'phone')).toBeVisible();
    await expect(getProfileInput(page, 'hire-date')).toBeVisible();
  });

  test('should allow editing profile fields', async ({ page }) => {
    await page.waitForTimeout(2000); // Wait for React to render
    const editButton = getProfileButton(page, 'edit');
    await editButton.waitFor({ state: 'visible', timeout: 10000 });
    await editButton.click();
    await expect(getProfileInput(page, 'full-name')).toBeEditable();
  });

  test('should save profile changes successfully', async ({ page }) => {
    await page.waitForTimeout(2000); // Wait for React to render
    const editButton = getProfileButton(page, 'edit');
    await editButton.waitFor({ state: 'visible', timeout: 10000 });
    await editButton.click();
    const fullNameInput = getProfileInput(page, 'full-name');
    await fullNameInput.waitFor({ state: 'visible', timeout: 10000 });
    await fullNameInput.fill('Test User Updated');
    const saveButton = getProfileButton(page, 'save');
    await saveButton.waitFor({ state: 'visible', timeout: 10000 });
    await saveButton.click();
    await expect(getSuccessMessage(page)).toBeVisible();
  });

  test('should display error message on invalid input', async ({ page }) => {
    await page.waitForTimeout(2000); // Wait for React to render
    const editButton = getProfileButton(page, 'edit');
    await editButton.waitFor({ state: 'visible', timeout: 10000 });
    await editButton.click();
    const fullNameInput = getProfileInput(page, 'full-name');
    await fullNameInput.waitFor({ state: 'visible', timeout: 10000 });
    await fullNameInput.fill('Test User');
    const phoneInput = getProfileInput(page, 'phone');
    await phoneInput.waitFor({ state: 'visible', timeout: 10000 });
    await phoneInput.fill('invalid-phone');
    const saveButton = getProfileButton(page, 'save');
    await saveButton.waitFor({ state: 'visible', timeout: 10000 });
    await saveButton.click();
    await expect(getProfileMessage(page, 'error')).toBeVisible();
  });
});
