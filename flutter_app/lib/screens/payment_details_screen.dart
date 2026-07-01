import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/parking_fee.dart';
import '../services/api_service.dart';
import 'card_payment_screen.dart';

class PaymentDetailsScreen extends StatefulWidget {
  static const routeName = '/payment-details';

  const PaymentDetailsScreen({super.key});

  @override
  State<PaymentDetailsScreen> createState() => _PaymentDetailsScreenState();
}

class _PaymentDetailsScreenState extends State<PaymentDetailsScreen> {
  final ApiService _apiService = ApiService();
  late Future<ParkingFee> _feeFuture;

  @override
  void initState() {
    super.initState();
    _feeFuture = _loadFee();
  }

  Future<ParkingFee> _loadFee() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');
    if (token == null || token.isEmpty) {
      throw Exception('Autentifică-te din nou');
    }
    return _apiService.getParkingFee(token);
  }

  void _refresh() {
    setState(() {
      _feeFuture = _loadFee();
    });
  }

  String _durationText(int totalMinutes) {
    final hours = totalMinutes ~/ 60;
    final minutes = totalMinutes % 60;
    final parts = <String>[];

    if (hours > 0) {
      parts.add('$hours ${hours == 1 ? 'oră' : 'ore'}');
    }
    if (minutes > 0 || hours == 0) {
      parts.add('$minutes ${minutes == 1 ? 'minut' : 'minute'}');
    }

    return parts.join(' și ');
  }

  void _openCardPayment(ParkingFee fee) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CardPaymentScreen.directParking(
          amount: fee.amount,
          parkingCode: fee.parkingCode,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalii Plată Parcare'),
        actions: [
          IconButton(
            onPressed: _refresh,
            tooltip: 'Reîncarcă',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: FutureBuilder<ParkingFee>(
        future: _feeFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      size: 64,
                      color: Color.fromARGB(255, 223, 223, 15),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      snapshot.error.toString().replaceFirst(
                            'Exception: ',
                            '',
                          ),
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 24),
                    FilledButton.icon(
                      onPressed: _refresh,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Reîncearcă'),
                    ),
                  ],
                ),
              ),
            );
          }

          final fee = snapshot.data!;
          return SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 16),
                  Card(
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                      side: const BorderSide(color: Color(0xFFE2E8F0)),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: const Color(0xFFEFF6FF),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.local_parking_rounded,
                              size: 48,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                          const SizedBox(height: 32),
                          const Text(
                            'Timp de parcare',
                            style: TextStyle(
                              color: Color(0xFF64748B),
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _durationText(fee.parkedMinutes),
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1E293B),
                            ),
                          ),
                          const SizedBox(height: 32),
                          const Divider(color: Color(0xFFE2E8F0)),
                          const SizedBox(height: 32),
                          const Text(
                            'Total de plată',
                            style: TextStyle(
                              color: Color(0xFF64748B),
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${fee.amount.toStringAsFixed(2)} ${fee.currency}',
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontSize: 40,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF10B981),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 48),
                  SizedBox(
                    height: 56,
                    child: FilledButton.icon(
                      onPressed: () => _openCardPayment(fee),
                      icon: const Icon(Icons.credit_card),
                      label: const Text('Plătește acum', style: TextStyle(fontSize: 18)),
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981),
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
