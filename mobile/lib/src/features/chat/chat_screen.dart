import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/services/api_service.dart';
import '../../../core/models/chat_message.dart';
import '../../../core/models/channel.dart';
import 'widgets/message_input.dart';
import 'widgets/message_bubble.dart';

class ChatScreen extends StatefulWidget {
  final Channel? channel;
  final int? receiverId;

  const ChatScreen({Key? key, this.channel, this.receiverId}) : super(key: key);

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadMessages();
  }

  Future<void> _loadMessages() async {
    setState(() => _isLoading = true);
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final messages = await apiService.getChatHistory(
        channelId: widget.channel?.id,
        receiverId: widget.receiverId,
      );
      setState(() {
        _messages.clear();
        _messages.addAll(messages);
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load messages: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _onMessageSent(ChatMessage message) {
    setState(() {
      _messages.add(message);
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.channel?.name ?? 'Chat'),
        actions: [
          if (widget.channel != null)
            IconButton(
              icon: const Icon(Icons.info),
              onPressed: () => _showChannelInfo(context),
            ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      return MessageBubble(message: message);
                    },
                  ),
          ),
          MessageInput(
            channelId: widget.channel?.id,
            receiverId: widget.receiverId,
            onMessageSent: _onMessageSent,
          ),
        ],
      ),
    );
  }

  void _showChannelInfo(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              widget.channel!.name,
              style: Theme.of(context).textTheme.headline6,
            ),
            const SizedBox(height: 8),
            Text('Type: ${widget.channel!.type}'),
            Text('Members: ${widget.channel!.memberCount ?? 0}'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
}
