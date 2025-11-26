import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps import get_db, get_current_user
from app.schemas.procurement import (
    VendorCreate, VendorOut, PurchaseOrderCreate, PurchaseOrderOut,
    InventoryItemCreate, InventoryItemOut, BidCreate
)
from app.services.procurement_service import ProcurementService
from app.models.user import User
from app.models.company import Company
from app.services.audit_service import AuditService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/procurement", tags=["Procurement"])

# Vendor CRUD
@router.post("/vendors/", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProcurementService.create_vendor(db, vendor, current_user.company_id)

@router.get("/vendors/", response_model=List[VendorOut])
def get_vendors(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProcurementService.get_vendors(db, current_user.company_id, status)

@router.put("/vendors/{vendor_id}", response_model=VendorOut)
def update_vendor(
    vendor_id: int,
    vendor: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = ProcurementService.update_vendor(db, vendor_id, current_user.company_id, vendor)
    if not updated:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return updated

@router.delete("/vendors/{vendor_id}")
def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not ProcurementService.delete_vendor(db, vendor_id, current_user.company_id):
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted"}

# Purchase Order CRUD
@router.post("/purchase-orders/", response_model=PurchaseOrderOut, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    po: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProcurementService.create_purchase_order(db, po, current_user.id, current_user.company_id)

@router.get("/purchase-orders/", response_model=List[PurchaseOrderOut])
def get_purchase_orders(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProcurementService.get_purchase_orders(db, current_user.company_id, status)

@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderOut)
def get_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    po = ProcurementService.get_purchase_order(db, po_id, current_user.company_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po

@router.post("/purchase-orders/{po_id}/approve", response_model=PurchaseOrderOut)
def approve_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RBAC: Only Admin/Manager can approve
    if current_user.role not in ["COMPANY_ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Only admins can approve purchase orders")
    approved = ProcurementService.approve_purchase_order(db, po_id, current_user, current_user.company_id)
    if not approved:
        raise HTTPException(status_code=404, detail="Purchase order not found or not pending")
    # Audit log
    AuditService.log_admin_action(
        db=db,
        action="APPROVE_PO",
        user_id=current_user.id,
        company_id=current_user.company_id,
        details={"po_id": po_id}
    )
    return approved

@router.post("/purchase-orders/{po_id}/reject", response_model=PurchaseOrderOut)
def reject_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RBAC: Only Admin/Manager can reject
    if current_user.role not in ["COMPANY_ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Only admins can reject purchase orders")
    rejected = ProcurementService.reject_purchase_order(db, po_id, current_user, current_user.company_id)
    if not rejected:
        raise HTTPException(status_code=404, detail="Purchase order not found or not pending")
    # Audit log
    AuditService.log_admin_action(
        db=db,
        action="REJECT_PO",
        user_id=current_user.id,
        company_id=current_user.company_id,
        details={"po_id": po_id}
    )
    return rejected

@router.post("/purchase-orders/{po_id}/bid", response_model=PurchaseOrderOut)
def add_bid(
    po_id: int,
    bid: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RBAC: Only Admin/Manager can bid (simulate supplier bidding)
    if current_user.role not in ["COMPANY_ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Only admins can add bids")
    updated = ProcurementService.add_bid_to_purchase_order(db, po_id, bid, current_user.company_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return updated

# Inventory CRUD
@router.get("/inventory/", response_model=List[InventoryItemOut])
async def get_inventory(
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ProcurementService.get_inventory_items(db, current_user.company_id, name)

@router.post("/inventory/", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ProcurementService.create_inventory_item(db, item, current_user.company_id)

@router.put("/inventory/{item_id}", response_model=InventoryItemOut)
async def update_inventory_item(
    item_id: int,
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = await ProcurementService.update_inventory_item(db, item_id, current_user.company_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated

@router.delete("/inventory/{item_id}")
async def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not await ProcurementService.delete_inventory_item(db, item_id, current_user.company_id):
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Inventory item deleted"}
