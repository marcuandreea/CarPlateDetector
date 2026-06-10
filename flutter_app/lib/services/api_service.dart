import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/subscription_plan.dart';
import '../models/active_subscription.dart';

class ApiService {
  final String baseUrl;
  final String apiKey;

  ApiService({
    this.baseUrl = 'http://127.0.0.1:8000',
    this.apiKey = const String.fromEnvironment('PARKING_API_KEY'),
  });

  // Functie helper pentru a construi header-ele JSON
  Map<String, String> _jsonHeaders({String? token}) {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (apiKey.isNotEmpty) {
      headers['X-API-Key'] = apiKey;
    }
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Future<void> initialize() async {
    if (kDebugMode) {
      print('ApiService initialized');
    }
  }


  // Inregistreaza un nou user
  Future<http.Response> register(Map<String, dynamic> payload) async {
    final uri = Uri.parse('$baseUrl/register');
    final res = await http.post(uri, body: jsonEncode(payload), headers: _jsonHeaders());
    return res;
  }

  // Autentifica un user si returneaza raspunsul API-ului
  Future<http.Response> login(String email, String password) async {
    final uri = Uri.parse('$baseUrl/login');
    return http.post(
      uri,
      body: jsonEncode({'email': email, 'password': password}),
      headers: _jsonHeaders(),
    );
  }

  // Preia profilul userului autentificat
  Future<http.Response> getProfile(String token) async {
    final uri = Uri.parse('$baseUrl/profile');
    return http.get(uri, headers: _jsonHeaders(token: token));
  }

  // Preia statusul masinii utilizatorului autentificat
  Future<String> getParkingStatus(String token) async {
    final uri = Uri.parse('$baseUrl/parking-status');
    final response = await http.get(uri, headers: _jsonHeaders(token: token));
    if (response.statusCode != 200) {
      throw Exception('Failed to load parking status (${response.statusCode})');
    }

    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) {
      return decoded['status']?.toString() ?? 'invalid';
    }
    return 'invalid';
  }

  // Actualizeaza profilul userului autentificat
  Future<http.Response> updateProfile(String token, Map<String, dynamic> payload) async {
    final uri = Uri.parse('$baseUrl/profile');
    return http.put(uri, body: jsonEncode(payload), headers: _jsonHeaders(token: token));
  }

  // Preia planurile de abonament din baza de date
  Future<List<SubscriptionPlan>> getSubscriptionPlans() async {
    final uri = Uri.parse('$baseUrl/subscription-plans');
    final response = await http.get(uri, headers: _jsonHeaders());
    if (response.statusCode != 200) {
      throw Exception('Failed to load subscription plans (${response.statusCode})');
    }

    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      return decoded
          .whereType<Map<String, dynamic>>()
          .map(SubscriptionPlan.fromJson)
          .toList();
    }

    return [];
  }

  // Preia abonamentul activ pentru userul autentificat
  Future<ActiveSubscription?> getActiveSubscription(String token) async {
    final uri = Uri.parse('$baseUrl/subscriptions/active');
    final response = await http.get(uri, headers: _jsonHeaders(token: token));
    
    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      if (decoded != null && decoded is Map<String, dynamic>) {
        return ActiveSubscription.fromJson(decoded);
      }
    }
    return null;
  }

  // Activeaza un abonament pentru userul autentificat
  Future<http.Response> activateSubscription(String token, int subscriptionId) async {
    final uri = Uri.parse('$baseUrl/subscriptions/activate');
    return http.post(
      uri,
      body: jsonEncode({'subscription_id': subscriptionId}),
      headers: _jsonHeaders(token: token),
    );
  }

  // Preia QR-ul activ ca bytes imagine
  Future<Uint8List> getActiveQr(String token) async {
    final uri = Uri.parse('$baseUrl/active-qr');
    final response = await http.get(uri, headers: _jsonHeaders(token: token));
    if (response.statusCode != 200) {
      throw Exception('Failed to load QR (${response.statusCode})');
    }
    return response.bodyBytes;
  }
}
