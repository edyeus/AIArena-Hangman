class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class Intent {
  final String intent;
  final String action;
  final String value;

  Intent({
    required this.intent,
    required this.action,
    required this.value,
  });

  factory Intent.fromJson(Map<String, dynamic> json) {
    return Intent(
      intent: json['intent'] as String,
      action: json['action'] as String,
      value: json['value'] as String,
    );
  }
}
