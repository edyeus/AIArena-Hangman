enum Priority {
  mustHave('must_have'),
  preferred('preferred'),
  avoid('avoid');

  final String value;
  const Priority(this.value);

  static Priority fromString(String value) {
    return Priority.values.firstWhere(
      (p) => p.value == value,
      orElse: () => Priority.preferred,
    );
  }
}

class Requirement {
  final String description;
  final Priority priority;

  Requirement({
    required this.description,
    required this.priority,
  });

  factory Requirement.fromJson(Map<String, dynamic> json) {
    return Requirement(
      description: json['description'] as String,
      priority: Priority.fromString(json['priority'] as String? ?? 'preferred'),
    );
  }

  Map<String, dynamic> toJson() => {
        'description': description,
        'priority': priority.value,
      };
}
