# Relational Data Flow Implementation Steps

## Step 1: Update Model Relationships with Cascades
- [ ] Update Company model: Add CASCADE to users, channels, meetings, chat_messages relationships
- [ ] Update User model: Add CASCADE to messages, reactions, meeting_participants, channel_members relationships
- [ ] Update Channel model: Add CASCADE to messages, channel_members relationships
- [ ] Update ChatMessage model: Add CASCADE to reactions relationship
- [ ] Update Meeting model: Add CASCADE to participants relationship

## Step 2: Add Lifecycle Audit Fields
- [ ] Add last_active (DateTime, nullable=True) to User model
- [ ] Add last_message_at (DateTime, nullable=True) to Channel model

## Step 3: Update Alembic Configuration
- [ ] Update backend/alembic/env.py to import all models for proper migration detection

## Step 4: Generate Migration
- [ ] Create new Alembic revision with column additions and FK constraint updates
- [ ] Verify migration includes proper CASCADE constraints

## Step 5: Create DB Integrity Tests
- [ ] Create backend/tests/test_db_integrity.py with cascade delete tests
- [ ] Add tests for referential integrity constraints
- [ ] Add validation for no orphaned records after deletes

## Step 6: Run Migration and Tests
- [ ] Execute migration on database (ensure venv is active)
- [ ] Run integrity tests to validate cascade behaviors
- [ ] Verify no data corruption occurred

## Step 7: Generate Summary Report
- [ ] Document all changes made in implementation report
- [ ] Create table lineage diagram showing relationships and cascades
- [ ] Validate all relational constraints are working correctly
