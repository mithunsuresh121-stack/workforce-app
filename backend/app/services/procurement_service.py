import structlog
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.vendor import Vendor, VendorStatus
from app.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from app.models.inventory_item import InventoryItem, InventoryStatus
from app.schemas.procurement import VendorCreate, PurchaseOrderCreate, InventoryItemCreate, BidCreate
from app.services.redis_service import redis_service
import json
from app.crud_notifications import create_notification
from app.models.notification import NotificationType
from app.models.user import User

logger = structlog.get_logger(__name__)

class ProcurementService:
    @staticmethod
    def create_vendor(db: Session, vendor_data: VendorCreate, company_id: int) -> Vendor:
        vendor = Vendor(**vendor_data.model_dump(), company_id=company_id)
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        logger.info("Vendor created", vendor_id=vendor.id, company_id=company_id)
        return vendor

    @staticmethod
    def get_vendors(db: Session, company_id: int, status: Optional[str] = None) -> List[Vendor]:
        query = db.query(Vendor).filter(Vendor.company_id == company_id)
        if status:
            query = query.filter(Vendor.status == status)
        return query.all()

    @staticmethod
    def update_vendor(db: Session, vendor_id: int, company_id: int, vendor_data: VendorCreate) -> Optional[Vendor]:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.company_id == company_id).first()
        if not vendor:
            return None
        for key, value in vendor_data.model_dump().items():
            setattr(vendor, key, value)
        db.commit()
        db.refresh(vendor)
        logger.info("Vendor updated", vendor_id=vendor.id)
        return vendor

    @staticmethod
    def delete_vendor(db: Session, vendor_id: int, company_id: int) -> bool:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.company_id == company_id).first()
        if not vendor:
            return False
        db.delete(vendor)
        db.commit()
        logger.info("Vendor deleted", vendor_id=vendor_id)
        return True

    @staticmethod
    def create_purchase_order(db: Session, po_data: PurchaseOrderCreate, created_by: int, company_id: int) -> PurchaseOrder:
        po = PurchaseOrder(**po_data.model_dump(), created_by=created_by, company_id=company_id)
        db.add(po)
        db.commit()
        db.refresh(po)
        logger.info("Purchase order created", po_id=po.id, company_id=company_id)
        return po

    @staticmethod
    def get_purchase_orders(db: Session, company_id: int, status: Optional[str] = None) -> List[PurchaseOrder]:
        query = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id)
        if status:
            query = query.filter(PurchaseOrder.status == status)
        return query.all()

    @staticmethod
    def approve_purchase_order(db: Session, po_id: int, approver: User, company_id: int) -> Optional[PurchaseOrder]:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.company_id == company_id).first()
        if not po or po.status != PurchaseOrderStatus.PENDING:
            return None
        po.status = PurchaseOrderStatus.APPROVED
        po.approver_id = approver.id
        db.commit()
        db.refresh(po)
        # Create notification for creator
        create_notification(
            db=db,
            user_id=po.created_by,
            company_id=company_id,
            title="Purchase Order Approved",
            message=f"Your purchase order for {po.item_name} has been approved.",
            type=NotificationType.TASK_ASSIGNED  # Reuse existing type
        )
        logger.info("Purchase order approved", po_id=po.id, approver_id=approver.id)
        return po

    @staticmethod
    def reject_purchase_order(db: Session, po_id: int, approver: User, company_id: int) -> Optional[PurchaseOrder]:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.company_id == company_id).first()
        if not po or po.status != PurchaseOrderStatus.PENDING:
            return None
        po.status = PurchaseOrderStatus.REJECTED
        po.approver_id = approver.id
        db.commit()
        db.refresh(po)
        # Create notification for creator
        create_notification(
            db=db,
            user_id=po.created_by,
            company_id=company_id,
            title="Purchase Order Rejected",
            message=f"Your purchase order for {po.item_name} has been rejected.",
            type=NotificationType.TASK_ASSIGNED
        )
        logger.info("Purchase order rejected", po_id=po.id, approver_id=approver.id)
        return po

    @staticmethod
    def add_bid_to_purchase_order(db: Session, po_id: int, bid_data: BidCreate, company_id: int) -> Optional[PurchaseOrder]:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.company_id == company_id).first()
        if not po:
            return None
        bids = json.loads(po.bids) if po.bids else []
        bids.append(bid_data.model_dump())
        po.bids = json.dumps(bids)
        db.commit()
        db.refresh(po)
        logger.info("Bid added to purchase order", po_id=po.id, vendor_id=bid_data.vendor_id)
        return po

    @staticmethod
    async def get_inventory_items(db: Session, company_id: int, name: Optional[str] = None) -> List[InventoryItem]:
        # Check Redis cache first
        cache_key = f"inventory:{company_id}:{name or 'all'}"
        cached = await redis_service.get(cache_key)
        if cached:
            logger.info("Inventory cache hit", cache_key=cache_key)
            cached_items = json.loads(cached)
            return [InventoryItem(**item) for item in cached_items]

        query = db.query(InventoryItem).filter(InventoryItem.company_id == company_id)
        if name:
            query = query.filter(InventoryItem.name.ilike(f"%{name}%"))
        items = query.all()

        # Cache result
        item_dicts = []
        for item in items:
            item_dict = item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)  # Remove SQLAlchemy state
            # Convert datetime fields to ISO strings for JSON serialization
            if 'created_at' in item_dict and item_dict['created_at']:
                item_dict['created_at'] = item_dict['created_at'].isoformat()
            if 'updated_at' in item_dict and item_dict['updated_at']:
                item_dict['updated_at'] = item_dict['updated_at'].isoformat()
            if 'expiry_date' in item_dict and item_dict['expiry_date']:
                item_dict['expiry_date'] = item_dict['expiry_date'].isoformat()
            item_dicts.append(item_dict)
        await redis_service.setex(cache_key, 300, json.dumps(item_dicts))  # TTL 5 min
        logger.info("Inventory cached", cache_key=cache_key, count=len(items))
        return items

    @staticmethod
    async def create_inventory_item(db: Session, item_data: InventoryItemCreate, company_id: int) -> InventoryItem:
        item = InventoryItem(**item_data.model_dump(), company_id=company_id)
        db.add(item)
        db.commit()
        db.refresh(item)
        # Invalidate cache
        await redis_service.delete(f"inventory:{company_id}:all")
        if item_data.name:
            await redis_service.delete(f"inventory:{company_id}:{item_data.name}")
        logger.info("Inventory item created", item_id=item.id, company_id=company_id)
        return item

    @staticmethod
    async def update_inventory_item(db: Session, item_id: int, company_id: int, item_data: InventoryItemCreate) -> Optional[InventoryItem]:
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id, InventoryItem.company_id == company_id).first()
        if not item:
            return None
        for key, value in item_data.model_dump().items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        # Invalidate cache
        await redis_service.delete(f"inventory:{company_id}:all")
        await redis_service.delete(f"inventory:{company_id}:{item.name}")
        logger.info("Inventory item updated", item_id=item.id)
        return item

    @staticmethod
    async def delete_inventory_item(db: Session, item_id: int, company_id: int) -> bool:
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id, InventoryItem.company_id == company_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        # Invalidate cache
        await redis_service.delete(f"inventory:{company_id}:all")
        await redis_service.delete(f"inventory:{company_id}:{item.name}")
        logger.info("Inventory item deleted", item_id=item_id)
        return True
