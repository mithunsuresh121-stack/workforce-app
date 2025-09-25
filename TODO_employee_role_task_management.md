# Employee Role Task Management Implementation

## Backend Changes
- [x] Create Attachment model (backend/app/models/attachment.py)
- [x] Update Task model (backend/app/models/task.py) - add attachments relationship, optional team_id (commented)
- [x] Update schemas (backend/app/schemas/schemas.py) - add Attachment schemas, update Task schemas
- [x] Update crud (backend/app/crud/task.py) - add attachment functions
- [x] Update routers (backend/app/routers/tasks.py) - add attachment endpoints, update permissions
- [x] Create uploads directory (backend/uploads/)

## Frontend Changes
- [x] Update Tasks.jsx - role-based filtering, assignee dropdown, attachment UI
- [x] Create TaskAttachments component (frontend-web/web-app/src/components/TaskAttachments.jsx)

## Database Migration
- [ ] Run Alembic migration for new Attachment table (pending - multiple heads in Alembic, needs merge)

## Testing
- [ ] Update tests/test_tasks.py with new test cases
- [ ] Test backend endpoints
- [ ] Test frontend UI

## Validation
- [ ] Verify role permissions
- [ ] Verify file upload/download
- [ ] Verify delete restrictions
