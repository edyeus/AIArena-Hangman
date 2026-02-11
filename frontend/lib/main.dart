import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import 'models/chat_model.dart';
import 'models/poi_model.dart';
import 'models/requirement_model.dart';
import 'models/plan_model.dart';
import 'widgets/chat_view_panel.dart';
import 'widgets/main_view_panel.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Trip Planner',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Trip Planner'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _chatController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final List<POI> _pois = [];
  final List<Requirement> _requirements = [];
  List<PlanOption> _planOptions = [];
  int _selectedOptionIndex = 0;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _messages.add(ChatMessage(
      text: 'Hi! Tell me your destination, dates, and preferences.',
      isUser: false,
    ));
  }

  @override
  void dispose() {
    _chatController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true));
      _isLoading = true;
    });
    _chatController.clear();

    WebSocketChannel? channel;

    try {
      // Open WebSocket connection
      channel = WebSocketChannel.connect(
        Uri.parse('ws://127.0.0.1:5000/ws/chat'),
      );

      // Send the message with current state
      channel.sink.add(jsonEncode({
        'message': message,
        'pois': _pois.map((p) => p.toJson()).toList(),
        'requirements': _requirements.map((r) => r.toJson()).toList(),
        'plan': _planOptions.map((p) => p.toJson()).toList(),
      }));

      // Listen for progressive updates
      await for (final data in channel.stream) {
        final messageData = jsonDecode(data as String) as Map<String, dynamic>;
        final messageType = messageData['type'] as String?;

        if (messageType == 'intents') {
          // Extract General_Response intents for chat
          final intents = messageData['data'] as List<dynamic>? ?? [];
          final generalResponses = intents
              .where((i) => (i as Map<String, dynamic>)['intent'] == 'General_Response')
              .map((i) => (i as Map<String, dynamic>)['value'] as String?)
              .where((text) => text != null && text.isNotEmpty)
              .join('\n\n');

          if (generalResponses.isNotEmpty) {
            setState(() {
              _messages.add(ChatMessage(text: generalResponses, isUser: false));
            });
          }
        } else if (messageType == 'pois') {
          // Update POIs immediately
          final newPOIs = (messageData['data'] as List<dynamic>)
              .map((p) => POI.fromJson(p as Map<String, dynamic>))
              .toList();
          setState(() {
            _pois.clear();
            _pois.addAll(newPOIs);
          });
        } else if (messageType == 'requirements') {
          // Update requirements immediately
          final newReqs = (messageData['data'] as List<dynamic>)
              .map((r) => Requirement.fromJson(r as Map<String, dynamic>))
              .toList();
          setState(() {
            _requirements.clear();
            _requirements.addAll(newReqs);
          });
        } else if (messageType == 'plan') {
          // Update plan options immediately
          final newOptions = (messageData['data'] as List<dynamic>)
              .map((p) => PlanOption.fromJson(p as Map<String, dynamic>))
              .toList();
          setState(() {
            _planOptions = newOptions;
            _selectedOptionIndex = 0;
          });
        } else if (messageType == 'done') {
          // Processing complete
          setState(() => _isLoading = false);
          await channel.sink.close();
          break;
        } else if (messageType == 'error') {
          // Error occurred
          final errorMessage = messageData['message'] as String? ?? 'An error occurred';
          _addErrorMessage(errorMessage);
          setState(() => _isLoading = false);
          await channel.sink.close();
          break;
        }
      }
    } catch (e) {
      _addErrorMessage('Network error. Please check your connection and ensure the backend is running.');
      setState(() => _isLoading = false);
    } finally {
      await channel?.sink.close();
    }
  }

  void _addErrorMessage(String text) {
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: false));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final bool isWide = constraints.maxWidth >= 900;
          final mainPanel = MainViewPanel(
            pois: _pois,
            requirements: _requirements,
            planOptions: _planOptions,
            selectedOptionIndex: _selectedOptionIndex,
            onOptionSelected: (index) {
              setState(() => _selectedOptionIndex = index);
            },
          );
          final chatPanel = ChatViewPanel(
            controller: _chatController,
            messages: _messages,
            isLoading: _isLoading,
            onSendMessage: _sendMessage,
          );

          if (isWide) {
            return Row(
              children: [
                Expanded(flex: 3, child: mainPanel),
                const VerticalDivider(width: 1, thickness: 1),
                Expanded(flex: 2, child: chatPanel),
              ],
            );
          }

          return Column(
            children: [
              Expanded(child: mainPanel),
              const Divider(height: 1, thickness: 1),
              SizedBox(
                height: constraints.maxHeight * 0.45,
                child: chatPanel,
              ),
            ],
          );
        },
      ),
    );
  }
}
