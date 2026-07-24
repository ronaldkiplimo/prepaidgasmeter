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
    final user = context.watch<AuthProvider>().user;
    final displayName = user?['first_name'] ?? user?['phone_number'] ?? 'User';
    final role = user?['role'] ?? 'customer';

    return Scaffold(
      appBar: AppBar(
        title: const Text('PrepaidGasMeter'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthProvider>().logout(),
          ),
        ],
      ),
      drawer: Drawer(
        child: Column(
          children: [
            DrawerHeader(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: Colors.white24,
                    child: Text(
                      displayName.isNotEmpty ? displayName[0].toUpperCase() : 'U',
                      style: const TextStyle(fontSize: 24, color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    displayName,
                    style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  Text(
                    role,
                    style: const TextStyle(color: Colors.white70, fontSize: 13),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                padding: EdgeInsets.zero,
                children: [
                  _DrawerItem(
                    icon: Icons.dashboard,
                    label: 'Home',
                    selected: _index == 0,
                    onTap: () { setState(() => _index = 0); Navigator.pop(context); },
                  ),
                  _DrawerItem(
                    icon: Icons.local_fire_department,
                    label: 'Meters',
                    selected: _index == 1,
                    onTap: () { setState(() => _index = 1); Navigator.pop(context); },
                  ),
                  _DrawerItem(
                    icon: Icons.payment,
                    label: 'Buy Gas',
                    selected: _index == 2,
                    onTap: () { setState(() => _index = 2); Navigator.pop(context); },
                  ),
                  _DrawerItem(
                    icon: Icons.receipt_long,
                    label: 'Transactions',
                    selected: _index == 3,
                    onTap: () { setState(() => _index = 3); Navigator.pop(context); },
                  ),
                  _DrawerItem(
                    icon: Icons.token,
                    label: 'Tokens',
                    selected: _index == 4,
                    onTap: () { setState(() => _index = 4); Navigator.pop(context); },
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            SafeArea(
              child: ListTile(
                leading: const Icon(Icons.logout, color: Colors.red),
                title: const Text('Logout', style: TextStyle(color: Colors.red)),
                onTap: () {
                  Navigator.pop(context);
                  context.read<AuthProvider>().logout();
                },
              ),
            ),
          ],
        ),
      ),
      body: _screens[_index],
    );
  }
}

class _DrawerItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _DrawerItem({
    required this.icon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        icon,
        color: selected ? Theme.of(context).colorScheme.primary : null,
      ),
      title: Text(
        label,
        style: TextStyle(
          fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
          color: selected ? Theme.of(context).colorScheme.primary : null,
        ),
      ),
      selected: selected,
      selectedTileColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.08),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      onTap: onTap,
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
                title: Text('KES ${t['amount']}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.teal.shade800)),
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
