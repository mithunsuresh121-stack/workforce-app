# TODO: Authentication and Role Management Modifications

## Current Status
- [x] Updated signup logic to not require or assign company_id automatically. All new users sign up as EMPLOYEE with company_id=None.
- [ ] Implement company creation endpoint for logged-in users without a company.
- [ ] Add endpoint for assigning users to a company (update company_id and role).
- [ ] Update role assignment: Company creator becomes SUPERADMIN for that company.
- [ ] Frontend (Mobile/Flutter): Create screen for company creation.
- [ ] Frontend (Mobile/Flutter): Create screen for assigning users to company.
- [ ] Verify login works without company_id.
- [ ] Test role assignments and hierarchy.
- [ ] Ensure no breakage for existing users.

## Next Steps
1. Modify backend/routers/companies.py to allow company creation for users without company_id, assigning them SUPERADMIN role.
2. Add new endpoint in backend/routers/companies.py or auth.py for assigning users to company.
3. Update mobile/lib/src to add CompanyCreationScreen.
4. Update mobile/lib/src to add UserAssignmentScreen.
5. Test all changes.
