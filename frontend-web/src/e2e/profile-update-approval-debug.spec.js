import { test, expect } from '@playwright/test';

test.describe('Profile Update and Approval Workflow', () => {
  test('Employee submits profile update request', async ({ page }) => {
    // Login as employee
    await page.goto('http://localhost:3000/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await page.fill('input[type="email"]', 'demo@company.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('http://localhost:3000/dashboard');

    // Wait for dashboard to load
    await page.waitForTimeout(3000);

    // Navigate to Profile page
    await page.click('text=Profile');
    await page.waitForURL('http://localhost:3000/profile');

    // Wait for page to fully load
    await page.waitForTimeout(3000);

    // Debug: Check what's actually on the page
    const pageContent = await page.textContent('body');
    console.log('Page content after navigation:', pageContent.substring(0, 1000));

    // Try different selectors for the Profile heading
    const profileHeading = page.locator('h3').filter({ hasText: 'Profile' });
    await expect(profileHeading).toBeVisible({ timeout: 10000 });

    // Click Edit button to open edit dialog
    await page.click('button:has-text("Edit")');

    // Wait for edit dialog to appear
    await expect(page.locator('text=Edit Profile')).toBeVisible();

    // Fill out the edit form
    await page.fill('input[name="department"]', 'Engineering');
    await page.fill('input[name="position"]', 'Senior Developer');
    await page.fill('input[name="phone"]', '+1-555-0123');
    await page.fill('input[name="hire_date"]', '2023-01-15');
    await page.selectOption('select[name="gender"]', 'Male');
    await page.fill('textarea[name="address"]', '123 Tech Street, Suite 456');
    await page.fill('input[name="city"]', 'San Francisco');
    await page.fill('input[name="emergency_contact"]', 'Jane Doe: +1-555-0987');
    await page.fill('input[name="employee_id"]', 'EMP001');
    await page.fill('input[name="profile_picture_url"]', 'https://example.com/avatar.jpg');

    // Submit the form
    await page.click('button:has-text("Submit Request")');

    // Verify success message
    await expect(page.locator('text=Profile update request submitted successfully')).toBeVisible();

    // Close the dialog
    await page.click('button:has-text("Cancel")');

    // Logout
    await page.click('button:has-text("Logout")');
    await page.waitForURL('http://localhost:3000/login');
  });
});
