import 'package:flutter/material.dart';

class ChatAssistantScreen extends StatelessWidget {
  const ChatAssistantScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chat Assistant'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Expanded(
              child: ListView(
                children: [
                  _ChatMessage(
                    message: 'Hello! How can I assist you today?',
                    isBot: true,
                  ),
                  _ChatMessage(
                    message: 'I need help with task management.',
                    isBot: false,
                  ),
                  _ChatMessage(
                    message: 'Sure! You can create, assign, and track tasks easily.',
                    isBot: true,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _ChatInputField(),
          ],
        ),
      ),
    );
  }
}

class _ChatMessage extends StatelessWidget {
  final String message;
  final bool isBot;

  const _ChatMessage({
    required this.message,
    required this.isBot,
  });

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isBot ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isBot ? Colors.grey[200] : Colors.blue[200],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          message,
          style: TextStyle(
            color: isBot ? Colors.black : Colors.white,
          ),
        ),
      ),
    );
  }
}

class _ChatInputField extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final TextEditingController controller = TextEditingController(); // Updated

    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: controller, // Updated to use the correct variable name
            decoration: InputDecoration(
              hintText: 'Type your message...',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        IconButton(
          icon: const Icon(Icons.send),
          onPressed: () {
            // TODO: Implement send message functionality
            controller.clear(); // Updated to use the new name
          },
        ),
      ],
    );
  }
}
