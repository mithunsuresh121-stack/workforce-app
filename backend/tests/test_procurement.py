import pytest
from sqlalchemy.orm import Session
from app.models.vendor import Vendor, VendorStatus
from app.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from app.models.inventory_item import InventoryItem, InventoryStatus
from app.schemas.procurement import VendorCreate, PurchaseOrderCreate, InventoryItemCreate, BidCreate
from app.services.procurement_service import ProcurementService
from app.models.user import User, UserRole
from app.models.company import Company
from app.services.redis_service import redis_service
import json
from unittest.mock import AsyncMock, patch

@pytest.fixture
def test_company(db: Session):
    company = Company(name="Test Company")
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@pytest.fixture
def test_admin_user(db: Session, test_company: Company):
    user = User(
        email="admin@test.com",
        hashed_password="hashed",
        full_name="Admin User",
        role=UserRole.COMPANY_ADMIN,
        company_id=test_company.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_employee_user(db: Session, test_company: Company):
    user = User(
        email="employee@test.com",
        hashed_password="hashed",
        full_name="Employee User",
        role=UserRole.EMPLOYEE,
        company_id=test_company.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

class TestProcurementService:
    def test_create_vendor(self, db: Session, test_company: Company):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com", phone="123-456-7890")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        assert vendor.name == "Test Vendor"
        assert vendor.contact_email == "vendor@test.com"
        assert vendor.company_id == test_company.id
        assert vendor.status == VendorStatus.ACTIVE

    def test_get_vendors(self, db: Session, test_company: Company):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        ProcurementService.create_vendor(db, vendor_data, test_company.id)
        vendors = ProcurementService.get_vendors(db, test_company.id)
        assert len(vendors) == 1
        assert vendors[0].name == "Test Vendor"

    def test_update_vendor(self, db: Session, test_company: Company):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        updated_data = VendorCreate(name="Updated Vendor", contact_email="updated@test.com")
        updated = ProcurementService.update_vendor(db, vendor.id, test_company.id, updated_data)
        assert updated.name == "Updated Vendor"
        assert updated.contact_email == "updated@test.com"

    def test_delete_vendor(self, db: Session, test_company: Company):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        success = ProcurementService.delete_vendor(db, vendor.id, test_company.id)
        assert success
        vendors = ProcurementService.get_vendors(db, test_company.id)
        assert len(vendors) == 0

    def test_create_purchase_order(self, db: Session, test_company: Company, test_employee_user: User):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        po_data = PurchaseOrderCreate(vendor_id=vendor.id, item_name="Test Item", quantity=10, amount=100.0)
        po = ProcurementService.create_purchase_order(db, po_data, test_employee_user.id, test_company.id)
        assert po.item_name == "Test Item"
        assert po.vendor_id == vendor.id
        assert po.created_by == test_employee_user.id
        assert po.status == PurchaseOrderStatus.PENDING

    def test_get_purchase_orders(self, db: Session, test_company: Company, test_employee_user: User):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        po_data = PurchaseOrderCreate(vendor_id=vendor.id, item_name="Test Item", quantity=10, amount=100.0)
        ProcurementService.create_purchase_order(db, po_data, test_employee_user.id, test_company.id)
        pos = ProcurementService.get_purchase_orders(db, test_company.id)
        assert len(pos) == 1
        assert pos[0].item_name == "Test Item"

    def test_approve_purchase_order(self, db: Session, test_company: Company, test_employee_user: User, test_admin_user: User):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        po_data = PurchaseOrderCreate(vendor_id=vendor.id, item_name="Test Item", quantity=10, amount=100.0)
        po = ProcurementService.create_purchase_order(db, po_data, test_employee_user.id, test_company.id)
        approved = ProcurementService.approve_purchase_order(db, po.id, test_admin_user, test_company.id)
        assert approved.status == PurchaseOrderStatus.APPROVED
        assert approved.approver_id == test_admin_user.id

    def test_reject_purchase_order(self, db: Session, test_company: Company, test_employee_user: User, test_admin_user: User):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        po_data = PurchaseOrderCreate(vendor_id=vendor.id, item_name="Test Item", quantity=10, amount=100.0)
        po = ProcurementService.create_purchase_order(db, po_data, test_employee_user.id, test_company.id)
        rejected = ProcurementService.reject_purchase_order(db, po.id, test_admin_user, test_company.id)
        assert rejected.status == PurchaseOrderStatus.REJECTED
        assert rejected.approver_id == test_admin_user.id

    def test_add_bid_to_purchase_order(self, db: Session, test_company: Company, test_employee_user: User):
        vendor_data = VendorCreate(name="Test Vendor", contact_email="vendor@test.com")
        vendor = ProcurementService.create_vendor(db, vendor_data, test_company.id)
        po_data = PurchaseOrderCreate(vendor_id=vendor.id, item_name="Test Item", quantity=10, amount=100.0)
        po = ProcurementService.create_purchase_order(db, po_data, test_employee_user.id, test_company.id)
        bid_data = BidCreate(vendor_id=vendor.id, amount=90.0, notes="Discount offer")
        updated = ProcurementService.add_bid_to_purchase_order(db, po.id, bid_data, test_company.id)
        bids = json.loads(updated.bids)
        assert len(bids) == 1
        assert bids[0]["amount"] == 90.0

    @pytest.mark.asyncio
    async def test_get_inventory_items_cache_miss(self, db: Session, test_company: Company):
        # Mock Redis to simulate cache miss
        with patch.object(redis_service, 'get', return_value=None) as mock_get, \
             patch.object(redis_service, 'setex') as mock_setex:
            item_data = InventoryItemCreate(name="Test Item", quantity=100, unit_price=10.0)
            await ProcurementService.create_inventory_item(db, item_data, test_company.id)
            items = await ProcurementService.get_inventory_items(db, test_company.id)
            assert len(items) == 1
            assert items[0].name == "Test Item"
            mock_get.assert_called()
            mock_setex.assert_called()

    @pytest.mark.asyncio
    async def test_get_inventory_items_cache_hit(self, db: Session, test_company: Company):
        # Mock Redis to simulate cache hit
        cached_data = [{"name": "Cached Item", "quantity": 50, "unit_price": 5.0, "status": "in_stock"}]
        with patch.object(redis_service, 'get', return_value=json.dumps(cached_data)) as mock_get:
            items = await ProcurementService.get_inventory_items(db, test_company.id)
            assert len(items) == 1
            assert items[0].name == "Cached Item"
            mock_get.assert_called()

    @pytest.mark.asyncio
    async def test_create_inventory_item(self, db: Session, test_company: Company):
        item_data = InventoryItemCreate(name="Test Item", quantity=100, unit_price=10.0)
        item = await ProcurementService.create_inventory_item(db, item_data, test_company.id)
        assert item.name == "Test Item"
        assert item.quantity == 100
        assert item.company_id == test_company.id

    @pytest.mark.asyncio
    async def test_update_inventory_item(self, db: Session, test_company: Company):
        item_data = InventoryItemCreate(name="Test Item", quantity=100, unit_price=10.0)
        item = await ProcurementService.create_inventory_item(db, item_data, test_company.id)
        updated_data = InventoryItemCreate(name="Updated Item", quantity=200, unit_price=15.0)
        updated = await ProcurementService.update_inventory_item(db, item.id, test_company.id, updated_data)
        assert updated.name == "Updated Item"
        assert updated.quantity == 200

    @pytest.mark.asyncio
    async def test_delete_inventory_item(self, db: Session, test_company: Company):
        item_data = InventoryItemCreate(name="Test Item", quantity=100, unit_price=10.0)
        item = await ProcurementService.create_inventory_item(db, item_data, test_company.id)
        success = await ProcurementService.delete_inventory_item(db, item.id, test_company.id)
        assert success
        items = await ProcurementService.get_inventory_items(db, test_company.id)
        assert len(items) == 0
