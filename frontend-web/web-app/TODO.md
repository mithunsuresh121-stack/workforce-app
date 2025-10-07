# TODO List 1 for Frontend Profile Update E2E Tests and Manual Testing Instructions

## Completed
- Fixed test environment by separating Playwright and Vitest tests into different directories.
- Updated playwright.config.js to point to e2e directory.
- Fixed frontend Profile.jsx to correctly fetch and display profile data.

## Pending
- Write Playwright end-to-end tests for profile update and approval workflow.
  - Employee submits profile update request.
  - Super Admin approves or rejects the request.
  - Form validation tests.
  - Employee views updated profile after approval.
- Prepare manual testing instructions for profile update feature.

## Next Steps
- Run the new Playwright e2e tests to verify functionality.
- Review and refine manual testing instructions.
- Address any test failures or issues found during test runs.
