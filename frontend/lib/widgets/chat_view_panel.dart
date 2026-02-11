import 'package:flutter/material.dart';
import '../models/chat_model.dart';
import 'chat_bubble.dart';

class ChatViewPanel extends StatefulWidget {
  final TextEditingController controller;
  final List<ChatMessage> messages;
  final bool isLoading;
  final Function(String) onSendMessage;

  const ChatViewPanel({
    super.key,
    required this.controller,
    required this.messages,
    required this.isLoading,
    required this.onSendMessage,
  });

  @override
  State<ChatViewPanel> createState() => _ChatViewPanelState();
}

class _ChatViewPanelState extends State<ChatViewPanel> {
  final ScrollController _scrollController = ScrollController();

  @override
  void didUpdateWidget(ChatViewPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.messages.length != oldWidget.messages.length) {
      _scrollToBottom();
    }
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
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        children: [
          Row(
            children: [
              Text('Chat Assistant', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              Icon(Icons.chat_bubble_outline, color: Theme.of(context).colorScheme.primary),
            ],
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: widget.messages.length + (widget.isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (widget.isLoading && index == widget.messages.length) {
                  return const ChatBubble(
                    text: 'Analyzing your request...',
                    isUser: false,
                  );
                }
                final message = widget.messages[index];
                return ChatBubble(
                  text: message.text,
                  isUser: message.isUser,
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: widget.controller,
                    minLines: 1,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      hintText: 'Ask about routes, dates, budgets...',
                      border: InputBorder.none,
                    ),
                    onSubmitted: widget.isLoading ? null : (text) {
                      if (text.trim().isNotEmpty) {
                        widget.onSendMessage(text);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: widget.isLoading ? null : () {
                    final text = widget.controller.text;
                    if (text.trim().isNotEmpty) {
                      widget.onSendMessage(text);
                    }
                  },
                  child: const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
