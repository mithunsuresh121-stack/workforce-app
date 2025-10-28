import React, { useState, useRef } from 'react';
import { FaPaperclip, FaSmile } from 'react-icons/fa';

const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() || attachments.length > 0) {
      onSend(message, attachments);
      setMessage('');
      setAttachments([]);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const newAttachments = files.map(file => ({
      file,
      name: file.name,
      type: file.type,
      size: file.size
    }));
    setAttachments(prev => [...prev, ...newAttachments]);
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const addEmoji = (emoji) => {
    setMessage(prev => prev + emoji);
    setShowEmojiPicker(false);
  };

  return (
    <div className="message-input-container">
      {attachments.length > 0 && (
        <div className="attachments-preview">
          {attachments.map((att, index) => (
            <div key={index} className="attachment-item">
              <span>{att.name}</span>
              <button onClick={() => removeAttachment(index)}>×</button>
            </div>
          ))}
        </div>
      )}
      <form onSubmit={handleSubmit} className="message-input-form">
        <button
          type="button"
          className="attachment-btn"
          onClick={() => fileInputRef.current?.click()}
        >
          <FaPaperclip />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileSelect}
          accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
        />
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="message-input"
        />
        <button
          type="button"
          className="emoji-btn"
          onClick={() => setShowEmojiPicker(!showEmojiPicker)}
        >
          <FaSmile />
        </button>
        <button type="submit" className="send-btn" disabled={!message.trim() && attachments.length === 0}>
          Send
        </button>
      </form>
      {showEmojiPicker && (
        <div className="emoji-picker">
          {['😀', '😂', '❤️', '👍', '👎', '🔥', '💯', '🙌'].map(emoji => (
            <button key={emoji} onClick={() => addEmoji(emoji)}>
              {emoji}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessageInput;
