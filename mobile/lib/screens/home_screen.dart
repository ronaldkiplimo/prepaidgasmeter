import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_client.dart';
import 'meters_screen.dart';
import 'purchase_screen.dart';
import 'transactions_screen.dart';
import 'tokens_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0;

  final _screens = const [
    _DashboardTab(),
    MetersScreen(),
    PurchaseScreen(),
    TransactionsScreen(),
    TokensScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PrepaidMeter'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthProvider>().logout(),
          ),
        ],
      ),
      body: _screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.electric_meter), label: 'Meters'),
          NavigationDestination(icon: Icon(Icons.payment), label: 'Buy'),
          NavigationDestination(icon: Icon(Icons.receipt_long), label: 'Txns'),
          NavigationDestination(icon: Icon(Icons.token), label: 'Tokens'),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatefulWidget {
  const _DashboardTab();

  @override
  State<_DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<_DashboardTab> {
  List<dynamic> _meters = [];
  List<dynamic> _transactions = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final api = ApiClient();
      final meters = await api.getMeters();
      final txns = await api.getTransactions();
      setState(() {
        _meters = meters;
        _transactions = txns.take(5).toList();
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    final user = context.watch<AuthProvider>().user;
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Hello, ${user?['first_name'] ?? user?['phone_number'] ?? ''}!',
            style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 16),
          Row(
            children: [
              _StatCard(label: 'Meters', value: '${_meters.length}'),
              const SizedBox(width: 12),
              _StatCard(label: 'Transactions', value: '${_transactions.length}'),
            ],
          ),
          const SizedBox(height: 24),
          Text('Recent Transactions', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          if (_transactions.isEmpty)
            const Card(child: Padding(padding: EdgeInsets.all(16), child: Text('No transactions yet.')))
          else
            ..._transactions.map((t) => Card(
              child: ListTile(
                title: Text('KES ${t['amount']}'),
                subtitle: Text('${t['meter_number']} · ${t['reference']}'),
                trailing: Chip(label: Text(t['status'], style: const TextStyle(fontSize: 10))),
              ),
            )),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
              const SizedBox(height: 4),
              Text(value, style: Theme.of(context).textTheme.headlineSmall),
            ],
          ),
        ),
      ),
    );
  }
}
