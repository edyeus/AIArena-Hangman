import 'package:flutter/material.dart';

import 'chat_bubble.dart';

class ChatViewPanel extends StatelessWidget {
  const ChatViewPanel({super.key, required this.controller});

  final TextEditingController controller;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surfaceVariant,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        children: [
          Row(
            children: [
              Text(
                'Chat Assistant',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const Spacer(),
              Icon(
                Icons.chat_bubble_outline,
                color: Theme.of(context).colorScheme.primary,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView(
              children: const [
                ChatBubble(
                  text: 'Hi! Tell me your destination and dates.',
                  isUser: false,
                ),
                ChatBubble(
                  text: 'Planning Tokyo for mid April.',
                  isUser: true,
                ),
                ChatBubble(
                  text: 'Great! Do you prefer food tours, day trips, or museums?',
                  isUser: false,
                ),
              ],
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
                    controller: controller,
                    minLines: 1,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      hintText: 'Ask about routes, dates, budgets...',
                      border: InputBorder.none,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: () {},
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
