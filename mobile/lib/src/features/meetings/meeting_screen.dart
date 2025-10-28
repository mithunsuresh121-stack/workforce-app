import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:provider/provider.dart';
import '../../../core/services/api_service.dart';
import '../../../core/models/meeting.dart';
import '../../../core/models/meeting_participant.dart';

class MeetingScreen extends StatefulWidget {
  final Meeting meeting;

  const MeetingScreen({Key? key, required this.meeting}) : super(key: key);

  @override
  _MeetingScreenState createState() => _MeetingScreenState();
}

class _MeetingScreenState extends State<MeetingScreen> {
  final RTCVideoRenderer _localRenderer = RTCVideoRenderer();
  final RTCVideoRenderer _remoteRenderer = RTCVideoRenderer();
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  List<MeetingParticipant> _participants = [];
  bool _isMuted = false;
  bool _isVideoOff = false;
  bool _isScreenSharing = false;

  @override
  void initState() {
    super.initState();
    _initializeRenderers();
    _joinMeeting();
    _loadParticipants();
  }

  Future<void> _initializeRenderers() async {
    await _localRenderer.initialize();
    await _remoteRenderer.initialize();
  }

  Future<void> _joinMeeting() async {
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      await apiService.joinMeeting(widget.meeting.id);

      // Initialize WebRTC
      await _initializeWebRTC();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to join meeting: $e')),
      );
    }
  }

  Future<void> _initializeWebRTC() async {
    final configuration = {
      'iceServers': [
        {'urls': 'stun:stun.l.google.com:19302'},
      ]
    };

    _peerConnection = await createPeerConnection(configuration);

    // Get user media
    _localStream = await navigator.mediaDevices.getUserMedia({
      'audio': !_isMuted,
      'video': !_isVideoOff,
    });

    _localRenderer.srcObject = _localStream;

    // Add tracks to peer connection
    _localStream!.getTracks().forEach((track) {
      _peerConnection!.addTrack(track, _localStream!);
    });

    // Handle remote stream
    _peerConnection!.onTrack = (event) {
      if (event.track.kind == 'video') {
        _remoteRenderer.srcObject = event.streams[0];
      }
    };

    // WebRTC signaling would be handled here via WebSocket
    // For simplicity, this is a basic setup
  }

  Future<void> _loadParticipants() async {
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final participants = await apiService.getMeetingParticipants(widget.meeting.id);
      setState(() {
        _participants = participants;
      });
    } catch (e) {
      print('Failed to load participants: $e');
    }
  }

  void _toggleMute() {
    setState(() {
      _isMuted = !_isMuted;
    });
    if (_localStream != null) {
      _localStream!.getAudioTracks().forEach((track) {
        track.enabled = !_isMuted;
      });
    }
  }

  void _toggleVideo() {
    setState(() {
      _isVideoOff = !_isVideoOff;
    });
    if (_localStream != null) {
      _localStream!.getVideoTracks().forEach((track) {
        track.enabled = !_isVideoOff;
      });
    }
  }

  Future<void> _toggleScreenShare() async {
    if (!_isScreenSharing) {
      try {
        final screenStream = await navigator.mediaDevices.getDisplayMedia({
          'video': true,
        });
        // Handle screen sharing
        setState(() {
          _isScreenSharing = true;
        });
      } catch (e) {
        print('Error sharing screen: $e');
      }
    } else {
      // Stop screen sharing
      setState(() {
        _isScreenSharing = false;
      });
    }
  }

  void _leaveMeeting() async {
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      await apiService.leaveMeeting(widget.meeting.id);
      Navigator.of(context).pop();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to leave meeting: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.meeting.title),
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              children: [
                // Remote video (full screen)
                RTCVideoView(
                  _remoteRenderer,
                  objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover,
                ),
                // Local video (picture-in-picture)
                Positioned(
                  top: 16,
                  right: 16,
                  width: 120,
                  height: 160,
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.white, width: 2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: RTCVideoView(
                      _localRenderer,
                      mirror: true,
                      objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.black87,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  icon: Icon(_isMuted ? Icons.mic_off : Icons.mic),
                  color: Colors.white,
                  onPressed: _toggleMute,
                ),
                IconButton(
                  icon: Icon(_isVideoOff ? Icons.videocam_off : Icons.videocam),
                  color: Colors.white,
                  onPressed: _toggleVideo,
                ),
                IconButton(
                  icon: Icon(_isScreenSharing ? Icons.screen_share : Icons.stop_screen_share),
                  color: Colors.white,
                  onPressed: _toggleScreenShare,
                ),
                IconButton(
                  icon: const Icon(Icons.people),
                  color: Colors.white,
                  onPressed: () => _showParticipants(context),
                ),
                IconButton(
                  icon: const Icon(Icons.call_end),
                  color: Colors.red,
                  onPressed: _leaveMeeting,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showParticipants(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Participants (${_participants.length})',
              style: Theme.of(context).textTheme.headline6,
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: _participants.length,
                itemBuilder: (context, index) {
                  final participant = _participants[index];
                  return ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.person)),
                    title: Text('User ${participant.userId}'),
                    subtitle: Text(participant.role),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _localRenderer.dispose();
    _remoteRenderer.dispose();
    _peerConnection?.dispose();
    _localStream?.dispose();
    super.dispose();
  }
}
