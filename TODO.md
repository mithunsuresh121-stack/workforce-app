# TODO: Add Sign Up and Remove Company ID from Login

## Backend Changes
- [x] Update LoginPayload in schemas.py to make company_id optional
- [x] Modify login endpoint in auth.py to use user's company_id if not provided in payload

## Frontend Changes
- [x] Remove company ID field from login_screen.dart
- [x] Add "Sign Up" button to login_screen.dart
- [x] Create signup_screen.dart with form (email, password, full_name)
- [x] Update auth_provider.dart to add signup method
- [x] Update app.dart to import signup_screen.dart

## Testing
- [ ] Test login without company ID
- [ ] Test sign up flow
- [ ] Verify backend handles optional company_id correctly
