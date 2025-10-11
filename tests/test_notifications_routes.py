import pytest
import requests

def test_create_announcement_admin_allowed(base_url, superadmin_jwt, auth_headers):
    """Test that admin can create announcements"""
    data = {
        "title": "Test Announcement",
        "message": "This is a test announcement."
    }
    response = requests.post(f"{base_url}/api/notifications/announce", json=data, headers=auth_headers(superadmin_jwt))
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['title'] == "Test Announcement"
    assert data['message'] == "This is a test announcement."

def test_create_announcement_manager_denied(base_url, manager_jwt, auth_headers):
    """Test that manager cannot create announcements"""
    data = {
        "title": "Test Announcement",
        "message": "This is a test announcement."
    }
    response = requests.post(f"{base_url}/api/notifications/announce", json=data, headers=auth_headers(manager_jwt))
    assert response.status_code == 403

def test_create_announcement_employee_denied(base_url, employee_jwt, auth_headers):
    """Test that employee cannot create announcements"""
    data = {
        "title": "Test Announcement",
        "message": "This is a test announcement."
    }
    response = requests.post(f"{base_url}/api/notifications/announce", json=data, headers=auth_headers(employee_jwt))
    assert response.status_code == 403

def test_list_announcements_all_roles(base_url, superadmin_jwt, manager_jwt, employee_jwt, auth_headers):
    """Test that all roles can list announcements"""
    # Test with superadmin
    response = requests.get(f"{base_url}/api/notifications/list", headers=auth_headers(superadmin_jwt))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Test with manager
    response = requests.get(f"{base_url}/api/notifications/list", headers=auth_headers(manager_jwt))
    assert response.status_code == 200

    # Test with employee
    response = requests.get(f"{base_url}/api/notifications/list", headers=auth_headers(employee_jwt))
    assert response.status_code == 200
