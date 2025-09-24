# Sidebar Company Info Implementation

## Backend Changes
- [x] Add `logo_url` field to Company model
- [x] Update CompanyOut schema to include logo_url
- [x] Update UserOut schema to include company name and logo_url
- [x] Update `/auth/me` endpoint to return company data
- [x] Create `/companies/{company_id}` endpoint for company details

## Frontend Changes
- [x] Update Sidebar component to conditionally hide Directory for Employees
- [x] Add company info section at bottom for Employees only
- [x] Create Company page component
- [x] Add `/company` route to App.jsx

## Testing
- [ ] Test authentication flow with different roles
- [ ] Verify company data display and navigation
- [ ] Test error handling for missing company data
