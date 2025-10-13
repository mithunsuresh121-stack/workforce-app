from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models.chat import ChatMessage
from ..crud_chat import create_chat_message, get_chat_history, get_company_chat_messages, mark_message_as_read
from ..deps import get_current_user
from ..schemas.schemas import ChatMessageCreate, ChatMessageOut
from ..routers.ws_notifications import manager  # Import WebSocket manager

router = APIRouter()

@router.post("/send", response_model=ChatMessageOut)
async def send_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Ensure sender and receiver are in the same company
    if message.receiver_id:
        # Check if receiver exists and is in same company
        from ..models.user import User
        receiver = db.query(User).filter(
            User.id == message.receiver_id,
            User.company_id == current_user.company_id
        ).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found in your company")
    else:
        # Company-wide message, only admins can send
        if current_user.role not in ["SUPERADMIN", "COMPANYADMIN"]:
            raise HTTPException(status_code=403, detail="Only admins can send company-wide messages")

    chat_message = create_chat_message(db, message, current_user.id, current_user.company_id)

    # Broadcast to WebSocket
    notification_data = {
        "type": "new_message",
        "data": {
            "id": chat_message.id,
            "sender_id": chat_message.sender_id,
            "receiver_id": chat_message.receiver_id,
            "message": chat_message.message,
            "created_at": chat_message.created_at.isoformat()
        }
    }
    await manager.broadcast_to_company(current_user.company_id, notification_data)

    return chat_message

@router.get("/history/{user_id}", response_model=List[ChatMessageOut])
def get_message_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Ensure both users are in the same company
    other_user = db.query(ChatMessage).join(ChatMessage.sender).filter(
        ChatMessage.id == user_id,
        ChatMessage.company_id == current_user.company_id
    ).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found in your company")

    messages = get_chat_history(db, current_user.id, user_id, current_user.company_id)
    return messages

@router.get("/company", response_model=List[ChatMessageOut])
def get_company_messages(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Only admins can view company-wide messages
    if current_user.role not in ["SUPERADMIN", "COMPANYADMIN"]:
        raise HTTPException(status_code=403, detail="Only admins can view company messages")

    messages = get_company_chat_messages(db, current_user.company_id)
    return messages

async def get_current_user_from_token(token: str, db: Session):
    # Placeholder: implement JWT verification
    # For now, assume token is user_id
    from ..models.user import User
    user_id = int(token)  # Simplified
    user = db.query(User).filter(User.id == user_id).first()
    return user

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    # Authenticate user from token
    user = await get_current_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.company_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.company_id)
