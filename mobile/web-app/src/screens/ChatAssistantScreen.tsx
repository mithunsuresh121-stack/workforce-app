import React, { useState, useEffect, useRef } from 'react';
import Alert, { AlertDescription, AlertTitle } from '../components/ui/Alert';
import Skeleton from '../components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

// Mock chat messages
const mockMessages = [
  { id: 1, text: "Hello! How can I help you today?", sender: "assistant", timestamp: "10:00 AM" },
  { id: 2, text: "I need help with the employee management system.", sender: "user", timestamp: "10:01 AM" },
  { id: 3, text: "Sure, I can help with that. What specifically would you like to know?", sender: "assistant", timestamp: "10:01 AM" },
  { id: 4, text: "How do I add a new employee to the system?", sender: "user", timestamp: "10:02 AM" },
  { id: 5, text: "To add a new employee, go to the Employees section and click the 'Add Employee' button. Fill in the required information and click 'Save'.", sender: "assistant", timestamp: "10:02 AM" },
];

const ChatAssistantScreen: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchChatData = async () => {
      try {
        setLoading(true);
        setError(null);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMessages(mockMessages);
      } catch (err) {
        setError('Failed to load chat assistant data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchChatData();
  }, []);

  useEffect(() => {
    // Scroll to bottom of chat when messages change
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async () => {
    if (inputValue.trim() === '') return;

    // Add user message to chat
    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Simulate API call to get assistant response
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Add assistant response
      const assistantMessage = {
        id: messages.length + 2,
        text: `I received your message: "${inputValue}". This is a simulated response from the assistant.`,
        sender: "assistant",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError('Failed to send message. Please try again.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Chat Assistant</h1>
        
        <Card className="shadow-sm h-[calc(100vh-200px)] flex flex-col">
          <CardHeader>
            <CardTitle>Chat Assistant</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            <div className="space-y-4">
              {[...Array(5)].map((_, index) => (
                <div key={index} className={`flex ${index % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
                  <div className={`max-w-xs md:max-w-md rounded-lg p-4 ${index % 2 === 0 ? 'bg-gray-100' : 'bg-blue-500 text-white'}`}>
                    <Skeleton className="h-4 w-full mb-2" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          <CardContent className="border-t">
            <div className="flex space-x-2">
              <Skeleton className="h-10 flex-1" />
              <Skeleton className="h-10 w-24" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Chat Assistant</h1>
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Chat Assistant</h1>
      
      <Card className="shadow-sm h-[calc(100vh-200px)] flex flex-col">
        <CardHeader>
          <CardTitle>Chat Assistant</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto">
          <div className="space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-xs md:max-w-md rounded-lg p-4 ${
                    message.sender === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.text}</p>
                  <p className={`text-xs mt-1 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                    {message.timestamp}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
        <CardContent className="border-t">
          <div className="flex space-x-2">
            <Input
              type="text"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1"
            />
            <Button onClick={handleSend}>Send</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatAssistantScreen;
