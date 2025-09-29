# Frontend Theme Refactor TODO

## 1. Update src/theme.js ✅
- Convert to MUI createTheme with palette, typography, components, shape, spacing matching Login page.

## 2. Update src/App.jsx ✅
- Import ThemeProvider and theme.
- Wrap Router in ThemeProvider.

## 3. Patch src/layouts/DashboardLayout.jsx ✅
- Update sx to use theme refs (e.g., colors, spacing).
- Add responsive sidebar collapse with useMediaQuery.
- Style buttons/topbar with theme.

## 4. Patch Pages ✅
- Dashboard.jsx: Update Typography, Card sx, chart colors, grid responsiveness.
- Employees.jsx: Update titles, cards, tables with theme.
- Projects.jsx: Same as above.
- Tasks.jsx: Same.
- Leave.jsx: Same.
- Attendance.jsx: Same.
- Documents.jsx: Same.

## 5. Scan and Remove Inconsistent Styling ✅
- Use search_files to find Tailwind classes or inline styles.
- Replace with MUI theme equivalents.

## 6. Followup Steps
- Run npm run build to check errors.
- Use browser_action to verify theme consistency and responsiveness.
- Run npm start if needed for live testing.
