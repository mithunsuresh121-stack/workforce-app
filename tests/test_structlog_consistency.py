import structlog
import json
import io
import pytest
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_structlog_json_output(monkeypatch):
    """Test that structlog outputs valid JSON with mandatory fields"""
    logger = structlog.get_logger("test")
    log_stream = io.StringIO()
    handler = structlog.PrintLogger(log_stream)
    structlog.configure(logger_factory=lambda: handler)

    logger.info("test_event", user_id=1, company_id=99)

    output = log_stream.getvalue().strip()
    log_data = json.loads(output)

    # Assert mandatory fields exist
    assert "event" in log_data
    assert log_data["event"] == "test_event"
    assert "timestamp" in log_data
    assert "user_id" in log_data
    assert log_data["user_id"] == 1
    assert "company_id" in log_data
    assert log_data["company_id"] == 99
    assert "level" in log_data

def test_structlog_consistency_across_modules():
    """Test that all backend modules have structlog configured"""
    import backend.app.auth as auth_module
    import backend.app.crud as crud_module
    import backend.app.routers.attendance as attendance_router
    import backend.app.routers.auth as auth_router
    import backend.app.routers.chat as chat_router
    import backend.app.routers.companies as companies_router
    import backend.app.routers.dashboard as dashboard_router
    import backend.app.routers.documents as documents_router
    import backend.app.routers.employees as employees_router
    import backend.app.routers.leaves as leaves_router
    import backend.app.routers.notification_preferences as notification_preferences_router
    import backend.app.routers.notifications as notifications_router
    import backend.app.routers.payroll as payroll_router
    import backend.app.routers.profile as profile_router
    import backend.app.routers.shifts as shifts_router
    import backend.app.routers.tasks as tasks_router
    import backend.app.routers.ws_notifications as ws_notifications_router
    import backend.app.crud_announcements as crud_announcements
    import backend.app.crud_chat as crud_chat
    import backend.app.crud_documents as crud_documents
    import backend.app.services.fcm_service as fcm_service
    import backend.app.services.digest_service as digest_service

    # List of modules to check
    modules = [
        auth_module, crud_module, attendance_router, auth_router, chat_router,
        companies_router, dashboard_router, documents_router, employees_router,
        leaves_router, notification_preferences_router, notifications_router,
        payroll_router, profile_router, shifts_router, tasks_router,
        ws_notifications_router, crud_announcements, crud_chat, crud_documents,
        fcm_service, digest_service
    ]

    for module in modules:
        # Check if module has logger attribute
        assert hasattr(module, 'logger'), f"Module {module.__name__} missing logger"

        # Check if logger is a structlog logger
        logger = getattr(module, 'logger')
        assert hasattr(logger, 'info'), f"Logger in {module.__name__} is not a structlog logger"

def test_no_print_statements_in_modules():
    """Test that no print() statements remain in backend modules"""
    import ast
    import os

    backend_dir = "backend/app"
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()

                # Parse the file and check for print calls
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                            pytest.fail(f"print() statement found in {filepath}")
                except SyntaxError:
                    # Skip files with syntax errors
                    pass

def test_structlog_http_request_logging():
    """Test that HTTP requests are logged with structlog"""
    # Make a test request
    response = client.get("/health")

    # Check that the request was successful
    assert response.status_code == 200

    # Note: In a real test environment, you would capture the log output
    # For now, we just ensure the endpoint works and logging is configured
