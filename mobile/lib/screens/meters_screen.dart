import 'package:flutter/material.dart';
import '../services/api_client.dart';

class MetersScreen extends StatefulWidget {
  const MetersScreen({super.key});

  @override
  State<MetersScreen> createState() => _MetersScreenState();
}

class _MetersScreenState extends State<MetersScreen> {
  List<dynamic> _meters = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _meters = await ApiClient().getMeters();
    } catch (_) {}
    setState(() => _loading = false);
  }

  Future<void> _addMeter() async {
    final meterNumber = TextEditingController();
    final nickname = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Meter'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: meterNumber, decoration: const InputDecoration(labelText: 'Meter Number')),
            TextField(controller: nickname, decoration: const InputDecoration(labelText: 'Nickname')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Add'),
          ),
        ],
      ),
    );

    if (result == true && meterNumber.text.isNotEmpty) {
      try {
        await ApiClient().addMeter({
          'meter_number': meterNumber.text.trim(),
          'nickname': nickname.text.trim(),
        });
        _load();
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: _meters.isEmpty
            ? ListView(children: const [SizedBox(height: 100), Center(child: Text('No meters registered'))])
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _meters.length,
                itemBuilder: (_, i) {
                  final m = _meters[i];
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.electric_meter),
                      title: Text(m['nickname'] ?? m['meter_number']),
                      subtitle: Text(m['meter_number']),
                      trailing: m['is_primary'] == true ? const Chip(label: Text('Primary')) : null,
                    ),
                  );
                },
              ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addMeter,
        child: const Icon(Icons.add),
      ),
    );
  }
}
