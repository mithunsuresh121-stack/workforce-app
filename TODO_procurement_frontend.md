# Frontend Procurement Integration TODO

## 1. Dependencies
- [ ] Add react-table to package.json
- [ ] Install dependencies (npm install)

## 2. Core Components
- [ ] Create ProcurementDashboard.tsx (Recharts pie/bar charts)
- [ ] Create VendorList.tsx (React Table with pagination, CRUD)
- [ ] Create PurchaseOrderForm.tsx (Formik/Yup validation)
- [ ] Create useProcurement.ts (React Query + WebSocket)

## 3. Routing & Security
- [ ] Update App.tsx with procurement routes (/procurement, /procurement/vendors, /procurement/pos)
- [ ] Enhance ProtectedRoute.jsx with RBAC (Admin/Manager access)

## 4. Testing
- [ ] Create Procurement.test.tsx (Vitest tests for all components)
- [ ] Run tests with coverage (vitest run --coverage)

## 5. Documentation
- [ ] Update TODO_integration.md to mark frontend procurement complete

## 6. Verification
- [ ] Verify WebSocket integration for approval notifications
- [ ] Verify API calls to /api/procurement/* endpoints
- [ ] Test responsive UI with Tailwind CSS
