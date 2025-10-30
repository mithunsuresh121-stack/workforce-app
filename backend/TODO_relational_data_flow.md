# Relational Data Flow + Lifecycle Correctness

## Overview
Update SQLAlchemy models with proper cascade delete behaviors, add lifecycle audit fields, create migration, and validate with integrity tests.

## Current Status
- Models registered and validated
- Relationships exist but lack cascade configurations
- Missing lifecycle fields: User.last_active, Channel.last_message_at

## Tasks

### 1. Update Model Relationships with Cascades
- [ ] Company model: Add CASCADE to users, channels, meetings, chat_messages
- [ ] User model: Add CASCADE to messages, reactions, meeting_participants, channel_members
- [ ] Channel model: Add CASCADE to messages, channel_members
- [ ] ChatMessage model: Add CASCADE to reactions
- [ ] Meeting model: Add CASCADE to participants

### 2. Add Lifecycle Audit Fields
- [ ] User model: Add last_active (DateTime, nullable=True)
- [ ] Channel model: Add last_message_at (DateTime, nullable=True)

### 3. Update Alembic Configuration
- [ ] Update env.py to import all models for migration detection

### 4. Generate Migration
- [ ] Create new Alembic revision with column additions and FK constraint updates

### 5. Create DB Integrity Tests
- [ ] Test cascade delete behaviors for all relationships
- [ ] Test referential integrity constraints
- [ ] Validate no orphaned records after deletes

### 6. Run Migration and Tests
- [ ] Execute migration on database
- [ ] Run integrity tests
- [ ] Verify no data corruption

### 7. Generate Summary Report
- [ ] Document all changes made
- [ ] Create table lineage diagram showing relationships and cascades
- [ ] Validate relational constraints

## Dependencies
- All models must be imported in alembic env.py
- Database connection must be available
- Existing data should not be affected by schema changes

## Validation Criteria
- All cascade deletes work correctly without leaving orphans
- Lifecycle fields are nullable and properly tracked
- Foreign key constraints prevent invalid data
- Migration is reversible
