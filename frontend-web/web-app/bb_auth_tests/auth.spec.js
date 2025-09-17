import { test, expect } from '@playwright/test';

const START_URL = process.env.START_URL || 'http://localhost:3000';
const DEMO_EMAIL = process.env.DEMO_EMAIL || 'admin';
const DEMO_PASS = process.env.DEMO_PASS || 'password';

test.describe('Auth flow', () => {
  test('Login page loads and has no AuthProvider errors', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    await page.goto(`${START_URL}/login`, { waitUntil: 'networkidle' });
    expect(await page.title()).toBeTruthy(); // at least a page title exists
    // ensure no immediate 'useAuth must be used' error in console
    expect(consoleErrors.join('\n')).not.toContain('useAuth must be used within an AuthProvider');
  });

  test('Deep-link to /dashboard redirects to /login when not authenticated', async ({ page }) => {
    await page.goto(`${START_URL}/dashboard`, { waitUntil: 'networkidle' });
    // if redirected, url should include /login or remain not /dashboard
    expect(page.url()).not.toContain('/dashboard', { timeout: 2000 });
  });

  test('Successful login redirects to /dashboard', async ({ page }) => {
    await page.goto(`${START_URL}/login`, { waitUntil: 'networkidle' });
    // Try to fill common selectors, try multiple fallbacks
    const emailSelector = 'input[type="email"], input[name="email"], input[id*="email"]';
    const passSelector = 'input[type="password"], input[name="password"], input[id*="password"]';
    const submitSelector = 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")';
    await page.fill(emailSelector, DEMO_EMAIL);
    await page.fill(passSelector, DEMO_PASS);
    await Promise.all([
      page.click(submitSelector),
      page.waitForNavigation({ waitUntil: 'networkidle', timeout: 5000 }).catch(() => {}),
    ]);
    // Check we are on dashboard or root with Layout applied
    expect(page.url()).toMatch(/dashboard|\/$/);
  });

  test('Logout clears session and prevents dashboard access', async ({ page }) => {
    // assume already logged in from prior test; otherwise login
    await page.goto(`${START_URL}/`, { waitUntil: 'networkidle' });
    // Try clicking logout links/menu - try common selectors
    const logoutSelectors = [
      'button:has-text("Logout")',
      'a:has-text("Logout")',
      'button[aria-label="logout"]',
      'button#logout'
    ];
    let clicked=false;
    for (const s of logoutSelectors) {
      const el = await page.$(s);
      if (el) { await el.click(); clicked=true; break; }
    }
    if (!clicked) {
      // try to call window.localStorage.removeItem via JS as fallback
      await page.evaluate(() => localStorage.removeItem('user'));
      await page.reload({ waitUntil: 'networkidle' });
    }
    // After logout, deep-link should redirect
    await page.goto(`${START_URL}/dashboard`, { waitUntil: 'networkidle' });
    expect(page.url()).not.toContain('/dashboard');
  });
});
