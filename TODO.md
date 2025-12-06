# Multi-Tenant SaaS Onboarding Flow Implementation

## Backend Changes
- [ ] Add `/companies/user` endpoint in `companies.py` to get user's companies list
- [ ] Update auth.py login to ensure company_id is included in token if user has one

## Frontend Changes
- [ ] Update AuthProvider to parse JWT token and extract companyId, role, email on login
- [ ] Add getUserCompanies method to ApiService
- [ ] Create CompanySelectorScreen for selecting from multiple companies
- [ ] Update SignupScreen to navigate to onboarding flow after successful signup
- [ ] Update LoginScreen to navigate to onboarding flow after successful login
- [ ] Update CompanyCreationScreen to use ApiService and handle navigation properly
- [ ] Create OnboardingFlow widget to orchestrate the flow: check companies -> create/select -> dashboard
- [ ] Update AppShell to include company switcher in app bar/drawer
- [ ] Ensure company ID is stored persistently and used in API headers

## Testing
- [ ] Test signup -> create company -> dashboard flow
- [ ] Test login with no company -> create company flow
- [ ] Test login with multiple companies -> selector -> dashboard flow
- [ ] Test company switching functionality
- [ ] Verify persistent storage of selected company
