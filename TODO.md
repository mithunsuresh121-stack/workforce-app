# TODO: Lark-Style Messenger & Meetings Integration for Workforce App

## Backend (FastAPI + PostgreSQL)
### DB Models & Migrations
- [ ] Edit `backend/app/models/chat.py`: Add attachments (JSONB for file URLs), reactions (relationship to new MessageReaction model)
- [ ] Create `backend/app/models/channels.py`: id, name, type (enum: DIRECT/GROUP/PUBLIC), company_id, created_by (user_id), members (many-to-many via new ChannelMember model: channel_id, user_id, joined_at)
- [ ] Create `backend/app/models/message_reactions.py`: id, message_id (FK ChatMessage), user_id (FK User), emoji (str), created_at
- [ ] Create `backend/app/models/meetings.py`: id, title, organizer_id (FK User), company_id, start_time/end_time (DateTime), status (enum: SCHEDULED/ACTIVE/ENDED), link (str for WebRTC room)
- [ ] Create `backend/app/models/meeting_participants.py`: meeting_id (FK), user_id (FK), role (enum: ORGANIZER/PARTICIPANT), join_time/leave_time (DateTime nullable)
- [ ] Edit `backend/app/models/notification.py`: Add types CHAT_MESSAGE, MEETING_INVITE, MEETING_STARTED
- [ ] Create Alembic revision: `alembic revision --autogenerate -m "add_chat_meetings"`
- [ ] Run `alembic upgrade head`

### Services
- [ ] Create `backend/app/services/chat_service.py`: Extend crud_chat – add create_group_channel, add_member, send_message_to_channel (with attachments JSON, reactions), get_channel_messages, add/remove_reaction, get_typing_users (Redis set), mark_read_receipts (update is_read + broadcast)
- [ ] Create `backend/app/services/meeting_service.py`: create_meeting, invite_participants (add to MeetingParticipant + FCM notify), join_meeting (update join_time, broadcast presence), end_meeting (update status/leave_times), get_meetings_for_user
- [ ] Edit `backend/app/services/fcm_service.py`: Add send_meeting_invite (with deep link data: {"type": "MEETING_INVITE", "meeting_id": id, "deep_link": "workforce://meeting/{id}"})
- [ ] Create `backend/app/services/redis_service.py`: For presence (user:online:{company_id}:{user_id} -> set expire 30s on heartbeat), typing (channel:typing:{channel_id}:{user_id})

### CRUD
- [ ] Create `backend/app/crud/crud_channels.py`: create/get/update/delete channels, manage members
- [ ] Create `backend/app/crud/crud_reactions.py`: add/get/remove reactions
- [ ] Create `backend/app/crud/crud_meetings.py`: create/get/join/end meetings, manage participants
- [ ] Edit `backend/app/crud/crud_chat.py`: Integrate channels (message.channel_id FK if not direct), attachments, reactions; add typing indicator broadcast
- [ ] Edit `backend/app/crud/crud_notifications.py`: Add create_chat_notification, create_meeting_notification (types above)

### Routers
- [ ] Edit `backend/app/routers/chat.py`: Add POST /channels/create, POST /channels/{channel_id}/members, POST /messages/{message_id}/reactions, GET /channels, GET /channels/{id}/messages, WS /ws/chat/{channel_id} (extend for typing/receipts via Redis)
- [ ] Create `backend/app/routers/meetings.py`: POST /create, GET /my, POST /{id}/invite, POST /{id}/join, GET /{id}/participants, WS /ws/{meeting_id} (signaling: offer/answer/ice-candidate via broadcast)
- [ ] Edit `backend/app/routers/ws_notifications.py`: Extend ConnectionManager – add user-specific broadcast (dict company:user_id -> WS), presence heartbeat (periodic ping), typing event handling
- [ ] Edit `backend/app/routers/notifications.py`: Add endpoints for chat/meeting types

### Main App & Infra
- [ ] Edit `backend/app/main.py`: Add meetings router, WS auth middleware, Redis client init
- [ ] Edit `backend/requirements.txt`: Add aioredis, python-multipart, alembic, structlog
- [ ] Edit `docker-compose.yml`: Add Redis service, update backend depends_on
- [ ] Edit `README.md`: Add setup for Redis, FCM credentials, WebRTC (STUN/TURN servers)

## Frontend (React)
### Structure & Components
- [ ] Create `frontend-web/web/src/features/chat_and_meetings/` folder
- [ ] Create `ChatPanel.jsx`: List channels/direct, message list (group by date), real-time via useWebSocket hook
- [ ] Create `MessageInput.jsx`: Textarea + send, emoji picker, file upload, mentions
- [ ] Create `MeetingRoom.jsx`: Video grid (PeerJS), controls (mute/camera/share screen), participant list
- [ ] Create `useChatStore.js` (Zustand): activeChannel, messages, typingUsers, unreadCounts
- [ ] Create `useMeetingStore.js`: activeMeeting, participants, signaling
- [ ] Edit existing WS hook: Extend for auth, channels, events (typing, receipts)
- [ ] Create `ChannelList.jsx`: Fetch /channels, join on click
- [ ] Integrate toasts for new messages/invites

### Dependencies
- [ ] Edit `frontend-web/web/package.json`: Add zustand, react-emoji-picker, react-dropzone, peerjs, socket.io-client

## Mobile (Flutter)
### Structure & Components
- [ ] Edit `mobile/lib/src/features/chat_screen.dart`: Channel list, message composer (attachments, reactions), real-time WS
- [ ] Create `mobile/lib/src/features/meeting_screen.dart`: RTCVideoRenderer, controls, participant list
- [ ] Edit `mobile/lib/src/api_service.dart`: Add methods for /channels, /messages/send (multipart), /meetings/create/join, WS connections
- [ ] Use Provider/Riverpod for chat/meeting state
- [ ] Edit FCM handler: Deep links for meeting invites

### Dependencies
- [ ] Edit `mobile/pubspec.yaml`: Add flutter_webrtc, web_socket_channel, file_picker, emoji_picker_flutter, firebase_dynamic_links

## Testing & Simulation
### Backend Tests
- [ ] Create `backend/tests/test_chat_service.py`: Test create_channel, send_message (attachments/reactions), WS broadcast, typing/receipts (mock Redis)
- [ ] Create `backend/tests/test_meeting_service.py`: Test create/join/end, participant mgmt, signaling events
- [ ] Edit `backend/tests/test_notifications.py`: Add chat/meeting types, FCM mocks
- [ ] Create `backend/tests/mock_firebase.py`: Mock FCMService for tests

### Frontend Tests
- [ ] Create `frontend-web/web/src/tests/chat_integration.test.js`: Render ChatPanel, simulate WS messages, test input/send/reactions (msw for API/WS mocks)

### Infra & Simulation
- [ ] Edit `docker-compose.yml`: Add services for React (nginx or dev server port 3000), Flutter web if needed
- [ ] Create `simulation_script.sh`: docker-compose up; curl tests for chat/meetings; simulate WS (wscat) for message flow/signaling
- [ ] Run local simulation: Backend localhost:8000, Frontend 3000; test end-to-end

### Lint/Format
- [ ] Run black/isort on backend
- [ ] Run eslint/prettier on frontend
- [ ] Run dart format on mobile

## Final Output
- [ ] Generate `Workforce App Communication Readiness Report.md`: Sections for Messenger/Meetings readiness, Integration health, Logging, Test summary, Score: 85/100
- [ ] Create `auto_patch_chat_meetings.sh`: Seq of commands: alembic upgrade, pip install, create files, run tests, docker-compose up
