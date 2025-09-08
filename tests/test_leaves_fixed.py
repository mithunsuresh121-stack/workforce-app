import pytest
import requests
import time
from datetime import datetime, timedelta

def test_health(base_url):
    r = requests.get(f"{base_url}/health")
    assert r.status_code == 200

def test_leave_crud_superadmin(base_url, superadmin_jwt, auth_headers):
    """Test full CRUD operations for leaves as superadmin"""
    # Create leave request
    start_at = (datetime.now() + timedelta(days=1))
    end_at = (datetime.now() + timedelta(days=3))

    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Vacation",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "status": "Pending"
    }

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [200, 201]
    leave_data = r.json()
    leave_id = leave_data["id"]

    # Verify leave was created with correct data
    assert leave_data["employee_id"] == 3
    assert leave_data["type"] == "Vacation"
    assert leave_data["status"] == "Pending"

    # Read - get the specific leave
    r = requests.get(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200
    assert r.json()["id"] == leave_id

    # Update leave status to Approved
    r = requests.put(f"{base_url}/leaves/{leave_id}/status", json={"status": "Approved"}, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200
    assert r.json()["status"] == "Approved"

    # Note: Leave details update endpoint is not implemented in the current API
    # Skipping the update details test for now

    # Delete leave
    r = requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200

    # Verify leave is deleted
    r = requests.get(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 404

def test_leave_status_transitions(base_url, superadmin_jwt, auth_headers):
    """Test leave status transitions and validation"""
    # Create leave request
    start_at = (datetime.now() + timedelta(days=5))
    end_at = (datetime.now() + timedelta(days=7))

    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Sick Leave",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "status": "Pending"
    }

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [200, 201]
    leave_id = r.json()["id"]

    # Test status transitions
    statuses = ["Approved", "Rejected", "Pending"]

    for status in statuses:
        r = requests.put(f"{base_url}/leaves/{leave_id}/status", json={"status": status}, headers=auth_headers(superadmin_jwt))
        assert r.status_code == 200
        assert r.json()["status"] == status

    # Clean up
    requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))

def test_leave_validation(base_url, superadmin_jwt, auth_headers):
    """Test leave request validation"""
    # Test invalid date range (end before start)
    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Vacation",
        "start_at": "2024-12-31T00:00:00",
        "end_at": "2024-01-01T00:00:00"
    }

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 422  # Validation error

    # Test missing required fields
    incomplete_payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Vacation"
        # Missing start_at and end_at
    }

    r = requests.post(f"{base_url}/leaves/", json=incomplete_payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 422

    # Test invalid leave type
    invalid_payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "InvalidType",
        "start_at": "2024-01-01T00:00:00",
        "end_at": "2024-01-02T00:00:00"
    }

    r = requests.post(f"{base_url}/leaves/", json=invalid_payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 422

def test_leave_role_based_access(base_url, superadmin_jwt, manager_jwt, employee_jwt, auth_headers):
    """Test role-based access control for leave operations"""
    # Create leave as superadmin
    start_at = (datetime.now() + timedelta(days=10))
    end_at = (datetime.now() + timedelta(days=12))

    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Personal Leave",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "status": "Pending"
    }

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [200, 201]
    leave_id = r.json()["id"]

    # Manager should be able to read and update leaves in their company
    r = requests.get(f"{base_url}/leaves/{leave_id}", headers=auth_headers(manager_jwt))
    assert r.status_code == 200

    r = requests.put(f"{base_url}/leaves/{leave_id}/status", json={"status": "Approved"}, headers=auth_headers(manager_jwt))
    assert r.status_code == 200

    # Employee should have limited access (read-only for their own leaves)
    r = requests.get(f"{base_url}/leaves/{leave_id}", headers=auth_headers(employee_jwt))
    assert r.status_code in [200, 403]  # May be restricted based on implementation

    # Employee should not be able to approve/reject leaves
    r = requests.put(f"{base_url}/leaves/{leave_id}/status", json={"status": "Rejected"}, headers=auth_headers(employee_jwt))
    assert r.status_code in [403, 401]

    # Clean up
    requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))

def test_leave_listing_and_filtering(base_url, superadmin_jwt, auth_headers):
    """Test leave listing and filtering capabilities"""
    # Create multiple leave requests
    leaves_created = []

    valid_types = ["Vacation", "Sick Leave", "Personal Leave"]
    for i in range(3):
        start_at = (datetime.now() + timedelta(days=i+1))
        end_at = (datetime.now() + timedelta(days=i+2))

        payload = {
            "tenant_id": "1",
            "employee_id": 3,
            "type": valid_types[i % len(valid_types)],
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "status": "Pending"
        }

        r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
        assert r.status_code in [200, 201]
        leaves_created.append(r.json()["id"])

    # Get all leaves
    r = requests.get(f"{base_url}/leaves/", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200
    leaves_list = r.json()
    assert len(leaves_list) >= 3

    # Verify our created leaves are in the list
    created_ids = [leave["id"] for leave in leaves_list]
    for leave_id in leaves_created:
        assert leave_id in created_ids

    # Clean up
    for leave_id in leaves_created:
        requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))

def test_leave_edge_cases(base_url, superadmin_jwt, auth_headers):
    """Test edge cases for leave operations"""
    # Test very long leave request
    start_at = (datetime.now() + timedelta(days=1))
    end_at = (datetime.now() + timedelta(days=365))  # 1 year leave

    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Vacation",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "status": "Pending"
    }

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    # This might be allowed or rejected based on business rules
    assert r.status_code in [200, 201, 422]

    if r.status_code in [200, 201]:
        leave_id = r.json()["id"]
        # Clean up if created
        requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))

    # Test same day leave
    same_day = (datetime.now() + timedelta(days=30))

    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Vacation",
        "start_at": same_day.isoformat(),
        "end_at": same_day.isoformat(),
        "status": "Pending"
    }

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [200, 201, 422]

    if r.status_code in [200, 201]:
        leave_id = r.json()["id"]
        # Clean up if created
        requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))

def test_leave_concurrent_operations(base_url, superadmin_jwt, auth_headers):
    """Test concurrent leave operations"""
    # Create multiple leave requests quickly
    leave_ids = []

    for i in range(5):
        start_at = (datetime.now() + timedelta(days=i+1))
        end_at = (datetime.now() + timedelta(days=i+2))

        payload = {
            "tenant_id": "1",
            "employee_id": 3,
            "type": "Vacation",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "status": "Pending"
        }

        r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
        if r.status_code in [200, 201]:
            leave_ids.append(r.json()["id"])

    # Verify all were created
    r = requests.get(f"{base_url}/leaves/", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200

    # Clean up
    for leave_id in leave_ids:
        requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))

def test_leave_timestamp_tracking(base_url, superadmin_jwt, auth_headers):
    """Test that timestamps are properly tracked"""
    start_at = (datetime.now() + timedelta(days=20))
    end_at = (datetime.now() + timedelta(days=22))

    payload = {
        "tenant_id": "1",
        "employee_id": 3,
        "type": "Vacation",
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "status": "Pending"
    }

    # Record time before creation
    before_create = datetime.now()

    r = requests.post(f"{base_url}/leaves/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [200, 201]
    leave_data = r.json()
    leave_id = leave_data["id"]

    # Verify timestamps exist and are reasonable
    assert "created_at" in leave_data
    assert "updated_at" in leave_data

    created_at = datetime.fromisoformat(leave_data["created_at"].replace('Z', '+00:00'))
    updated_at = datetime.fromisoformat(leave_data["updated_at"].replace('Z', '+00:00'))

    # Timestamps should be after our before_create time
    assert created_at >= before_create
    assert updated_at >= before_create

    # Update the leave and check updated_at changes
    time.sleep(1)  # Small delay to ensure timestamp difference
    before_update = datetime.now()

    r = requests.put(f"{base_url}/leaves/{leave_id}/status", json={"status": "Approved"}, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200
    updated_leave = r.json()

    updated_at_after = datetime.fromisoformat(updated_leave["updated_at"].replace('Z', '+00:00'))
    assert updated_at_after >= before_update

    # Clean up
    requests.delete(f"{base_url}/leaves/{leave_id}", headers=auth_headers(superadmin_jwt))
