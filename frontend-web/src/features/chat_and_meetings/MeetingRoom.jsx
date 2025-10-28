import React, { useState, useEffect, useRef } from 'react';
import { FaMicrophone, FaMicrophoneSlash, FaVideo, FaVideoSlash, FaPhone, FaUsers } from 'react-icons/fa';

const MeetingRoom = ({ meetingId, userId, onLeave }) => {
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const peerConnectionRef = useRef(null);

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
        track.enabled = isMuted;
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
              {participant.role === 'organizer' && <span className="organizer-badge">Organizer</span>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default MeetingRoom;
