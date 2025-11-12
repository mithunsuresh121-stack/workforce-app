# Procurement Management Integration TODO

## Status: Core features complete; integrate procurement as new module with RBAC (Admin/Manager access)

### Backend Implementation
- [x] Create SQLAlchemy models: `backend/app/models/vendor.py`, `purchase_order.py`, `inventory_item.py`
- [x] Create Pydantic schemas: `backend/app/schemas/procurement.py`
- [x] Create FastAPI router: `backend/app/routers/procurement.py` (CRUD, approvals, bidding)
- [x] Create service: `backend/app/services/procurement_service.py` (business logic, Redis caching)
- [x] Create Alembic migration: `backend/alembic/versions/new_procurement_tables.py`
- [x] Create pytest tests: `backend/tests/test_procurement.py` (coverage >90%)
- [x] Update `backend/app/models/__init__.py` (import new models)
- [x] Update `backend/app/routers/__init__.py` (import procurement router)
- [x] Update `backend/app/main.py` (include procurement router)
- [x] Fix updated_at field issue in models and services
- [x] Fix E2E test for procurement flow

### Frontend Implementation
- [ ] Create `frontend-web/web-app/src/pages/ProcurementDashboard.tsx` (charts with Recharts)
- [ ] Create `frontend-web/web-app/src/components/VendorList.tsx` (paginated table)
- [ ] Create `frontend-web/web-app/src/components/PurchaseOrderForm.tsx` (Formik/Yup form)
- [ ] Create `frontend-web/web-app/src/hooks/useProcurement.ts` (React Query, WebSocket)
- [ ] Create Vitest tests: `frontend-web/web-app/src/__tests__/Procurement.test.tsx`
- [ ] Update `frontend-web/web-app/src/App.tsx` (add routes: /procurement, /vendors, /pos)
- [ ] Update `frontend-web/web-app/package.json` (add react-query, recharts, etc.)

### Flutter Implementation
- [ ] Create `mobile/lib/screens/procurement_dashboard.dart` (ListView, HTTP, fl_chart)
- [ ] Update `mobile/lib/main.dart` (add /procurement route)
- [ ] Update `mobile/pubspec.yaml` (add fl_chart)

### Security & Integration
- [ ] Enforce RBAC (Admin/Manager for approvals/bidding)
- [ ] Add audit logs for PO actions
- [ ] Integrate WebSocket for real-time approval notifications
- [ ] Add demo seed data to `backend/app/seed_demo_user.py`

### Testing & Verification
- [ ] Run Alembic migration
- [ ] Run backend tests (pytest --cov)
- [ ] Run frontend tests (vitest run)
- [ ] Run Flutter tests (flutter test)
- [ ] Verify endpoints, RBAC, Redis caching, WebSocket
- [ ] Confirm responsive UI and type safety

### Dependencies
- [ ] Install frontend deps: npm i @tanstack/react-query recharts react-table formik yup
- [ ] Install Flutter deps: flutter pub add fl_chart
