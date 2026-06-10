import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';

class QRScreen extends StatefulWidget {
  static const routeName = '/qr';
  const QRScreen({super.key});

  @override
  State<QRScreen> createState() => _QRScreenState();
}

class _QRScreenState extends State<QRScreen> {
  final ApiService _apiService = ApiService();
  Uint8List? _qrBytes;
  String? _errorMessage;
  String? _parkingStatus;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadQr();
  }

  Future<void> _loadQr() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');
      if (!mounted) return;

      if (token == null || token.isEmpty) {
        setState(() {
          _errorMessage = 'Please login again';
          _loading = false;
        });
        return;
      }

      final results = await Future.wait([
        _apiService.getActiveQr(token),
        _apiService.getParkingStatus(token),
      ]);
      if (!mounted) return;

      setState(() {
        _qrBytes = results[0] as Uint8List;
        _parkingStatus = results[1] as String;
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _errorMessage = error.toString();
        _loading = false;
      });
    }
  }

  String _statusMessage(String? status) {
    switch (status) {
      case 'paid':
        return 'Folosiți acest cod pentru a ieși din parcare';
      case 'waiting_payment':
      case 'payment_expired':
        return 'Folosiți acest cod pentru a plăti';
      default:
        return 'QR not available';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('QR')),
      body: Center(
        child: _loading
            ? const CircularProgressIndicator()
            : _qrBytes != null
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text('QR activ'),
                      const SizedBox(height: 16),
                      Image.memory(_qrBytes!, width: 240, height: 240, fit: BoxFit.contain),
                      const SizedBox(height: 16),
                      Text(
                        _statusMessage(_parkingStatus),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadQr,
                        child: const Text('Refresh'),
                      ),
                    ],
                  )
                : Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_errorMessage ?? 'QR not available'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadQr,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
      ),
    );
  }
}
