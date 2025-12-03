import { test, expect } from '@playwright/test';

test('login → dashboard → logout flow', async ({ page }) => {
  // Listen for console messages
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push(`${msg.type()}: ${msg.text()}`);
  });

  // Go to root page first (SPA routing)
  await page.goto('http://localhost:3000/');

  // Wait for the app to load and navigate to login
  await page.waitForSelector('input[type="email"]', { state: 'visible' });

  // Check login page loads (look for email input)
  await expect(page.locator('input[type="email"]')).toBeVisible();

  // Enter credentials (replace with real valid test creds)
  await page.fill('input[type="email"]', 'demo@company.com');
  await page.fill('input[type="password"]', 'password123');

  // Listen for network requests
  const requests = [];
  page.on('request', request => {
    if (request.url().includes('/api/auth/login')) {
      requests.push(request);
    }
  });

  const responses = [];
  page.on('response', response => {
    if (response.url().includes('/api/auth/login')) {
      responses.push(response);
    }
  });

  await page.click('button:has-text("Login")', { force: true });

  // Wait a bit for the login to process
  await page.waitForTimeout(3000);

  console.log('Login API requests made:', requests.length);
  console.log('Login API responses received:', responses.length);

  if (responses.length > 0) {
    const response = responses[0];
    console.log('Login response status:', response.status());
    console.log('Login response body:', await response.text());
  } else {
    console.log('No login API response received - proxy may not be working');
  }

  // Check if there's an error message
  const errorElement = page.locator('text=Invalid credentials');
  if (await errorElement.isVisible()) {
    console.log('Login failed with invalid credentials');
    throw new Error('Login failed');
  }

  // Check if we're still on login page
  if (page.url().includes('/login')) {
    console.log('Still on login page, login may have failed');
    throw new Error('Still on login page');
  }

  // Debug: take screenshot after login
  await page.screenshot({ path: 'login-after.png', fullPage: true });

  // Verify dashboard loads
  await page.waitForURL('http://localhost:3000/dashboard');
  await page.screenshot({ path: 'dashboard-loaded.png', fullPage: true });
  const content = await page.content();
  console.log('Dashboard page content:', content.substring(0, 2000));
  const h3Elements = await page.locator('h3').allTextContents();
  console.log('H3 elements found:', h3Elements);

  // Check if we have any h3 with "Welcome back"
  const welcomeElements = await page.locator('h3').filter({ hasText: 'Welcome back' }).count();
  console.log('Welcome back elements found:', welcomeElements);

  if (welcomeElements === 0) {
    console.warn('No "Welcome back" text found on dashboard, trying alternative selector');
    // Try alternative selector with partial text
    const altWelcomeElements = await page.locator('text=Welcome back').count();
    console.log('Alternative welcome elements found:', altWelcomeElements);
    if (altWelcomeElements === 0) {
      throw new Error('No "Welcome back" text found on dashboard with alternative selector');
    }
  }

  await expect(page.locator('h3').filter({ hasText: 'Welcome back' })).toBeVisible();



  // Test navigation to Profile
  await page.click('text=Profile');
  await page.waitForURL('http://localhost:3000/profile');
  await expect(page.locator('h3:has-text("Profile")')).toBeVisible();

  // Test navigation to Directory
  await page.click('text=Directory');
  await page.waitForURL('http://localhost:3000/directory');
  await expect(page.locator('h3:has-text("Directory")')).toBeVisible();

  // Test navigation to Tasks
  await page.click('text=Tasks');
  await page.waitForURL('http://localhost:3000/tasks');
  await expect(page.locator('h3:has-text("Tasks")')).toBeVisible();

  // Test navigation to Leave
  await page.click('text=Leave');
  await page.waitForURL('http://localhost:3000/leave');
  await expect(page.locator('h3:has-text("Leave")')).toBeVisible();

  // Back to Dashboard
  await page.click('text=Dashboard');
  await page.waitForURL('http://localhost:3000/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' }).first()).toBeVisible();

  // Logout
  await page.click('button:has-text("Logout")');

  // Verify redirect to login
  await page.waitForURL('http://localhost:3000/login');
  await expect(page.locator('input[type="email"]')).toBeVisible();

  // Log console messages
  console.log('Console messages during test:');
  consoleMessages.forEach(msg => console.log(msg));
});
