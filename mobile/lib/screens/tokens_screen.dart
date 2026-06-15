import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_client.dart';

class TokensScreen extends StatefulWidget {
  const TokensScreen({super.key});

  @override
  State<TokensScreen> createState() => _TokensScreenState();
}

class _TokensScreenState extends State<TokensScreen> {
  List<dynamic> _tokens = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _tokens = await ApiClient().getTokenHistory();
    } catch (_) {}
    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return RefreshIndicator(
      onRefresh: _load,
      child: _tokens.isEmpty
          ? ListView(children: const [SizedBox(height: 100), Center(child: Text('No tokens yet'))])
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _tokens.length,
              itemBuilder: (_, i) {
                final t = _tokens[i];
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Meter: ${t['meter_number']}', style: TextStyle(color: Colors.grey.shade600)),
                        const SizedBox(height: 8),
                        SelectableText(
                          t['token'],
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text('${t['token_units']} units · KES ${t['token_amount']}'),
                        Text('Ref: ${t['transaction_reference']}', style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 4),
                        Text(
                          DateFormat('MMM d, yyyy HH:mm').format(DateTime.parse(t['generated_at'])),
                          style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
