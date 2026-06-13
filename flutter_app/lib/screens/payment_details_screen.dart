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
        title: const Text('Detalii parcare'),
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
                      size: 44,
                      color: Colors.red,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      snapshot.error.toString().replaceFirst(
                            'Exception: ',
                            '',
                          ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
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
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(
                    Icons.local_parking,
                    size: 52,
                    color: Colors.blue,
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Ai stat: ${_durationText(fee.parkedMinutes)}',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Total de plată: '
                    '${fee.amount.toStringAsFixed(2)} ${fee.currency}',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const Spacer(),
                  SizedBox(
                    height: 50,
                    child: FilledButton.icon(
                      onPressed: () => _openCardPayment(fee),
                      icon: const Icon(Icons.credit_card),
                      label: const Text('Plătește acum'),
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
