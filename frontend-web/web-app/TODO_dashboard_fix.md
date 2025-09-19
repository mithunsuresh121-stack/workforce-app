# Dashboard Loading Fix TODO

## Steps to Complete

- [x] Export the axios api instance from AuthContext.jsx
- [x] Update Dashboard.jsx to import and use the exported api instance instead of plain axios
- [x] Update Profile.jsx to use the exported api instance instead of creating its own
- [x] Test dashboard loading to verify API calls now hit localhost:8000
- [x] If 403 persists, investigate backend permissions for dashboard endpoints
