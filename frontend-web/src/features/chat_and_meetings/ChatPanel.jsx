import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import MessageInput from './MessageInput';
import { formatMessageTime } from '../../utils/dateUtils';

const ChatPanel = ({ activeChat, userId, companyId }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const ws = useWebSocket(`/ws/${userId}`);

  useEffect(() => {
    if (ws) {
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          setMessages(prev => [...prev, data.message]);
        } else if (data.type === 'typing') {
          setIsTyping(data.is_typing);
        }
      };
    }
  }, [ws]);

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

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h3>{activeChat?.name || 'Chat'}</h3>
        {isTyping && <span className="typing-indicator">Someone is typing...</span>}
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
      <MessageInput onSend={handleSendMessage} />
    </div>
  );
};

export default ChatPanel;
