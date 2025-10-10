import pytest
from sqlalchemy.orm import Session
from app import models, crud
from app.schemas.swap_request import SwapRequestCreate

def test_shift_swap_approval_creates_notification(db_session: Session, client, manager_user, employee_user):
    # Create a pending swap request as employee
    swap_data = SwapRequestCreate(
        target_employee_id=manager_user.id,  # Assuming manager has shifts
        requester_shift_id=1,  # Assume shift exists
        target_shift_id=2
    )
    # Assuming endpoint exists, but for test, create directly
    swap = models.SwapRequest(
        requester_id=employee_user.id,
        target_employee_id=manager_user.id,
        requester_shift_id=1,
        target_shift_id=2,
        status="PENDING",
        company_id=employee_user.company_id
    )
    db_session.add(swap)
    db_session.commit()
    db_session.refresh(swap)

    # Approve as manager
    response = client.post(f"/shifts/swap-approve/{swap.id}", headers={"Authorization": f"Bearer {manager_user.token}"})
    assert response.status_code == 200

    # Check swap status
    db_session.refresh(swap)
    assert swap.status == "APPROVED"

    # Check notification created
    notification = db_session.query(models.Notification).filter(
        models.Notification.user_id == employee_user.id,
        models.Notification.type == "SHIFT_SWAP_APPROVED"
    ).first()
    assert notification is not None
    assert "approved" in notification.message.lower()

def test_shift_swap_rejection_creates_notification(db_session: Session, client, manager_user, employee_user):
    # Similar to above, but reject
    swap = models.SwapRequest(
        requester_id=employee_user.id,
        target_employee_id=manager_user.id,
        requester_shift_id=1,
        target_shift_id=2,
        status="PENDING",
        company_id=employee_user.company_id
    )
    db_session.add(swap)
    db_session.commit()
    db_session.refresh(swap)

    response = client.post(f"/shifts/swap-reject/{swap.id}", headers={"Authorization": f"Bearer {manager_user.token}"})
    assert response.status_code == 200

    db_session.refresh(swap)
    assert swap.status == "REJECTED"

    notification = db_session.query(models.Notification).filter(
        models.Notification.user_id == employee_user.id,
        models.Notification.type == "SHIFT_SWAP_REJECTED"
    ).first()
    assert notification is not None
    assert "rejected" in notification.message.lower()

def test_shift_swap_approval_forbidden_for_employee(db_session: Session, client, employee_user):
    # Create swap
    swap = models.SwapRequest(
        requester_id=employee_user.id,
        target_employee_id=employee_user.id,  # Self
        requester_shift_id=1,
        target_shift_id=2,
        status="PENDING",
        company_id=employee_user.company_id
    )
    db_session.add(swap)
    db_session.commit()
    db_session.refresh(swap)

    response = client.post(f"/shifts/swap-approve/{swap.id}", headers={"Authorization": f"Bearer {employee_user.token}"})
    assert response.status_code == 403

def test_get_shift_swaps_for_manager(db_session: Session, client, manager_user, employee_user):
    # Create swap
    swap = models.SwapRequest(
        requester_id=employee_user.id,
        target_employee_id=manager_user.id,
        requester_shift_id=1,
        target_shift_id=2,
        status="PENDING",
        company_id=manager_user.company_id
    )
    db_session.add(swap)
    db_session.commit()

    response = client.get("/shifts/swaps?status=PENDING", headers={"Authorization": f"Bearer {manager_user.token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s['id'] == swap.id for s in data)
