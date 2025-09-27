#!/usr/bin/env python3
"""
Test script for permissions system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.permissions import has_permission, PERMISSIONS_MAP
from app.models.user import Role

def test_permissions():
    print("=== Testing Permissions System ===\n")

    # Test permissions map
    print("Permissions Map:")
    for role, perms in PERMISSIONS_MAP.items():
        print(f"  {role.value}: {len(perms)} permissions")
    print()

    # Mock users
    class MockUser:
        def __init__(self, role):
            self.role = role

    employee = MockUser(Role.EMPLOYEE)
    manager = MockUser(Role.MANAGER)
    admin = MockUser(Role.COMPANYADMIN)
    superadmin = MockUser(Role.SUPERADMIN)

    # Test cases
    tests = [
        ("Employee can clock in", employee, "attendance.create", True),
        ("Manager can approve leave", manager, "leave.approve", True),
        ("Admin can create users", admin, "user.create", True),
        ("SuperAdmin has full access", superadmin, "admin.full_access", True),
        ("Employee cannot create users", employee, "user.create", False),
        ("Employee cannot approve leave", employee, "leave.approve", False),
        ("Manager cannot delete users", manager, "user.delete", False),
    ]

    print("Permission Tests:")
    all_passed = True
    for desc, user, perm, expected in tests:
        result = has_permission(user, perm)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {desc}: {result} (expected {expected})")
        if result != expected:
            all_passed = False

    print()
    if all_passed:
        print("✓ All permission tests passed!")
        return True
    else:
        print("✗ Some permission tests failed!")
        return False

if __name__ == "__main__":
    success = test_permissions()
    sys.exit(0 if success else 1)
