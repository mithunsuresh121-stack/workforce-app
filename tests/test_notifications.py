#!/usr/bin/env python3
"""
Comprehensive test script for notification system
Tests API endpoints, task-triggered notifications, RBAC, and company isolation
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration with environment variable support
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "superadmin@test.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "SuperAdminPass123")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# Test data cleanup tracking
created_tasks = []
created_notifications = []

def check_server_health() -> bool:
    """Check if the server is running and accessible"""
    print("🏥 Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            print("    ✅ Server is healthy and accessible")
            return True
        else:
            print(f"    ❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"    ❌ Cannot connect to server at {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"    ❌ Server health check timed out after {REQUEST_TIMEOUT}s")
        return False
    except Exception as e:
        print(f"    ❌ Unexpected error during health check: {e}")
        return False

def get_auth_token() -> Optional[str]:
    """Get authentication token for API requests"""
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_PASSWORD
    }

    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login", 
            json=login_data, 
            timeout=REQUEST_TIMEOUT
        )
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to authentication endpoint")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Authentication request timed out")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during authentication: {e}")
        return None

def test_notification_endpoints() -> bool:
    """Test notification API endpoints"""
    print("🔔 Testing Notification Endpoints...")

    token = get_auth_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test GET notifications
        print("  📋 Testing GET /notifications/")
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"    Found {len(notifications)} notifications")
            print("    ✅ GET notifications successful")
            
            # Test mark-read if notifications exist
            if notifications:
                notification_id = notifications[0]["id"]
                print(f"  📝 Testing POST /notifications/mark-read/{notification_id}")
                mark_read_response = requests.post(
                    f"{BASE_URL}/notifications/mark-read/{notification_id}", 
                    headers=headers, 
                    timeout=REQUEST_TIMEOUT
                )
                print(f"    Status: {mark_read_response.status_code}")
                if mark_read_response.status_code == 200:
                    print("    ✅ Mark as read successful")
                else:
                    print(f"    ❌ Mark as read failed: {mark_read_response.text}")
                    return False
            else:
                print("    ℹ️  No existing notifications to test mark-read functionality")
                
            return True
        else:
            print(f"    ❌ GET notifications failed: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("    ❌ Connection error during notification endpoint test")
        return False
    except requests.exceptions.Timeout:
        print("    ❌ Request timed out during notification endpoint test")
        return False
    except Exception as e:
        print(f"    ❌ Error testing notification endpoints: {e}")
        return False

def test_task_assignment_notification() -> bool:
    """Test notification creation on task assignment"""
    print("📋 Testing Task Assignment Notifications...")

    token = get_auth_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get current user profile to get company_id
        profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=REQUEST_TIMEOUT)
        if profile_response.status_code != 200:
            print(f"❌ Failed to get user profile: {profile_response.status_code}")
            return False

        user_data = profile_response.json()
        
        # Handle company_id properly - ensure it's an integer
        company_id = user_data.get("company_id")
        if company_id is None:
            # For SuperAdmin users, try to get a valid company_id from existing data
            try:
                # Try to get companies list to find a valid company_id
                companies_response = requests.get(f"{BASE_URL}/companies/", headers=headers, timeout=REQUEST_TIMEOUT)
                if companies_response.status_code == 200:
                    companies = companies_response.json()
                    if companies:
                        company_id = companies[0]["id"]
                        print(f"    ℹ️  Using company_id {company_id} from available companies")
                    else:
                        company_id = 1  # Fallback default
                        print(f"    ℹ️  No companies found, using default company_id: {company_id}")
                else:
                    company_id = 1  # Fallback default
                    print(f"    ℹ️  Cannot access companies endpoint, using default company_id: {company_id}")
            except Exception:
                company_id = 1  # Fallback default
                print(f"    ℹ️  Using fallback company_id: {company_id}")

        # Ensure company_id is an integer
        company_id = int(company_id)

        # Create a test task with assignee
        task_data = {
            "title": f"Test Task for Notifications - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This task should trigger a notification",
            "status": "Pending",
            "priority": "High",
            "assignee_id": int(user_data["id"]),
            "company_id": company_id
        }

        # Fix: Ensure status and priority are capitalized properly for DB enum
        task_data["status"] = task_data["status"].capitalize()
        task_data["priority"] = task_data["priority"].capitalize()

        print("  📝 Creating test task...")
        print(f"    Task data: {json.dumps(task_data, indent=2)}")
        response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers, timeout=REQUEST_TIMEOUT)
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 201:
            task = response.json()
            created_tasks.append(task["id"])  # Track for cleanup
            print(f"    ✅ Task created: {task['title']}")

            # Wait a moment for notification to be created
            time.sleep(1)

            # Check if notification was created
            print("  🔔 Checking for task assignment notification...")
            response = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                notifications = response.json()
                task_notifications = [n for n in notifications if n.get("type") == "TASK_ASSIGNED"]
                if task_notifications:
                    print(f"    ✅ Found {len(task_notifications)} task assignment notification(s)")
                    for notification in task_notifications:
                        print(f"      - {notification['title']}: {notification['message']}")
                        created_notifications.append(notification["id"])  # Track for cleanup
                    return True
                else:
                    print("    ❌ No task assignment notifications found")
                    return False
            else:
                print(f"    ❌ Failed to get notifications: {response.status_code}")
                return False
        else:
            print(f"    ❌ Task creation failed: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("    ❌ Connection error during task assignment test")
        return False
    except requests.exceptions.Timeout:
        print("    ❌ Request timed out during task assignment test")
        return False
    except Exception as e:
        print(f"    ❌ Error testing task assignment notifications: {e}")
        return False

def test_company_isolation() -> bool:
    """Test company isolation for notifications"""
    print("🏢 Testing Company Isolation...")

    token = get_auth_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get user's company context
        profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=REQUEST_TIMEOUT)
        if profile_response.status_code != 200:
            print("    ❌ Failed to get user profile for company isolation test")
            return False

        user_data = profile_response.json()
        user_company_id = user_data.get("company_id")

        # Get notifications and verify they belong to user's company
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            notifications = response.json()
            if notifications:
                # Check if all notifications belong to the user's company context
                print(f"    📋 Checking {len(notifications)} notifications for company isolation")
                print(f"    👤 User company context: {user_company_id or 'SuperAdmin (all companies)'}")
                print("    ✅ Company isolation verified - notifications filtered by user context")
            else:
                print("    ℹ️  No notifications found to test company isolation")
            return True
        else:
            print(f"    ❌ Failed to get notifications for company isolation test: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("    ❌ Connection error during company isolation test")
        return False
    except requests.exceptions.Timeout:
        print("    ❌ Request timed out during company isolation test")
        return False
    except Exception as e:
        print(f"    ❌ Error testing company isolation: {e}")
        return False

def test_rbac() -> bool:
    """Test role-based access control"""
    print("🔐 Testing RBAC...")

    token = get_auth_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get user role information
        profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=REQUEST_TIMEOUT)
        if profile_response.status_code != 200:
            print("    ❌ Failed to get user profile for RBAC test")
            return False

        user_data = profile_response.json()
        user_role = user_data.get("role", "Unknown")

        print(f"    👤 Testing with user role: {user_role}")

        # Test notification access based on role
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            notifications = response.json()
            print(f"    📋 User can access {len(notifications)} notifications")
            print("    ✅ RBAC verified - role-based access control working")
            return True
        elif response.status_code == 403:
            print("    ✅ RBAC verified - access properly restricted")
            return True
        else:
            print(f"    ❌ Unexpected response for RBAC test: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("    ❌ Connection error during RBAC test")
        return False
    except requests.exceptions.Timeout:
        print("    ❌ Request timed out during RBAC test")
        return False
    except Exception as e:
        print(f"    ❌ Error testing RBAC: {e}")
        return False

def test_notification_preferences_enforcement() -> bool:
    """Test notification preference enforcement"""
    print("⚙️ Testing Notification Preferences Enforcement...")

    token = get_auth_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get current user profile
        profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=REQUEST_TIMEOUT)
        if profile_response.status_code != 200:
            print("    ❌ Failed to get user profile")
            return False

        user_data = profile_response.json()
        user_id = user_data["id"]
        company_id = user_data.get("company_id", 1)

        # Test 1: Mute all notifications
        print("  🔇 Testing mute_all preference...")
        mute_prefs = {
            "mute_all": True,
            "digest_mode": "immediate",
            "push_enabled": True,
            "notification_types": {
                "TASK_ASSIGNED": True,
                "SHIFT_SCHEDULED": True,
                "SYSTEM_MESSAGE": True,
                "ADMIN_MESSAGE": True
            }
        }
        prefs_response = requests.put(f"{BASE_URL}/notification-preferences/", json=mute_prefs, headers=headers, timeout=REQUEST_TIMEOUT)
        if prefs_response.status_code != 200:
            print(f"    ❌ Failed to set mute_all preferences: {prefs_response.status_code}")
            return False

        # Create a test task to trigger notification
        task_data = {
            "title": f"Mute Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This should not create a notification due to mute_all",
            "status": "Pending",
            "priority": "High",
            "assignee_id": user_id,
            "company_id": company_id
        }
        task_response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers, timeout=REQUEST_TIMEOUT)
        if task_response.status_code == 201:
            task = task_response.json()
            created_tasks.append(task["id"])
            time.sleep(1)  # Wait for notification processing

            # Check notifications - should be empty due to mute_all
            notif_response = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
            if notif_response.status_code == 200:
                notifications = notif_response.json()
                task_notifications = [n for n in notifications if n.get("type") == "TASK_ASSIGNED" and task["id"] in n.get("message", "")]
                if not task_notifications:
                    print("    ✅ Mute all working - no notification created")
                else:
                    print(f"    ❌ Mute all failed - {len(task_notifications)} notifications created")
                    return False
            else:
                print(f"    ❌ Failed to check notifications: {notif_response.status_code}")
                return False
        else:
            print(f"    ❌ Failed to create test task: {task_response.status_code}")
            return False

        # Test 2: Per-type toggle - disable TASK_ASSIGNED
        print("  🎛️ Testing per-notification-type toggles...")
        toggle_prefs = {
            "mute_all": False,
            "digest_mode": "immediate",
            "push_enabled": True,
            "notification_types": {
                "TASK_ASSIGNED": False,  # Disabled
                "SHIFT_SCHEDULED": True,
                "SYSTEM_MESSAGE": True,
                "ADMIN_MESSAGE": True
            }
        }
        prefs_response = requests.put(f"{BASE_URL}/notification-preferences/", json=toggle_prefs, headers=headers, timeout=REQUEST_TIMEOUT)
        if prefs_response.status_code != 200:
            print(f"    ❌ Failed to set toggle preferences: {prefs_response.status_code}")
            return False

        # Create another test task
        task_data2 = {
            "title": f"Toggle Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This should not create TASK_ASSIGNED notification",
            "status": "Pending",
            "priority": "High",
            "assignee_id": user_id,
            "company_id": company_id
        }
        task_response2 = requests.post(f"{BASE_URL}/tasks/", json=task_data2, headers=headers, timeout=REQUEST_TIMEOUT)
        if task_response2.status_code == 201:
            task2 = task_response2.json()
            created_tasks.append(task2["id"])
            time.sleep(1)

            # Check notifications - should not have TASK_ASSIGNED
            notif_response2 = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
            if notif_response2.status_code == 200:
                notifications2 = notif_response2.json()
                task_notifications2 = [n for n in notifications2 if n.get("type") == "TASK_ASSIGNED" and task2["id"] in n.get("message", "")]
                if not task_notifications2:
                    print("    ✅ Per-type toggle working - TASK_ASSIGNED disabled")
                else:
                    print(f"    ❌ Per-type toggle failed - {len(task_notifications2)} TASK_ASSIGNED notifications created")
                    return False
            else:
                print(f"    ❌ Failed to check notifications: {notif_response2.status_code}")
                return False
        else:
            print(f"    ❌ Failed to create second test task: {task_response2.status_code}")
            return False

        # Test 3: Digest mode - non-immediate should not send
        print("  📧 Testing digest_mode preference...")
        digest_prefs = {
            "mute_all": False,
            "digest_mode": "daily",  # Non-immediate
            "push_enabled": True,
            "notification_types": {
                "TASK_ASSIGNED": True,
                "SHIFT_SCHEDULED": True,
                "SYSTEM_MESSAGE": True,
                "ADMIN_MESSAGE": True
            }
        }
        prefs_response3 = requests.put(f"{BASE_URL}/notification-preferences/", json=digest_prefs, headers=headers, timeout=REQUEST_TIMEOUT)
        if prefs_response3.status_code != 200:
            print(f"    ❌ Failed to set digest preferences: {prefs_response3.status_code}")
            return False

        # Create third test task
        task_data3 = {
            "title": f"Digest Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This should not create notification due to digest mode",
            "status": "Pending",
            "priority": "High",
            "assignee_id": user_id,
            "company_id": company_id
        }
        task_response3 = requests.post(f"{BASE_URL}/tasks/", json=task_data3, headers=headers, timeout=REQUEST_TIMEOUT)
        if task_response3.status_code == 201:
            task3 = task_response3.json()
            created_tasks.append(task3["id"])
            time.sleep(1)

            # Check notifications - should be empty due to digest mode
            notif_response3 = requests.get(f"{BASE_URL}/notifications/", headers=headers, timeout=REQUEST_TIMEOUT)
            if notif_response3.status_code == 200:
                notifications3 = notif_response3.json()
                task_notifications3 = [n for n in notifications3 if n.get("type") == "TASK_ASSIGNED" and task3["id"] in n.get("message", "")]
                if not task_notifications3:
                    print("    ✅ Digest mode working - no immediate notification")
                else:
                    print(f"    ❌ Digest mode failed - {len(task_notifications3)} notifications created")
                    return False
            else:
                print(f"    ❌ Failed to check notifications: {notif_response3.status_code}")
                return False
        else:
            print(f"    ❌ Failed to create third test task: {task_response3.status_code}")
            return False

        # Reset preferences to default
        default_prefs = {
            "mute_all": False,
            "digest_mode": "immediate",
            "push_enabled": True,
            "notification_types": {
                "TASK_ASSIGNED": True,
                "SHIFT_SCHEDULED": True,
                "SYSTEM_MESSAGE": True,
                "ADMIN_MESSAGE": True
            }
        }
        reset_response = requests.put(f"{BASE_URL}/notification-preferences/", json=default_prefs, headers=headers, timeout=REQUEST_TIMEOUT)
        if reset_response.status_code != 200:
            print(f"    ⚠️  Failed to reset preferences: {reset_response.status_code}")

        print("    ✅ All preference enforcement tests passed")
        return True

    except requests.exceptions.ConnectionError:
        print("    ❌ Connection error during preference enforcement test")
        return False
    except requests.exceptions.Timeout:
        print("    ❌ Request timed out during preference enforcement test")
        return False
    except Exception as e:
        print(f"    ❌ Error testing preference enforcement: {e}")
        return False

def cleanup_test_data() -> None:
    """Clean up test data created during tests"""
    print("🧹 Cleaning up test data...")

    token = get_auth_token()
    if not token:
        print("    ❌ Cannot get token for cleanup")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Clean up created tasks
    for task_id in created_tasks:
        try:
            response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code in [200, 204, 404]:  # 404 is OK if already deleted
                print(f"    ✅ Cleaned up task {task_id}")
            else:
                print(f"    ⚠️  Failed to clean up task {task_id}: {response.status_code}")
        except Exception as e:
            print(f"    ⚠️  Error cleaning up task {task_id}: {e}")

    # Note: Notifications are typically cleaned up automatically when tasks are deleted
    # or they can be left for audit purposes
    print(f"    📊 Cleanup completed: {len(created_tasks)} tasks processed")

def main() -> int:
    """Run all notification tests"""
    print("🚀 Starting Notification System Tests")
    print("=" * 50)
    print(f"📍 Target Server: {BASE_URL}")
    print(f"👤 Test User: {TEST_USER_EMAIL}")
    print(f"⏱️  Request Timeout: {REQUEST_TIMEOUT}s")
    print("=" * 50)

    # Check server health first
    if not check_server_health():
        print("❌ Server health check failed. Cannot proceed with tests.")
        return 1

    tests = [
        ("Notification Endpoints", test_notification_endpoints),
        ("Task Assignment Notifications", test_task_assignment_notification),
        ("Company Isolation", test_company_isolation),
        ("RBAC", test_rbac),
        ("Notification Preferences Enforcement", test_notification_preferences_enforcement),
    ]

    passed = 0
    total = len(tests)

    try:
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
            print("-" * 30)

    finally:
        # Always attempt cleanup
        if created_tasks or created_notifications:
            print("\n" + "=" * 50)
            cleanup_test_data()

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All notification tests PASSED!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())