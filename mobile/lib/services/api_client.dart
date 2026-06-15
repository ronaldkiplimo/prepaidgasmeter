import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );
}

class ApiClient {
  static final ApiClient _instance = ApiClient._();
  factory ApiClient() => _instance;
  ApiClient._();

  final _storage = const FlutterSecureStorage();
  String? _accessToken;

  Future<void> setTokens(String access, String refresh) async {
    _accessToken = access;
    await _storage.write(key: 'access_token', value: access);
    await _storage.write(key: 'refresh_token', value: refresh);
  }

  Future<void> loadTokens() async {
    _accessToken = await _storage.read(key: 'access_token');
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<String?> get refreshToken => _storage.read(key: 'refresh_token');

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_accessToken != null) 'Authorization': 'Bearer $_accessToken',
      };

  Future<http.Response> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool retry = true,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$path');
    late http.Response response;

    switch (method) {
      case 'GET':
        response = await http.get(uri, headers: _headers);
        break;
      case 'POST':
        response = await http.post(uri, headers: _headers, body: jsonEncode(body));
        break;
      case 'PATCH':
        response = await http.patch(uri, headers: _headers, body: jsonEncode(body));
        break;
      case 'DELETE':
        response = await http.delete(uri, headers: _headers);
        break;
      default:
        throw UnsupportedError('Method $method not supported');
    }

    if (response.statusCode == 401 && retry) {
      final refreshed = await _refreshAccessToken();
      if (refreshed) return _request(method, path, body: body, retry: false);
    }

    return response;
  }

  Future<bool> _refreshAccessToken() async {
    final refresh = await _storage.read(key: 'refresh_token');
    if (refresh == null) return false;

    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/token/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': refresh}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _accessToken = data['access'];
      await _storage.write(key: 'access_token', value: _accessToken!);
      return true;
    }
    await clearTokens();
    return false;
  }

  Future<Map<String, dynamic>> login(String phone, String password) async {
    final response = await _request('POST', '/auth/login/', body: {
      'phone_number': phone,
      'password': password,
    });
    if (response.statusCode != 200) {
      throw ApiException(jsonDecode(response.body));
    }
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> register(Map<String, dynamic> data) async {
    final response = await _request('POST', '/auth/register/', body: data);
    if (response.statusCode != 201) {
      throw ApiException(jsonDecode(response.body));
    }
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> profile() async {
    final response = await _request('GET', '/auth/profile/');
    if (response.statusCode != 200) throw ApiException(jsonDecode(response.body));
    return jsonDecode(response.body);
  }

  Future<List<dynamic>> getMeters() async {
    final response = await _request('GET', '/meters/');
    if (response.statusCode != 200) throw ApiException(jsonDecode(response.body));
    final data = jsonDecode(response.body);
    return data['results'] ?? data;
  }

  Future<Map<String, dynamic>> addMeter(Map<String, dynamic> data) async {
    final response = await _request('POST', '/meters/', body: data);
    if (response.statusCode != 201) throw ApiException(jsonDecode(response.body));
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> purchaseToken(Map<String, dynamic> data) async {
    final response = await _request('POST', '/payments/purchase/', body: data);
    if (response.statusCode != 201) throw ApiException(jsonDecode(response.body));
    return jsonDecode(response.body);
  }

  Future<List<dynamic>> getTransactions() async {
    final response = await _request('GET', '/payments/transactions/');
    if (response.statusCode != 200) throw ApiException(jsonDecode(response.body));
    final data = jsonDecode(response.body);
    return data['results'] ?? data;
  }

  Future<List<dynamic>> getTokenHistory() async {
    final response = await _request('GET', '/tokens/history/');
    if (response.statusCode != 200) throw ApiException(jsonDecode(response.body));
    final data = jsonDecode(response.body);
    return data['results'] ?? data;
  }
}

class ApiException implements Exception {
  final dynamic data;
  ApiException(this.data);

  @override
  String toString() {
    if (data is Map) {
      if (data['detail'] != null) return data['detail'].toString();
      return data.values.expand((v) => v is List ? v : [v]).join(', ');
    }
    return 'API Error';
  }
}
