import React, { useState, useEffect, useRef } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

export default function ChatPanel({ channelId, token }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const [typing, setTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const { send, connected } = useWebSocket(`/api/ws/chat/${channelId}`, token, (msg) => {
    if (msg.type === 'message_receive') {
      setMessages(prev => [...prev, msg.data]);
    } else if (msg.type === 'typing_start') {
      setTypingUsers(prev => prev.includes(msg.data.user_id) ? prev : [...prev, msg.data.user_id]);
    } else if (msg.type === 'typing_stop') {
      setTypingUsers(prev => prev.filter(id => id !== msg.data.user_id));
    } else if (msg.type === 'reaction_add') {
      setMessages(prev => prev.map(m =>
        m.id === msg.data.message_id
          ? { ...m, reactions: [...(m.reactions || []), msg.data.reaction] }
          : m
      ));
    } else if (msg.type === 'reaction_update') {
      setMessages(prev => prev.map(m =>
        m.id === msg.data.message_id
          ? { ...m, reactions: msg.data.reactions }
          : m
      ));
    }
  });

  const handleSend = () => {
    if (text.trim()) {
      send({ type: 'message_send', text });
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (!typing) {
      send({ type: 'typing_start' });
      setTyping(true);
    }
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  useEffect(() => {
    if (typing) {
      const timer = setTimeout(() => {
        send({ type: 'typing_stop' });
        setTyping(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [typing, send]);

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>Chat Channel {channelId}</h2>
      <div style={{ border: '1px solid #ccc', height: '300px', overflowY: 'scroll', padding: '10px', marginBottom: '10px' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{ marginBottom: '10px' }}>
            <strong>User {msg.sender_id}:</strong> {msg.text}
            {msg.reactions && msg.reactions.length > 0 && (
              <div>
                {msg.reactions.map(r => (
                  <span key={r.emoji} style={{ marginRight: '5px', cursor: 'pointer' }} onClick={() => send({ type: 'reaction_add', message_id: msg.id, emoji: r.emoji })}>
                    {r.emoji} {r.count}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      {typingUsers.length > 0 && (
        <div style={{ fontStyle: 'italic', color: '#666', marginBottom: '10px' }}>
          {typingUsers.length === 1 ? `User ${typingUsers[0]} is typing...` : `${typingUsers.length} users are typing...`}
        </div>
      )}
      <div>
        <input
          type="text"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          style={{ width: '80%', padding: '5px' }}
          disabled={!connected}
        />
        <button onClick={handleSend} disabled={!connected || !text.trim()}>
          Send
        </button>
        <div style={{ marginTop: '5px', color: connected ? 'green' : 'red' }}>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
    </div>
  );
}
