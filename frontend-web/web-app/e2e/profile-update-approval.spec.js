import { test, expect } from '@playwright/test';

test.describe('Profile Update and Approval Workflow', () => {
  test('Employee submits profile update request', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });

    // Login as employee
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Sign In")');

    // Wait for dashboard to load
    await page.waitForURL('http://localhost:3000/dashboard', { timeout: 10000 });
    await expect(page.locator('h3:has-text("Welcome back")')).toBeVisible();

    // Navigate to Profile page
    await page.click('a[href="/profile"]');
    await page.waitForURL('http://localhost:3000/profile', { timeout: 10000 });

    // Wait for page to load and debug
    await page.waitForTimeout(2000);
    console.log('Page content:', await page.textContent('body'));

    // Verify Profile page loads
    await expect(page.locator('h3:has-text("Profile")')).toBeVisible();

    // Click Edit Profile button
    await page.click('button:has-text("Edit Profile")');

    // Verify Edit Profile dialog opens
    await expect(page.locator('text=Edit Profile')).toBeVisible();

    // Fill out profile update form
    await page.fill('input[name="phone"]', '+1-555-0123');
    await page.fill('input[name="department"]', 'Engineering');
    await page.fill('input[name="position"]', 'Senior Developer');
    await page.fill('input[name="address"]', '123 Tech Street');
    await page.fill('input[name="city"]', 'San Francisco');
    await page.fill('input[name="emergency_contact"]', '+1-555-0987');

    // Submit the profile update request
    await page.click('button:has-text("Submit Update Request")');

    // Verify success message
    await expect(page.locator('text=Profile update request submitted successfully')).toBeVisible();

    // Verify dialog closes
    await expect(page.locator('text=Edit Profile')).not.toBeVisible();
  });

  test('Super Admin views and approves profile update request', async ({ page, request }) => {
    // First, create a profile update request via API
    const loginResponse = await request.post('http://localhost:8000/api/auth/login', {
      data: { email: 'demo@company.com', password: 'password123' }
    });
    const loginData = await loginResponse.json();
    const token = loginData.access_token;

    // Submit profile update request
    await request.post('http://localhost:8000/api/profile/request-update', {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        user_id: 1, // Assuming demo user ID is 1
        request_type: 'update',
        payload: {
          phone: '+1-555-0123',
          department: 'Engineering',
          position: 'Senior Developer'
        }
      }
    });

    // Login as Super Admin
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button:has-text("Sign In")');

    // Wait for dashboard
    await page.waitForURL('http://localhost:3000/dashboard', { timeout: 10000 });

    // Navigate to Super Admin Approvals
    await page.goto('http://localhost:3000/approvals', { waitUntil: 'networkidle' });

    // Verify page loads
    await expect(page.locator('h3:has-text("Profile Update Requests")')).toBeVisible();

    // Find the pending request
    await expect(page.locator('text=Pending')).toBeVisible();

    // Click Approve button
    await page.click('button:has-text("Approve")');

    // Verify approval confirmation
    await expect(page.locator('text=Request approved successfully')).toBeVisible();

    // Verify request status changes to approved
    await expect(page.locator('text=Approved')).toBeVisible();
  });

  test('Super Admin rejects profile update request', async ({ page, request }) => {
    // First, create a profile update request via API
    const loginResponse = await request.post('http://localhost:8000/api/auth/login', {
      data: { email: 'demo@company.com', password: 'password123' }
    });
    const loginData = await loginResponse.json();
    const token = loginData.access_token;

    // Submit profile update request
    await request.post('http://localhost:8000/api/profile/request-update', {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        user_id: 1,
        request_type: 'update',
        payload: {
          phone: '+1-555-0123',
          department: 'Engineering'
        }
      }
    });

    // Login as Super Admin
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button:has-text("Sign In")');

    // Navigate to Super Admin Approvals
    await page.click('a[href="/approvals"]');
    await page.waitForURL('http://localhost:3000/approvals', { timeout: 10000 });

    // Find the pending request
    await expect(page.locator('text=Pending')).toBeVisible();

    // Click Reject button
    await page.click('button:has-text("Reject")');

    // Verify rejection confirmation
    await expect(page.locator('text=Request rejected successfully')).toBeVisible();

    // Verify request status changes to rejected
    await expect(page.locator('text=Rejected')).toBeVisible();
  });

  test('Form validation prevents invalid profile updates', async ({ page }) => {
    // Login as employee
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Sign In")');

    // Navigate to Profile
    await page.click('a[href="/profile"]');
    await page.click('button:has-text("Edit Profile")');

    // Try to submit empty form
    await page.click('button:has-text("Submit Update Request")');

    // Verify validation errors (assuming form has validation)
    // Note: This test may need adjustment based on actual form validation implementation
    await expect(page.locator('text=Edit Profile')).toBeVisible(); // Dialog should remain open
  });

  test('Employee views updated profile after approval', async ({ page, request }) => {
    // First, login as employee and submit update request
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Sign In")');

    // Submit profile update
    await page.click('a[href="/profile"]');
    await page.click('button:has-text("Edit Profile")');
    await page.fill('input[name="phone"]', '+1-555-0123');
    await page.fill('input[name="department"]', 'Engineering');
    await page.click('button:has-text("Submit Update Request")');

    // Logout
    await page.click('button:has-text("Logout")');

    // Login as Super Admin and approve the request
    await page.fill('input[type="email"]', 'admin@app.com');
    await page.fill('input[type="password"]', 'supersecure123');
    await page.click('button:has-text("Sign In")');

    await page.click('a[href="/approvals"]');
    await page.click('button:has-text("Approve")');

    // Logout as Super Admin
    await page.click('button:has-text("Logout")');

    // Login back as employee
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Sign In")');

    // Check updated profile
    await page.click('a[href="/profile"]');
    await expect(page.locator('text=+1-555-0123')).toBeVisible();
    await expect(page.locator('text=Engineering')).toBeVisible();
  });
});
