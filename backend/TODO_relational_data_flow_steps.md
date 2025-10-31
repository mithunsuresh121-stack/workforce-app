# Relational Data Flow + Lifecycle Correctness - Implementation Steps

## Current Status
- Models registered and validated
- Partial cascades added to Company model
- Missing lifecycle fields (last_active in User, last_message_at in Channel)
- No DB-level cascades or integrity tests

## Pending Tasks

### 1. Update Model Relationships with Cascades
- [ ] backend/app/models/company.py: Add missing 'attendances' relationship with cascade="all, delete-orphan"
- [ ] backend/app/models/user.py: Add 'last_active' field; update relationships with appropriate cascades
- [ ] backend/app/models/channels.py: Add 'last_message_at' field; add cascades to all relationships
- [ ] backend/app/models/chat.py: Add cascades to all relationships
- [ ] backend/app/models/message_reactions.py: Add cascades to message and user relationships
- [ ] backend/app/models/meetings.py: Add cascades to organizer, company, participants relationships
- [ ] backend/app/models/meeting_participants.py: Add cascades to meeting and user relationships

### 2. Generate Alembic Migration
- [ ] Run `alembic revision --autogenerate -m "add_cascades_lifecycle_fields"`
- [ ] Review migration file for DB-level ON DELETE CASCADE on FKs
- [ ] Edit migration to add ondelete='CASCADE' to FK constraints where appropriate

### 3. Run Migration
- [ ] Execute `alembic upgrade head`
- [ ] Verify no errors in migration

### 4. Create/Update DB Integrity Tests
- [ ] Update backend/tests/test_db_integrity.py with comprehensive cascade delete test
- [ ] Add constraint violation tests (FK integrity errors)
- [ ] Ensure test imports all models to configure mappers

### 5. Run Tests
- [ ] Execute `pytest backend/tests/test_db_integrity.py -v`
- [ ] Verify cascade delete works and constraints are enforced

### 6. Generate Summary Report
- [ ] Create backend/RELATIONAL_INTEGRITY_REPORT.md with:
  - Summary of changes made
  - Test results
  - ASCII table lineage diagram
  - Any remaining issues

### 7. Final Verification
- [ ] Run full pytest suite to ensure no regressions
- [ ] Verify live testing (if applicable) shows proper cascade behavior
