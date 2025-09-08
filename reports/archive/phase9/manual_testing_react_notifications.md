# Manual Testing Instructions for React Web Notifications

## Areas to Test
- Notification dropdown menu
- Unread badge updates on navbar icon
- Mark-as-read functionality for individual notifications
- Real-time updates (if applicable)

## Test Steps

### Notification Dropdown
1. Click the notifications icon in the navbar.
2. Verify the dropdown opens and displays a list of notifications.
3. Confirm each notification shows title, message snippet, and timestamp.
4. Check that unread notifications are visually distinct (bold or highlighted).

### Unread Badge
1. Confirm the unread badge count appears on the notifications icon.
2. Mark a notification as read and verify the badge count decreases accordingly.
3. Refresh the page and confirm the badge count persists correctly.

### Mark-as-Read
1. Click the mark-as-read button/icon on an unread notification.
2. Verify the notification visually updates to read state.
3. Confirm the backend API call is successful (check network tab).
4. Confirm the unread badge updates accordingly.

### Real-Time Updates
1. If real-time updates are implemented, trigger a new notification (e.g., assign a task).
2. Verify the notification appears in the dropdown without page refresh.
3. Confirm the unread badge updates in real-time.

## Notes
- Document any UI glitches or inconsistencies.
- Report any API errors or failures.
- Confirm cross-browser compatibility if possible.

---

This document serves as a guide for manual testing of the React web notifications UI for Phase 9.
