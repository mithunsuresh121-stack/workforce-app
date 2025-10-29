# TODO: Lark-Style Messenger & Meetings Integration

## Backend Extensions
- [ ] Extend `websocket_manager.py`: Add typing indicators, read receipts, presence tracking, WebRTC signaling (offer/answer/ICE) for meetings.
- [ ] Update `chat_service.py`: Integrate typing and read receipts with WS broadcasts.
- [ ] Update `meeting_service.py`: Add WebRTC signaling routes and participant status updates.
- [ ] Extend `fcm_service.py`: Add deep link payloads for meeting invites.
- [ ] Create `mock_firebase.py`: Simulate FCM sends for testing.
- [ ] Create new Alembic migration: Add indexes on company_id, channel_id, etc., for performance.
- [ ] Update `docker-compose.yml`: Add Redis service, expose ports.
- [ ] Update `README.md`: Add setup for chat/meetings, simulation steps.

## Frontend (React) Updates
- [ ] Update `ChatPanel.jsx`: Integrate WS for real-time messages/typing/presence, add Redux/Zustand store.
- [ ] Update `MessageInput.jsx`: Add emoji picker, file upload, mentions.
- [ ] Update `MeetingRoom.jsx`: Implement WebRTC with PeerJS, controls, participant list.
- [ ] Create `src/store/chatSlice.js`: Zustand store for chats/meetings/presence.
- [ ] Update `package.json`: Add peerjs, react-emoji-picker, react-hot-toast.

## Mobile (Flutter) Updates
- [ ] Update `chat_screen.dart`: WS connection, real-time updates, ListView.
- [ ] Update `meeting_screen.dart`: flutter_webrtc integration, controls, signaling.
- [ ] Update `api_service.dart`: Add new endpoints (/messages/send, /channels/create, /meetings/create/join).
- [ ] Update `pubspec.yaml`: Add flutter_webrtc, web_socket_channel, firebase_messaging, uni_links.

## Testing Extensions
- [ ] Extend `test_chat_service.py`: Add tests for typing/receipts/reactions.
- [ ] Extend `test_meeting_service.py`: Add tests for signaling/participants.
- [ ] Create `frontend/tests/chat_integration.test.js`: Component/WS tests.
- [ ] Run pytest, npm test, flutter test after patches.

## Simulation & Reporting
- [ ] Run docker-compose up: Verify backend(8000), frontend(3000), redis(6379).
- [ ] Test e2e: Create channel/meeting, send message, join WS, WebRTC call, FCM push.
- [ ] Generate `readiness_report.md`: Messenger 90%, Meetings 80%, Integration 95%, Logging 100%, Tests 80%, Overall 89/100.
- [ ] Log changes to `backend/change_log.txt`.

## Safety
- Run pytest after each backend patch.
- Do not modify existing migrations.
- Maintain structlog and JWT auth.
