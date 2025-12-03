# TODO: Remove @material-tailwind/react from frontend-web/web-app

## Overview
Remove all usage of @material-tailwind/react components and replace with plain HTML/Tailwind CSS equivalents. The project already has custom linear components that serve as examples.

## Files to Update
- [x] src/index.js: Remove ThemeProvider import and usage
- [ ] src/pages/Dashboard_with_charts.jsx: Replace Card, CardBody, Typography, Spinner, Alert
- [ ] src/pages/Dashboard_contribution.jsx: Replace Card, CardBody, Typography, Spinner, Alert
- [ ] src/pages/Dashboard_fixed.jsx: Replace Card, CardBody, Typography, Spinner, Alert, DialogFooter
- [ ] src/pages/Profile_professional.jsx: Replace various components
- [ ] src/pages/Profile_enhanced.jsx: Replace various components
- [ ] src/pages/SuperAdminApprovals.jsx: Replace Card, CardBody, CardHeader, Typography, Button, Alert, Spinner, Chip, Dialog, DialogHeader, DialogBody, DialogFooter, Textarea
- [ ] src/components/DashboardCharts_fixed.jsx: Replace Card, CardBody, Typography, Spinner, Alert
- [ ] src/components/EditProfileForm_enhanced.jsx: Replace various components
 - [x] src/components/ProfileDetails_enhanced.jsx: Replace Typography, Card, CardBody, Skeleton
- [ ] src/components/DashboardCharts_final.jsx: Replace Card, CardBody, Typography, Spinner, Alert
 - [x] src/components/DashboardCharts_contribution.jsx: Replace Card, CardBody, Typography, Spinner, Alert
- [x] src/components/ProfileDetails.jsx: Replace Typography
- [ ] src/components/DashboardCharts_corrected.jsx: Replace Card, CardBody, Typography, Spinner, Alert
- [ ] src/components/EditProfileForm.jsx: Replace Card, CardBody, CardHeader, Typography, Input, Button, Alert, Select, Option, Textarea
 - [x] src/components/ProfileCard.jsx: Replace Card, CardBody, Avatar, Typography, Button, Chip, Tooltip
- [ ] src/components/ProfileCard_enhanced.jsx: Replace Card, CardBody, Avatar, Typography, Button, Chip, Tooltip, Badge

## Replacement Strategy
- Card/CardBody -> div with Tailwind classes (bg-white rounded-lg shadow-md p-4, etc.)
- Typography -> h1, h2, p, span with text classes (text-lg font-semibold, etc.)
- Button -> button with Tailwind classes (bg-blue-500 text-white px-4 py-2 rounded, etc.)
- Input -> input with Tailwind classes (border rounded px-3 py-2, etc.)
- Spinner -> Custom spinner div or loading text
- Alert -> div with bg-red-100 text-red-700, etc.
- Dialog/Modal -> Custom modal implementation or remove if not critical
- Avatar -> img or div with initials
- Chip -> span with classes
- Tooltip -> Custom tooltip or remove
- Badge -> span with classes
- Select/Option -> select/option with classes
- Textarea -> textarea with classes
- Skeleton -> Custom skeleton div

## Followup Steps
- [ ] Run npm install to ensure no missing deps
- [ ] Build the app: npm run build
- [ ] Start dev server: npm run dev
- [ ] Test all updated pages for UI consistency
- [ ] Verify no console errors related to missing components
