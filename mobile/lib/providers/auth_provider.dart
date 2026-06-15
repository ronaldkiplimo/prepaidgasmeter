import 'package:flutter/foundation.dart';
import 'api_client.dart';

class AuthProvider extends ChangeNotifier {
  final _api = ApiClient();
  Map<String, dynamic>? _user;
  bool _loading = true;
  bool _isAuthenticated = false;

  Map<String, dynamic>? get user => _user;
  bool get loading => _loading;
  bool get isAuthenticated => _isAuthenticated;

  Future<void> init() async {
    await _api.loadTokens();
    try {
      _user = await _api.profile();
      _isAuthenticated = true;
    } catch (_) {
      _isAuthenticated = false;
    }
    _loading = false;
    notifyListeners();
  }

  Future<void> login(String phone, String password) async {
    final data = await _api.login(phone, password);
    await _api.setTokens(data['access'], data['refresh']);
    _user = data['user'];
    _isAuthenticated = true;
    notifyListeners();
  }

  Future<void> register(Map<String, dynamic> formData) async {
    final data = await _api.register(formData);
    await _api.setTokens(data['tokens']['access'], data['tokens']['refresh']);
    _user = data['user'];
    _isAuthenticated = true;
    notifyListeners();
  }

  Future<void> logout() async {
    await _api.clearTokens();
    _user = null;
    _isAuthenticated = false;
    notifyListeners();
  }
}
