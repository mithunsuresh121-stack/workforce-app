# Manual Testing Instructions for Profile Update Feature

## Overview
This document provides step-by-step instructions for manually testing the profile update and approval workflow in the Workforce App.

## Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend server running on `http://localhost:3000`
3. Database seeded with test users (demo@company.com, superadmin@company.com)

## Test Users
- **Employee**: demo@company.com / password123
- **Super Admin**: superadmin@company.com / password123

## Test Scenarios

### Scenario 1: Employee Profile Update Request

#### Steps:
1. Open browser and navigate to `http://localhost:3000/login`
2. Login with employee credentials:
   - Email: demo@company.com
   - Password: password123
3. Click "Sign In" button
4. Verify dashboard loads with "Welcome back" message
5. Click "Profile" in the navigation menu
6. Verify Profile page loads with "Profile" heading
7. Click "Edit Profile" button
8. Verify "Edit Profile" dialog opens
9. Fill in the following fields:
   - Phone: +1-555-0123
   - Department: Engineering
   - Position: Senior Developer
   - Address: 123 Tech Street
   - City: San Francisco
   - Emergency Contact: +1-555-0987
10. Click "Submit Update Request" button
11. Verify success message: "Profile update request submitted successfully! It will be reviewed by an administrator."
12. Verify dialog closes automatically

#### Expected Results:
- Profile update request is submitted successfully
- Success message appears
- Dialog closes
- Request appears in Super Admin approvals queue

### Scenario 2: Super Admin Approves Profile Update

#### Steps:
1. Open new browser tab/window and navigate to `http://localhost:3000/login`
2. Login with Super Admin credentials:
   - Email: superadmin@company.com
   - Password: password123
3. Click "Sign In" button
4. Verify dashboard loads
5. Click "Super Admin Approvals" in navigation menu
6. Verify "Profile Update Requests" page loads
7. Look for pending request from demo@company.com
8. Verify request shows status "Pending"
9. Click "Approve" button on the request
10. Verify confirmation message: "Request approved successfully"
11. Verify request status changes to "Approved"

#### Expected Results:
- Request status changes from "Pending" to "Approved"
- Employee's profile is updated with new information
- Success message appears

### Scenario 3: Super Admin Rejects Profile Update

#### Steps:
1. Login as Super Admin (same as Scenario 2, steps 1-6)
2. Find another pending request or create new one
3. Click "Reject" button on the request
4. Verify confirmation message: "Request rejected successfully"
5. Verify request status changes to "Rejected"

#### Expected Results:
- Request status changes from "Pending" to "Rejected"
- Employee's profile remains unchanged
- Success message appears

### Scenario 4: Employee Views Updated Profile

#### Steps:
1. Login as employee (demo@company.com)
2. Navigate to Profile page
3. Verify updated information appears:
   - Phone: +1-555-0123
   - Department: Engineering
   - Position: Senior Developer
   - Address: 123 Tech Street
   - City: San Francisco
   - Emergency Contact: +1-555-0987

#### Expected Results:
- All updated profile information displays correctly
- Profile card shows user information
- Profile details section shows all updated fields

### Scenario 5: Form Validation Testing

#### Steps:
1. Login as employee
2. Navigate to Profile page
3. Click "Edit Profile" button
4. Leave all fields empty
5. Click "Submit Update Request" button
6. Verify form validation prevents submission
7. Fill in invalid data (e.g., invalid phone number format)
8. Verify validation messages appear

#### Expected Results:
- Form cannot be submitted with empty required fields
- Validation messages appear for invalid data
- Dialog remains open until valid data is entered

## Error Scenarios to Test

### Network Error Handling
1. Submit profile update request
2. Disconnect internet during submission
3. Verify appropriate error message appears
4. Reconnect and retry submission

### Unauthorized Access
1. Try to access Super Admin approvals as regular employee
2. Verify access is denied with appropriate error message

### Invalid Data Submission
1. Try to submit profile update for another user (as employee)
2. Verify permission denied error

## Browser Compatibility Testing
- Test all scenarios in Chrome, Firefox, and Safari
- Verify responsive design on mobile and tablet viewports

## Performance Testing
- Submit multiple profile update requests
- Verify Super Admin can handle multiple pending requests
- Test page load times for Profile and Super Admin Approvals pages

## Data Persistence Testing
- Submit profile update and approve it
- Logout and login again
- Verify changes persist across sessions

## Edge Cases
- Test with very long text in fields (department, position, address)
- Test with special characters in fields
- Test with empty optional fields
- Test multiple simultaneous requests from different users

## Reporting Issues
When reporting issues, please include:
- Browser and version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Console error messages
- Network request/response details

## Success Criteria
- All test scenarios pass without errors
- Profile updates work end-to-end
- Super Admin approval workflow functions correctly
- Form validation works as expected
- Error handling is appropriate
- UI is responsive and user-friendly
