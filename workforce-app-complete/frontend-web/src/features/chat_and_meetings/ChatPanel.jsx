import React, { useState, useEffect, useRef } from 'react';
import MessageInput from './MessageInput';
import { formatMessageTime } from '../../utils/dateUtils';

const ChatPanel = ({ activeChat, userId, companyId }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [ws, setWs] = useState(null);
  const [reconnecting, setReconnecting] = useState(false);
  const messagesEndRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const reconnectDelayRef = useRef(1000); // Start with 1s delay
  const reconnectTimeoutRef = useRef(null);

  const connectWebSocket = () => {
    if (!activeChat) return;

    const token = localStorage.getItem('token');
    const wsUrl = `ws://localhost:8000/ws/chat/${activeChat.id}?token=${token}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log("Connected to chat WebSocket");
      setReconnecting(false);
      reconnectDelayRef.current = 1000; // Reset backoff delay on successful connection
      // Start heartbeat
      heartbeatIntervalRef.current = setInterval(() => {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000); // Every 30 seconds
    };
      console.log('Connected to chat WebSocket');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "pong") {
        // Heartbeat response - connection is alive
        return;
      }
      const data = JSON.parse(event.data);
      if (data.type === 'message') {
        setMessages(prev => [...prev, data.message]);
      } else if (data.type === 'typing') {
        if (data.is_typing) {
          setTypingUsers(prev => [...new Set([...prev, data.user_id])]);
        } else {
          setTypingUsers(prev => prev.filter(id => id !== data.user_id));
        }
      } else if (data.type === 'read_receipt') {
        // Handle read receipts
        setMessages(prev => prev.map(msg =>
          msg.id <= data.last_read_message_id && msg.sender_id !== userId
            ? { ...msg, is_read: true }
            : msg
        ));
      }
    };

    websocket.onclose = () => {
      console.log("Chat WebSocket disconnected, reconnecting...");
      setReconnecting(true);
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 30000); // Exponential backoff, max 30s
        connectWebSocket();
      }, reconnectDelayRef.current);
    };
      console.log('Chat WebSocket disconnected, reconnecting...');
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws) ws.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    };
      if (ws) ws.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, [activeChat?.id]);

  useEffect(() => {
    // Load message history
    if (activeChat) {
      fetch(`/api/chat/messages/history?channel_id=${activeChat.id}&limit=50`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
        .then(res => res.json())
        .then(data => setMessages(data));
    }
  }, [activeChat]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (messageText, attachments = []) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const messageData = {
        type: "message",
        message: {
          message: messageText,
          channel_id: activeChat.id,
          attachments
        }
      };
      ws.send(JSON.stringify(messageData));
    } else {
      const pendingMessages = JSON.parse(localStorage.getItem("pending_messages") || "[]");
      pendingMessages.push({
        message: messageText,
        channel_id: activeChat.id,
        attachments,
        timestamp: Date.now()
      });
      localStorage.setItem("pending_messages", JSON.stringify(pendingMessages));
    }
  };
    if (ws && activeChat) {
      const messageData = {
        type: 'message',
        message: {
          message: messageText,
          channel_id: activeChat.id,
          attachments
        }
      };
      ws.send(JSON.stringify(messageData));
    }
  };

  const handleTyping = (isTyping) => {
    if (ws && activeChat) {
      ws.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h3>{activeChat?.name || 'Chat'}</h3>
        {reconnecting <h3>{activeChat?.name || 'Chat'}</h3><h3>{activeChat?.name || 'Chat'}</h3> <span className="reconnecting-indicator">Reconnecting...</span>}
        {typingUsers.length > 0 && (
          <span className="typing-indicator">
            {typingUsers.length === 1 ? 'Someone is typing...' : `${typingUsers.length} people are typing...`}
          </span>
        )}
      </div>
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender_id === userId ? 'sent' : 'received'}`}>
            <div className="message-content">
              <span className="sender-name">{msg.sender_id === userId ? 'You' : `User ${msg.sender_id}`}</span>
              <p>{msg.message}</p>
              {msg.attachments?.length > 0 && (
                <div className="attachments">
                  {msg.attachments.map((att, i) => (
                    <a key={i} href={att.url} target="_blank" rel="noopener noreferrer">
                      {att.name}
                    </a>
                  ))}
                </div>
              )}
              <span className="message-time">{formatMessageTime(msg.created_at)}</span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput onSend={handleSendMessage} onTyping={handleTyping} />
    </div>
  );
};

export default ChatPanel;
  // Send queued messages on reconnect
  useEffect(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const pendingMessages = JSON.parse(localStorage.getItem("pending_messages") || "[]");
      if (pendingMessages.length > 0) {
        pendingMessages.forEach(msg => {
          ws.send(JSON.stringify({ type: "message", message: msg }));
        });
        localStorage.removeItem("pending_messages");
      }
    }
  }, [ws?.readyState]);
