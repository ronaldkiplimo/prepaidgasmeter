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

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: _meters.isEmpty
            ? ListView(children: const [SizedBox(height: 100), Center(child: Text('No meters assigned'))])
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _meters.length,
                itemBuilder: (_, i) {
                  final m = _meters[i];
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.local_fire_department),
                      title: Text(m['nickname'] ?? m['meter_number']),
                      subtitle: Text(m['meter_number']),
                      trailing: m['is_primary'] == true ? const Chip(label: Text('Primary')) : null,
                    ),
                  );
                },
              ),
      ),
    );
  }
}
