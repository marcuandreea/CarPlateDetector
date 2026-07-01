import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';
import 'payment_details_screen.dart';

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
        return 'Folosește acest cod pentru a ieși din parcare';
      case 'waiting_payment':
      case 'payment_expired':
        return 'Folosește acest cod pentru a plăti la terminal';
      default:
        return 'QR Code invalid sau expirat';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cod QR Parcare')),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: _loading
              ? const CircularProgressIndicator()
              : _qrBytes != null
                  ? Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          'Scanează la barieră',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1E293B),
                          ),
                        ),
                        const SizedBox(height: 24),
                        Card(
                          elevation: 4,
                          shadowColor: const Color(0xFF94A3B8).withOpacity(0.3),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(24),
                          ),
                          child: Container(
                            padding: const EdgeInsets.all(32),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(24),
                            ),
                            child: Column(
                              children: [
                                Container(
                                  decoration: BoxDecoration(
                                    border: Border.all(color: const Color(0xFFE2E8F0), width: 2),
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                  padding: const EdgeInsets.all(16),
                                  child: Image.memory(
                                    _qrBytes!,
                                    width: 200,
                                    height: 200,
                                    fit: BoxFit.contain,
                                  ),
                                ),
                                const SizedBox(height: 24),
                                Text(
                                  _statusMessage(_parkingStatus),
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    color: Color(0xFF475569),
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 32),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            ElevatedButton.icon(
                              onPressed: _loadQr,
                              icon: const Icon(Icons.refresh),
                              label: const Text('Reîncarcă'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFF1F5F9),
                                foregroundColor: const Color(0xFF1E293B),
                                elevation: 0,
                              ),
                            ),
                          ],
                        ),
                        if (_parkingStatus == 'waiting_payment' ||
                            _parkingStatus == 'payment_expired') ...[
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            height: 56,
                            child: FilledButton.icon(
                              onPressed: () => Navigator.pushNamed(
                                context,
                                PaymentDetailsScreen.routeName,
                              ),
                              icon: const Icon(Icons.credit_card),
                              label: const Text('Plătește online', style: TextStyle(fontSize: 18)),
                            ),
                          ),
                        ],
                      ],
                    )
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.qr_code_scanner_rounded,
                          size: 64,
                          color: Color(0xFF94A3B8),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _errorMessage ?? 'Codul QR nu este disponibil',
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Color(0xFF64748B), fontSize: 16),
                        ),
                        const SizedBox(height: 24),
                        FilledButton.icon(
                          onPressed: _loadQr,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Reîncearcă'),
                        ),
                      ],
                    ),
        ),
      ),
    );
  }
}
