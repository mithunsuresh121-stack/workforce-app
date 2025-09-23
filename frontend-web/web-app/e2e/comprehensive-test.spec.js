import { test, expect } from '@playwright/test';

test.describe('Comprehensive Frontend and Backend Tests', () => {
  test('Login, Dashboard, Navigation, and API Endpoints', async ({ page, request }) => {
    // Frontend: Login flow
    await page.goto('http://localhost:3000/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('http://localhost:3000/dashboard');
    await page.screenshot({ path: 'dashboard-after-login.png', fullPage: true });
    const h3Elements = await page.locator('h3').allTextContents();
    console.log('H3 elements found:', h3Elements);
    await expect(page.locator('h3').filter({ hasText: 'Welcome back' })).toBeVisible();

    // Frontend: Navigation test
    const pages = ['Profile', 'Directory', 'Tasks', 'Leave', 'Dashboard'];
    for (const p of pages) {
      await page.click(`text=${p}`);
      await page.waitForURL(`http://localhost:3000/${p.toLowerCase()}`);
      await expect(page.locator(`h3:has-text("${p}")`)).toBeVisible();
    }

    // Frontend: Logout
    await page.click('button:has-text("Logout")');
    await page.waitForURL('http://localhost:3000/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Backend: API endpoint tests
    const apiBase = 'http://localhost:8000/api';

    // Test health endpoint
    const healthRes = await request.get('http://localhost:8000/health');
    expect(healthRes.ok()).toBeTruthy();
    const healthJson = await healthRes.json();
    expect(healthJson.status).toBe('healthy');

    // Test auth login
    const loginRes = await request.post(`${apiBase}/auth/login`, {
      data: { email: 'demo@company.com', password: 'password123' },
    });
    expect(loginRes.ok()).toBeTruthy();
    const loginJson = await loginRes.json();
    expect(loginJson).toHaveProperty('access_token');

    // Use token for authenticated requests
    const token = loginJson.access_token;
    const authHeaders = { Authorization: `Bearer ${token}` };

    // Test /me endpoint
    const meRes = await request.get(`${apiBase}/auth/me`, { headers: authHeaders });
    expect(meRes.ok()).toBeTruthy();
    const meJson = await meRes.json();
    expect(meJson).toHaveProperty('email', 'demo@company.com');

    // Test dashboard KPIs
    const kpisRes = await request.get(`${apiBase}/dashboard/kpis`, { headers: authHeaders });
    expect(kpisRes.ok()).toBeTruthy();
    const kpisJson = await kpisRes.json();
    expect(kpisJson).toHaveProperty('total_employees');

    // Test recent activities
    const activitiesRes = await request.get(`${apiBase}/dashboard/recent-activities`, { headers: authHeaders });
    expect(activitiesRes.ok()).toBeTruthy();
    const activitiesJson = await activitiesRes.json();
    expect(Array.isArray(activitiesJson)).toBe(true);

    // Test notifications
    const notificationsRes = await request.get(`${apiBase}/auth/notifications`, { headers: authHeaders });
    expect(notificationsRes.ok()).toBeTruthy();
    const notificationsJson = await notificationsRes.json();
    expect(Array.isArray(notificationsJson)).toBe(true);
  });
});
