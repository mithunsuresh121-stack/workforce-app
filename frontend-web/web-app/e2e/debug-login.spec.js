import { test, expect } from '@playwright/test';

test('debug login flow', async ({ page }) => {
  // Listen for console messages
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push(`${msg.type()}: ${msg.text()}`);
  });

  // Go to login page
  await page.goto('http://localhost:3000/login');

  // Check login page loads
  await expect(page.locator('input[type="email"]')).toBeVisible();

  // Enter credentials
  await page.fill('input[type="email"]', 'demo@company.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Login")');

  // Wait for navigation or error
  await page.waitForTimeout(5000);

  // Log current URL and page content
  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());

  // Check if we're on dashboard
  if (page.url().includes('/dashboard')) {
    console.log('Successfully navigated to dashboard');

    // Wait a bit for content to load
    await page.waitForTimeout(2000);

    // Log all h3 elements
    const h3Elements = await page.locator('h3').allTextContents();
    console.log('All h3 elements:', h3Elements);

    // Log page HTML for debugging
    const pageContent = await page.content();
    console.log('Page contains "Welcome back":', pageContent.includes('Welcome back'));

    // Check for loading spinner
    const spinner = await page.locator('.flex.items-center.justify-center').count();
    console.log('Loading spinners found:', spinner);

    // Check for error messages
    const errors = await page.locator('.text-red-600').allTextContents();
    console.log('Error messages:', errors);

  } else {
    console.log('Not on dashboard, checking for error messages');
    const errorText = await page.locator('.text-red-600').allTextContents();
    console.log('Error text:', errorText);
  }

  // Log localStorage token
  const token = await page.evaluate(() => localStorage.getItem('token'));
  console.log('Token in localStorage:', token ? 'present' : 'not present');

  // Log console messages
  console.log('Console messages:');
  consoleMessages.forEach(msg => console.log('  ', msg));
});
