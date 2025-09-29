# Auto-Fix “Loading…” Blank Page in Workforce App

## Steps
- [ ] Check backend availability via curl to http://localhost:8000/api/auth/me
- [ ] If down, activate venv: source backend/venv/bin/activate
- [ ] Start FastAPI backend: uvicorn main:app --reload --host 127.0.0.1 --port 8000
- [ ] Verify backend responds (401 or user JSON)
- [ ] Seed test users: python seed_data.py
- [ ] Test login endpoint with curl for superadmin
- [ ] Confirm /api/auth/me returns user JSON
- [ ] Start frontend on localhost:3000 if not running
- [ ] Verify frontend renders dashboard past “loading…” screen
