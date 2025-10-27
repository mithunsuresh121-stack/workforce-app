import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from ..deps import get_db, get_current_user
from ..schemas import TaskCreate, TaskOut, AttachmentOut
from ..crud import list_tasks, create_task, get_task_by_id, update_task, delete_task, create_attachment, delete_attachment, list_attachments_by_task
from ..crud_notifications import create_notification
from ..models.user import User
from ..models.task import Task, TaskStatus, TaskPriority
from ..models.attachment import Attachment
from ..models.notification import NotificationType
import os
import shutil
from datetime import datetime

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskOut])
def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by task priority"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all tasks for the current user's company with optional filters
    """
    from sqlalchemy import and_
    query = db.query(Task).filter(Task.company_id == current_user.company_id)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    tasks = query.all()
    return tasks

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def add_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task for the current user's company
    Only managers can assign tasks to others
    """
    # Ensure the task is created for the user's company (SuperAdmin can create for any company)
    if current_user.role != "SuperAdmin" and payload.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create task for another company"
        )

    # Role-based permissions: Only managers can assign tasks to others
    if payload.assignee_id and current_user.role not in ["Manager", "CompanyAdmin", "SuperAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can assign tasks to others"
        )

    # Set assigned_by to current user if not provided
    assigned_by = payload.assigned_by or current_user.id

    # Fix: Ensure company_id is set to current_user.company_id if not provided or invalid
    company_id = payload.company_id if payload.company_id else current_user.company_id

    try:
        # Ensure status is properly converted to enum value
        if isinstance(payload.status, str):
            # If it's a string, try to match it to an enum value
            status_value = payload.status
        else:
            # If it's an enum, get its value
            status_value = payload.status.value

        task = create_task(
            db=db,
            assigning_user=current_user,
            title=payload.title,
            description=payload.description or "",
            status=status_value,
            priority=payload.priority or "Medium",
            due_at=payload.due_at,
            assignee_id=payload.assignee_id,
            company_id=company_id  # Pass fixed company_id explicitly to create_task
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

    # Create notification for task assignment (respects user preferences)
    if payload.assignee_id:
        assignee = db.query(User).filter(User.id == payload.assignee_id).first()
        if assignee:
            notification = create_notification(
                db=db,
                user_id=payload.assignee_id,
                company_id=company_id,  # Use the fixed company_id variable
                title="New Task Assigned",
                message=f"You have been assigned a new task: {payload.title}",
                type=NotificationType.TASK_ASSIGNED
            )
            # Notification creation is handled silently - if user disabled this type, no notification is created

    return task

@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID
    """
    task = get_task_by_id(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskOut)
def update_task_endpoint(
    task_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task
    Managers can update any task, employees can only update their own tasks
    """
    task = get_task_by_id(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Role-based permissions
    if current_user.role not in ["Manager", "CompanyAdmin", "SuperAdmin"]:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own tasks"
            )

    # Only managers can change assignee
    if payload.assignee_id and current_user.role not in ["Manager", "CompanyAdmin", "SuperAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can reassign tasks"
        )

    updated_task = update_task(
        db=db,
        updating_user=current_user,
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_at=payload.due_at,
        assignee_id=payload.assignee_id
    )
    return updated_task

@router.delete("/{task_id}")
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task
    Only managers can delete tasks
    """
    task = get_task_by_id(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Only managers can delete tasks
    if current_user.role not in ["Manager", "CompanyAdmin", "SuperAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can delete tasks"
        )

    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )

    return {"message": "Task deleted successfully"}
