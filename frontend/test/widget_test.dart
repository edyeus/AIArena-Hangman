import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('Trip Planner app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();

    // Verify that the Trip Planner app loads with expected elements.
    expect(find.text('Trip Planner'), findsWidgets);
    expect(find.text('Chat Assistant'), findsOneWidget);

    // Verify initial bot message is present
    expect(find.text('Hi! Tell me your destination, dates, and preferences.'), findsOneWidget);

    // Verify that the app has the key sections (they should be present even if empty)
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(Scaffold), findsOneWidget);
  });
}
