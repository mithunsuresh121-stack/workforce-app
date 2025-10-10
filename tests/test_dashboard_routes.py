import pytest
import requests

def test_get_attendance_trend_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/attendance", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "date" in data[0] or "week" in data[0]
        assert "present" in data[0]
        assert "absent" in data[0]


def test_get_leave_utilization_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/leaves", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "utilization_pct" in data[0]


def test_get_overtime_data_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/overtime", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "department" in data[0]
        assert "total_overtime" in data[0]


def test_get_payroll_estimates_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/payroll", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    data = response.json()
    assert "total_estimated_payroll" in data
    assert "employees_count" in data


def test_export_attendance_csv_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/export/attendance", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=attendance_export_weekly.csv" in response.headers["content-disposition"]


def test_export_leaves_csv_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/export/leaves", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"


def test_export_overtime_csv_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/export/overtime", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"


def test_export_payroll_csv_manager(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/export/payroll", headers=auth_headers(manager_jwt))
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"


def test_dashboard_endpoints_employee_denied(base_url, employee_jwt, auth_headers):
    # Employee should be denied access
    response = requests.get(f"{base_url}/api/dashboard/attendance", headers=auth_headers(employee_jwt))
    assert response.status_code == 403

    response = requests.get(f"{base_url}/api/dashboard/leaves", headers=auth_headers(employee_jwt))
    assert response.status_code == 403

    response = requests.get(f"{base_url}/api/dashboard/overtime", headers=auth_headers(employee_jwt))
    assert response.status_code == 403

    response = requests.get(f"{base_url}/api/dashboard/payroll", headers=auth_headers(employee_jwt))
    assert response.status_code == 403

    response = requests.get(f"{base_url}/api/dashboard/export/attendance", headers=auth_headers(employee_jwt))
    assert response.status_code == 403


def test_export_invalid_type(base_url, manager_jwt, auth_headers):
    response = requests.get(f"{base_url}/api/dashboard/export/invalid", headers=auth_headers(manager_jwt))
    assert response.status_code == 400
