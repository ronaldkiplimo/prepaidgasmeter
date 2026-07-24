import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_client.dart';

class PurchaseScreen extends StatefulWidget {
  const PurchaseScreen({super.key});

  @override
  State<PurchaseScreen> createState() => _PurchaseScreenState();
}

class _PurchaseScreenState extends State<PurchaseScreen> {
  List<dynamic> _meters = [];
  String? _selectedMeterId;
  final _amountController = TextEditingController();
  final _phoneController = TextEditingController();
  bool _loading = true;
  bool _submitting = false;
  Map<String, dynamic>? _result;

  static const _quickAmounts = [100, 200, 500, 1000, 2000, 5000];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_phoneController.text.isEmpty) {
      final user = context.read<AuthProvider>().user;
      _phoneController.text = user?['phone_number'] ?? '';
    }
  }

  Future<void> _load() async {
    try {
      _meters = await ApiClient().getMeters();
      if (_meters.isNotEmpty) {
        final primary = _meters.cast<Map>().firstWhere(
          (m) => m['is_primary'] == true,
          orElse: () => _meters.first,
        );
        _selectedMeterId = primary['id'];
      }
    } catch (_) {}
    setState(() => _loading = false);
  }

  Future<void> _purchase() async {
    if (_selectedMeterId == null || _amountController.text.isEmpty) return;
    setState(() { _submitting = true; _result = null; });
    try {
      final result = await ApiClient().purchaseToken({
        'meter_id': _selectedMeterId,
        'amount': _amountController.text,
        'phone_number': _phoneController.text.trim(),
      });
      setState(() => _result = result);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('STK Push sent! Check your phone.')),
        );
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    if (_meters.isEmpty) {
      return const Center(child: Text('Add a meter before purchasing tokens.'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            value: _selectedMeterId,
            decoration: const InputDecoration(labelText: 'Select Meter'),
            items: _meters.map<DropdownMenuItem<String>>((m) {
              return DropdownMenuItem(
                value: m['id'],
                child: Text('${m['nickname'] ?? m['meter_number']} (${m['meter_number']})'),
              );
            }).toList(),
            onChanged: (v) => setState(() => _selectedMeterId = v),
          ),
          const SizedBox(height: 16),
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.teal.shade200, width: 2),
              gradient: LinearGradient(
                colors: [Colors.teal.shade50, Colors.amber.shade50],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.monetization_on, color: Colors.teal.shade700, size: 20),
                    const SizedBox(width: 8),
                    Text('Amount (KES)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.teal.shade800)),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _amountController,
                  decoration: InputDecoration(
                    labelText: 'Enter amount',
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.teal.shade500, width: 2)),
                    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.teal.shade700, width: 2.5)),
                  ),
                  keyboardType: TextInputType.number,
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: Colors.teal.shade900, textBaseline: TextBaseline.alphabetic),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _quickAmounts.map((a) => ActionChip(
                    label: Text('KES $a', style: TextStyle(fontWeight: FontWeight.bold)),
                    backgroundColor: Colors.teal.shade50,
                    side: BorderSide(color: Colors.teal.shade200),
                    onPressed: () => _amountController.text = '$a',
                  )).toList(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _phoneController,
            decoration: const InputDecoration(labelText: 'M-Pesa Phone'),
            keyboardType: TextInputType.phone,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _submitting ? null : _purchase,
            child: _submitting
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : Text('Pay KES ${_amountController.text.isEmpty ? "0" : _amountController.text}'),
          ),
          if (_result != null) ...[
            const SizedBox(height: 24),
            Card(
              color: Colors.green.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Payment Initiated', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('Reference: ${_result!['reference']}'),
                    Text('Status: ${_result!['status']}'),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
