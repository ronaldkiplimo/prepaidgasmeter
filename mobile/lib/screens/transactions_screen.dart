import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_client.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  List<dynamic> _transactions = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _transactions = await ApiClient().getTransactions();
    } catch (_) {}
    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return RefreshIndicator(
      onRefresh: _load,
      child: _transactions.isEmpty
          ? ListView(children: const [SizedBox(height: 100), Center(child: Text('No transactions'))])
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _transactions.length,
              itemBuilder: (_, i) {
                final t = _transactions[i];
                return Card(
                  child: ListTile(
                    title: Text('KES ${t['amount']}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.teal.shade800)),
                    subtitle: Text('${t['meter_number']}\n${t['reference']}'),
                    isThreeLine: true,
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Chip(label: Text(t['status'], style: const TextStyle(fontSize: 10))),
                        Text(
                          DateFormat('MMM d, HH:mm').format(DateTime.parse(t['created_at'])),
                          style: const TextStyle(fontSize: 10),
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
