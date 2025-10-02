# Fix Document Management Issues

## Steps
- [x] Add download endpoint in backend/app/routers/documents.py to support /documents/{id}/download
- [x] Adjust upload endpoint in backend/app/routers/documents.py to match frontend expectations (e.g., rename to /documents/upload or adjust parameters)
- [x] Ensure backend returns document fields that match frontend expectations (name instead of title, type instead of file_type, upload_date instead of created_at, uploaded_by as string)
- [x] Update backend/app/schemas/document.py to include computed fields or adjust response model
- [ ] Test upload functionality
- [ ] Test download functionality
- [ ] Test delete functionality
- [ ] Test listing and filtering
