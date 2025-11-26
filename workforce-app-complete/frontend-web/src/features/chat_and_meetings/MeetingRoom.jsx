import React, { useState, useEffect, useRef } from 'react';
import { FaMicrophone, FaMicrophoneSlash, FaVideo, FaVideoSlash, FaPhone, FaUsers } from 'react-icons/fa';
import useWebSocket from '../../../web-app/src/hooks/useWebSocket';

const MeetingRoom = ({ meetingId, userId, onLeave }) => {
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const token = localStorage.getItem('token');
  const { send, connected } = useWebSocket(`/api/ws/meetings/${meetingId}`, token, (msg) => {
    if (msg.type === 'pong') {
      // Heartbeat response
      return;
    } else if (msg.type === 'meeting_join') {
      setParticipants(prev => [...prev.filter(p => p.user_id !== msg.data.user_id), { user_id: msg.data.user_id, online: true }]);
    } else if (msg.type === 'meeting_leave') {
      setParticipants(prev => prev.filter(p => p.user_id !== msg.data.user_id));
    } else if (msg.type === 'presence_update') {
      setParticipants(msg.data.online_users || []);
    } else if (msg.type === 'meeting_signal') {
      handleWebRTCSignaling(msg.data);
    }
  });

  useEffect(() => {
    if (connected) {
      send({ type: 'meeting_join' });
    }
  }, [connected, send]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (connected) {
        send({ type: 'ping' });
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [connected, send]);

  const handleWebRTCSignaling = (data) => {
    // Handle WebRTC signaling (offer, answer, ice-candidate)
    if (peerConnectionRef.current) {
      if (data.type === 'offer') {
        peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data.data));
        // Create and send answer
        peerConnectionRef.current.createAnswer().then(answer => {
          peerConnectionRef.current.setLocalDescription(answer);
          send({ type: 'meeting_signal', data: { type: 'answer', data: answer } });
        });
      } else if (data.type === 'answer') {
        peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data.data));
      } else if (data.type === 'ice-candidate') {
        peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(data.data));
      }
    }
  };

  useEffect(() => {
    // Initialize WebRTC
    initializeWebRTC();
    // Load participants
    fetchParticipants();

    return () => {
      // Cleanup WebRTC connections
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };
  }, [meetingId]);

  const initializeWebRTC = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: !isVideoOff,
        audio: !isMuted
      });

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }

      // WebRTC peer connection setup would go here
      // This is a simplified version - in production you'd use a library like PeerJS or native WebRTC
      peerConnectionRef.current = new RTCPeerConnection();

      stream.getTracks().forEach(track => {
        peerConnectionRef.current.addTrack(track, stream);
      });

      // Signaling would be handled via WebSocket
      // For now, we'll just set up the basic connection
    } catch (error) {
      console.error('Error initializing WebRTC:', error);
    }
  };

  const fetchParticipants = async () => {
    try {
      const response = await fetch(`/api/meetings/${meetingId}/participants`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setParticipants(data);
    } catch (error) {
      console.error('Error fetching participants:', error);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    const stream = localVideoRef.current?.srcObject;
    if (stream) {
      stream.getAudioTracks().forEach(track => {
        track.enabled = !isMuted;
      });
    }
  };

  const toggleVideo = () => {
    setIsVideoOff(!isVideoOff);
    const stream = localVideoRef.current?.srcObject;
    if (stream) {
      stream.getVideoTracks().forEach(track => {
        track.enabled = !isVideoOff;
      });
    }
  };

  const toggleScreenShare = async () => {
    try {
      if (!isScreenSharing) {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true
        });
        // Handle screen sharing
        setIsScreenSharing(true);
      } else {
        // Stop screen sharing
        setIsScreenSharing(false);
      }
    } catch (error) {
      console.error('Error sharing screen:', error);
    }
  };

  const leaveMeeting = async () => {
    try {
      // Send leave message via WebSocket
      if (connected) {
        send({ type: 'meeting_leave' });
      }

      await fetch(`/api/meetings/${meetingId}/leave`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      onLeave();
    } catch (error) {
      console.error('Error leaving meeting:', error);
    }
  };

  return (
    <div className="meeting-room">
      <div className="meeting-header">
        <h2>Meeting Room</h2>
        {!connected && <span className="reconnecting-indicator">Reconnecting...</span>}
        <div className="meeting-info">
          <span>Meeting ID: {meetingId}</span>
          <span>Participants: {participants.length}</span>
        </div>
      </div>

      <div className="video-container">
        <div className="local-video">
          <video
            ref={localVideoRef}
            autoPlay
            muted
            className="video-element"
          />
          <div className="video-overlay">
            <span>You</span>
          </div>
        </div>

        <div className="remote-videos">
          {participants.filter(p => p.user_id !== userId).map(participant => (
            <div key={participant.user_id} className="remote-video">
              <video
                ref={remoteVideoRef}
                autoPlay
                className="video-element"
              />
              <div className="video-overlay">
                <span>User {participant.user_id}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="meeting-controls">
        <button
          className={`control-btn ${isMuted ? 'muted' : ''}`}
          onClick={toggleMute}
        >
          {isMuted ? <FaMicrophoneSlash /> : <FaMicrophone />}
        </button>

        <button
          className={`control-btn ${isVideoOff ? 'video-off' : ''}`}
          onClick={toggleVideo}
        >
          {isVideoOff ? <FaVideoSlash /> : <FaVideo />}
        </button>

        <button
          className={`control-btn ${isScreenSharing ? 'active' : ''}`}
          onClick={toggleScreenShare}
        >
          Screen Share
        </button>

        <button className="control-btn participants-btn">
          <FaUsers />
          <span>{participants.length}</span>
        </button>

        <button className="control-btn leave-btn" onClick={leaveMeeting}>
          <FaPhone />
          Leave
        </button>
      </div>

      <div className="participants-list">
        <h3>Participants ({participants.length})</h3>
        <ul>
          {participants.map(participant => (
            <li key={participant.user_id}>
              User {participant.user_id}
              {participant.online && <span style={{ color: 'green', marginLeft: '5px' }}>●</span>}
              {participant.role === 'organizer' && <span className="organizer-badge">Organizer</span>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default MeetingRoom;
