import pytest
import requests
import io

def test_upload_document_manager_allowed(base_url, manager_jwt, auth_headers):
    """Test that manager can upload documents"""
    # Create a dummy file
    file_content = b"Test document content"
    files = {'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')}
    data = {'type': 'POLICY', 'access_role': 'EMPLOYEE'}
    headers = auth_headers(manager_jwt)
    # Remove Content-Type from headers as requests will set it for multipart
    headers.pop('Content-Type', None)

    response = requests.post(f"{base_url}/api/documents/upload", files=files, data=data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['type'] == 'POLICY'
    assert data['access_role'] == 'EMPLOYEE'

def test_upload_document_employee_denied(base_url, employee_jwt, auth_headers):
    """Test that employee cannot upload documents"""
    file_content = b"Test document content"
    files = {'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')}
    data = {'type': 'POLICY', 'access_role': 'EMPLOYEE'}
    headers = auth_headers(employee_jwt)
    headers.pop('Content-Type', None)

    response = requests.post(f"{base_url}/api/documents/upload", files=files, data=data, headers=headers)
    assert response.status_code == 403

def test_list_documents(base_url, manager_jwt, auth_headers):
    """Test listing documents"""
    response = requests.get(f"{base_url}/api/documents/list", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Assuming seeded data exists
    if data:
        assert 'id' in data[0]
        assert 'type' in data[0]
        assert 'access_role' in data[0]

def test_list_documents_employee_limited(base_url, employee_jwt, auth_headers):
    """Test that employee sees only EMPLOYEE access documents"""
    response = requests.get(f"{base_url}/api/documents/list", headers=auth_headers(employee_jwt))
    assert response.status_code == 200
    data = response.json()
    for doc in data:
        assert doc['access_role'] in ['EMPLOYEE']  # Assuming role hierarchy

def test_download_document_allowed(base_url, manager_jwt, auth_headers):
    """Test downloading a document that user has access to"""
    # First, list to get an ID
    response = requests.get(f"{base_url}/api/documents/list", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    docs = response.json()
    if docs:
        doc_id = docs[0]['id']
        response = requests.get(f"{base_url}/api/documents/download/{doc_id}", headers=auth_headers(manager_jwt))
        assert response.status_code == 200
        assert 'application/pdf' in response.headers.get('content-type', '')

def test_download_document_denied(base_url, employee_jwt, auth_headers):
    """Test downloading a document that user does not have access to"""
    # Assuming there is a MANAGER only document
    # First, get list as manager to find a MANAGER doc
    manager_response = requests.get(f"{base_url}/api/documents/list", headers=auth_headers(manager_jwt))
    assert manager_response.status_code == 200
    manager_docs = manager_response.json()
    manager_only_docs = [d for d in manager_docs if d['access_role'] == 'MANAGER']
    if manager_only_docs:
        doc_id = manager_only_docs[0]['id']
        response = requests.get(f"{base_url}/api/documents/download/{doc_id}", headers=auth_headers(employee_jwt))
        assert response.status_code == 403
