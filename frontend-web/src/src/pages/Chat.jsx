import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import './Chat.css';

const Chat = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchUsers();
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (selectedUser) {
      fetchMessages(selectedUser.id);
    }
  }, [selectedUser]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchUsers = async () => {
    try {
      // Assuming there's an endpoint to get company users
      // For now, we'll use a placeholder
      const response = await api.get('/users/company');
      setUsers(response.data.filter(u => u.id !== user.id));
    } catch (error) {
      console.error('Error fetching users:', error);
      // Fallback: use sample users
      setUsers([
        { id: 2, full_name: 'John Doe', role: 'EMPLOYEE' },
        { id: 3, full_name: 'Jane Smith', role: 'MANAGER' }
      ]);
    }
  };

  const fetchMessages = async (userId) => {
    try {
      const response = await api.get(`/chat/history/${userId}`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
      setMessages([]);
    }
  };

  const connectWebSocket = () => {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat?token=${localStorage.getItem('token')}`);
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'new_message') {
        setMessages(prev => [...prev, data.message]);
        // Play sound alert
        playNotificationSound();
      }
    };
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after delay
      setTimeout(connectWebSocket, 3000);
    };
    wsRef.current = ws;
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedUser) return;

    try {
      setLoading(true);
      const response = await api.post('/chat/send', {
        receiver_id: selectedUser.id,
        message: newMessage.trim()
      });
      setMessages(prev => [...prev, response.data]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const playNotificationSound = () => {
    // Simple beep sound
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1fLOfCsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBzeP1
