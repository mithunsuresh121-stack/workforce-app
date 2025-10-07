import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_upload_document_simple(employee_jwt, auth_headers):
    headers = auth_headers(employee_jwt)
    file_content = b"Test file content"
    response = client.post(
        "/api/documents/upload",
        files={"file": ("testfile.txt", file_content, "text/plain")},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "testfile.txt"
    assert "id" in data

def test_get_documents(employee_jwt, auth_headers):
    headers = auth_headers(employee_jwt)
    response = client.get("/api/documents/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_document(employee_jwt, auth_headers):
    headers = auth_headers(employee_jwt)
    # First upload a document
    file_content = b"Test file content"
    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("updatefile.txt", file_content, "text/plain")},
        headers=headers
    )
    assert upload_response.status_code == 201
    doc_id = upload_response.json()["id"]

    # Update the document title and description
    update_data = {"title": "Updated Title", "description": "Updated description"}
    update_response = client.put(f"/api/documents/{doc_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    updated_doc = update_response.json()
    assert updated_doc["title"] == "Updated Title"
    assert updated_doc["description"] == "Updated description"

def test_delete_document(employee_jwt, auth_headers):
    headers = auth_headers(employee_jwt)
    # Upload a document to delete
    file_content = b"Test file content"
    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("deletefile.txt", file_content, "text/plain")},
        headers=headers
    )
    assert upload_response.status_code == 201
    doc_id = upload_response.json()["id"]

    # Delete the document
    delete_response = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Document deleted"

    # Verify document no longer exists
    get_response = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_response.status_code == 404
