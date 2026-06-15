import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fields = <String, TextEditingController>{
    'username': TextEditingController(),
    'email': TextEditingController(),
    'phone_number': TextEditingController(),
    'first_name': TextEditingController(),
    'last_name': TextEditingController(),
    'password': TextEditingController(),
    'password_confirm': TextEditingController(),
  };
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    for (final c in _fields.values) { c.dispose(); }
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    if (_fields['password']!.text != _fields['password_confirm']!.text) {
      setState(() => _error = 'Passwords do not match');
      return;
    }
    setState(() { _loading = true; _error = null; });
    try {
      final data = <String, dynamic>{};
      for (final e in _fields.entries) {
        if (e.key != 'password_confirm') data[e.key] = e.value.text.trim();
      }
      await context.read<AuthProvider>().register(data);
      if (mounted) Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Register')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                _field('first_name', 'First Name'),
                _field('last_name', 'Last Name'),
                _field('username', 'Username'),
                _field('email', 'Email'),
                _field('phone_number', 'Phone Number'),
                _field('password', 'Password', obscure: true),
                _field('password_confirm', 'Confirm Password', obscure: true),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ],
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _register,
                    child: _loading
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                        : const Text('Register'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _field(String key, String label, {bool obscure = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: _fields[key],
        decoration: InputDecoration(labelText: label),
        obscureText: obscure,
        validator: (v) => v == null || v.isEmpty ? '$label is required' : null,
      ),
    );
  }
}
