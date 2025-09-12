import type { Page } from '@playwright/test';
import { request } from '@playwright/test';

export async function loginUser(page: Page) {
  try {
    const apiContext = await request.newContext();
    const response = await apiContext.post('http://localhost:8000/auth/login', {
      data: {
        email: 'admin@app.com',   // adjust to match your seeded test user
        password: 'supersecure123',        // adjust accordingly
      },
    });

    if (!response.ok()) {
      throw new Error(`Login failed: ${response.status()} ${response.statusText()}`);
    }

    const body = await response.json();
    const token = body.access_token;

    if (!token) {
      throw new Error('Auth token missing in login response');
    }

    console.log('Login successful, token received');

    // Store token in browser localStorage
    await page.addInitScript((value) => {
      window.localStorage.setItem('auth_token', value);
    }, token);

    console.log('Auth token stored in localStorage via addInitScript');
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// Add resilient wait helpers for inputs and buttons
export function getProfileInput(page: Page, field: string) {
  const locator = page.locator(`[data-testid="profile-${field}"]`);
  return locator;
}

export function getProfileButton(page: Page, button: string) {
  const locator = page.locator(`[data-testid="profile-${button}-button"]`);
  return locator;
}

export function getProfileMessage(page: Page, type: string) {
  return page.locator(`[data-testid="profile-${type}-message"]`);
}

export function getDirectoryFilter(page: Page, filter: string) {
  return page.locator(`[data-testid="directory-filter-${filter}"]`);
}

export function getDirectoryItem(page: Page, id: string) {
  return page.locator(`[data-testid="directory-item-${id}"]`);
}

export function getDirectoryMessage(page: Page, type: string) {
  return page.locator(`[data-testid="directory-${type}"]`);
}

export function getDirectoryList(page: Page) {
  return page.locator('[data-testid="directory-user-list"]');
}

export function getDirectoryItems(page: Page) {
  return page.locator('[data-testid^="directory-item-"]');
}

export function getDirectorySort(page: Page, type: string) {
  return page.locator(`[data-testid="directory-sort-${type}"]`);
}

export function getDirectorySortBy(page: Page) {
  return page.locator('[data-testid="directory-sort-by"]');
}

export function getDirectorySortOrder(page: Page) {
  return page.locator('[data-testid="directory-sort-order"]');
}

// Additional helpers for page titles and other elements
export function getPageTitle(page: Page, title: string) {
  return page.locator(`[data-testid="page-title-${title}"]`);
}

export function getSuccessMessage(page: Page) {
  return page.locator(`[data-testid="profile-success-message"]`);
}

export function getTableHeader(page: Page, header: string) {
  return page.locator(`[data-testid="directory-header-${header}"]`);
}

export function getStatusIndicator(page: Page, status: string) {
  return page.locator(`[data-testid="status-${status}"]`);
}
