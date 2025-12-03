import json

import httpx
import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.deps import get_current_user
from app.main import app
from app.models.company import Company
from app.models.inventory_item import InventoryItem
from app.models.purchase_order import PurchaseOrder
from app.models.user import User
from app.models.vendor import Vendor

client = TestClient(app)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    # Mock a user for testing
    user = User(
        id=1,
        email="demo@company.com",
        full_name="Demo User",
        role="COMPANY_ADMIN",
        company_id=1,
    )
    return user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Set up test data before running tests"""
    db = SessionLocal()
    try:
        # Create test company if not exists
        company = db.query(Company).filter_by(name="Demo Company").first()
        if not company:
            company = Company(name="Demo Company")
            db.add(company)
            db.commit()
            db.refresh(company)

        # Create test user if not exists
        user = db.query(User).filter_by(email="demo@company.com").first()
        if not user:
            hashed_password = pwd_context.hash("password123")
            user = User(
                email="demo@company.com",
                hashed_password=hashed_password,
                full_name="Demo User",
                role="EMPLOYEE",
                company_id=company.id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create test vendor if not exists
            vendor = (
                db.query(Vendor)
                .filter_by(name="Test Vendor", company_id=company.id)
                .first()
            )
            if not vendor:
                vendor = Vendor(
                    name="Test Vendor",
                    contact_email="vendor@test.com",
                    company_id=company.id,
                )
                db.add(vendor)
                db.commit()
                db.refresh(vendor)

        # Create test inventory item if not exists
        # inventory_item = db.query(InventoryItem).filter_by(name="Test Item", company_id=company.id).first()
        # if not inventory_item:
        #     inventory_item = InventoryItem(
        #         name="Test Item",
        #         quantity=100,
        #         unit_price=10.0,
        #         company_id=company.id
        #     )
        #     db.add(inventory_item)
        #     db.commit()
        #     db.refresh(inventory_item)

        # db.commit()
    finally:
        db.close()


class TestE2EFlows:
    """End-to-end tests for key flows: auth, notifications, procurement"""

    def test_auth_login_flow(self):
        """Test authentication login flow"""
        # Simulate login (in real E2E, this would use Playwright for browser login)
        response = client.post(
            "/api/auth/login",
            json={"email": "demo@company.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_notifications_flow(self):
        """Test notifications API flow with caching"""
        # Get notifications (should hit cache or DB)
        response = client.get("/api/notifications/?limit=10&offset=0")
        assert response.status_code == 200
        notifications = response.json()
        assert isinstance(notifications, list)

        # Mark one as read
        if notifications:
            notification_id = notifications[0]["id"]
            response = client.post(f"/api/notifications/mark-read/{notification_id}")
            assert response.status_code == 200
            assert response.json()["message"] == "Notification marked as read"

    def test_procurement_flow(self):
        """Test procurement CRUD flow"""
        # Clean up existing data
        from app.db import SessionLocal
        from app.models.vendor import Vendor

        db = SessionLocal()
        try:
            # Delete existing purchase orders and vendors for company 1
            db.query(PurchaseOrder).filter(PurchaseOrder.company_id == 1).delete()
            db.query(Vendor).filter(Vendor.company_id == 1).delete()
            db.commit()
        finally:
            db.close()

        # Create a vendor first
        db = SessionLocal()
        vendor = Vendor(
            name="Test Vendor", contact_email="vendor@test.com", company_id=1
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        vendor_id = vendor.id
        db.close()

        # Create a purchase order (mock data)
        response = client.post(
            "/api/procurement/purchase-orders/",
            json={
                "vendor_id": vendor_id,
                "item_name": "Test Item",
                "quantity": 10,
                "amount": 100.0,
            },
        )
        assert response.status_code == 201
        po_data = response.json()
        po_id = po_data["id"]

        # Get the purchase order
        response = client.get(f"/api/procurement/purchase-orders/{po_id}")
        assert response.status_code == 200
        assert response.json()["id"] == po_id

        # Update status (approve)
        response = client.post(f"/api/procurement/purchase-orders/{po_id}/approve")
        assert response.status_code == 200

        # List purchase orders
        response = client.get("/api/procurement/purchase-orders/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
