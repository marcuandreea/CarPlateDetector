import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/subscription_plan.dart';
import '../services/api_service.dart';

class CardPaymentScreen extends StatefulWidget {
  static const routeName = '/card-payment';
  const CardPaymentScreen({super.key});

  @override
  State<CardPaymentScreen> createState() => _CardPaymentScreenState();
}

class _CardPaymentScreenState extends State<CardPaymentScreen> {
  final _formKey = GlobalKey<FormState>();
  final _cardNumberController = TextEditingController();
  final _expiryDateController = TextEditingController();
  final _cvvController = TextEditingController();
  final _nameController = TextEditingController();
  final ApiService _apiService = ApiService();

  bool _loading = false;

  SubscriptionPlan? _selectedPlan;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _selectedPlan ??= ModalRoute.of(context)?.settings.arguments as SubscriptionPlan?;
  }

  String? _validateCardNumber(String? value) {
    final digits = value?.replaceAll(' ', '') ?? '';
    if (digits.length != 16) return 'Card number must contain 16 digits';
    if (!RegExp(r'^\d{16}$').hasMatch(digits)) return 'Card number must contain only digits';
    return null;
  }

  String? _validateExpiryDate(String? value) {
    if (value == null || value.trim().isEmpty) return 'Expiry date is required';
    final match = RegExp(r'^(\d{2})/(\d{2}|\d{4})$').firstMatch(value.trim());
    if (match == null) return 'Use MM/YY or MM/YYYY';

    final month = int.tryParse(match.group(1)!);
    final yearText = match.group(2)!;
    final year = yearText.length == 2 ? 2000 + int.parse(yearText) : int.parse(yearText);
    if (month == null || month < 1 || month > 12) return 'Invalid month';

    final now = DateTime.now();
    final expiry = DateTime(year, month + 1, 0);
    final currentMonthEnd = DateTime(now.year, now.month + 1, 0);
    if (expiry.isBefore(currentMonthEnd)) return 'Card has expired';
    return null;
  }

  String? _validateCvv(String? value) {
    if (value == null || value.trim().isEmpty) return 'CVV is required';
    if (!RegExp(r'^\d{3}$').hasMatch(value.trim())) return 'CVV must contain 3 digits';
    return null;
  }

  String? _validateCardholderName(String? value) {
    if (value == null || value.trim().isEmpty) return 'Cardholder name is required';
    if (!RegExp(r'^[A-Za-zÀ-ÿ\s]+$').hasMatch(value.trim())) return 'Name must contain only letters';
    return null;
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedPlan == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No subscription plan selected')),
      );
      return;
    }

    setState(() => _loading = true);
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');
      if (token == null || token.isEmpty) {
        throw Exception('Please login again');
      }

      final response = await _apiService.activateSubscription(token, _selectedPlan!.id);
      if (!mounted) return;

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Subscription activated successfully')),
        );
        Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to activate subscription (${response.statusCode})')),
        );
      }
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Payment error: $error')),
      );
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  void dispose() {
    _cardNumberController.dispose();
    _expiryDateController.dispose();
    _cvvController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Card Payment')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              Text(
                'Plan selectat: ${_selectedPlan?.nume ?? '-'}',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Text(
                'Pret: ${_selectedPlan?.price.toStringAsFixed(2) ?? '0.00'} RON',
              ),
              Text(
                'Durata: ${_selectedPlan?.duration ?? 0} zile',
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _cardNumberController,
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(19),
                  CardNumberTextFormatter(),
                ],
                decoration: const InputDecoration(
                  labelText: 'Card number',
                  border: OutlineInputBorder(),
                ),
                validator: _validateCardNumber,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _expiryDateController,
                keyboardType: TextInputType.datetime,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(5),
                  ExpiryDateTextFormatter(),
                ],
                decoration: const InputDecoration(
                  labelText: 'Expiry date (MM/YY)',
                  border: OutlineInputBorder(),
                ),
                validator: _validateExpiryDate,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _cvvController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'CVV',
                  border: OutlineInputBorder(),
                ),
                validator: _validateCvv,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _nameController,
                keyboardType: TextInputType.name,
                decoration: const InputDecoration(
                  labelText: 'Nume detinator card',
                  border: OutlineInputBorder(),
                ),
                validator: _validateCardholderName,
              ),
              const SizedBox(height: 20),
              SizedBox(
                height: 48,
                child: _loading
                    ? const Center(child: CircularProgressIndicator())
                    : ElevatedButton(
                        onPressed: _submit,
                        child: const Text('Creează și activează abonamentul'),
                      ),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Back'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class CardNumberTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
    final digits = newValue.text.replaceAll(' ', '');
    final buffer = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i > 0 && i % 4 == 0) {
        buffer.write(' ');
      }
      buffer.write(digits[i]);
    }

    final formatted = buffer.toString();
    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}

class ExpiryDateTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
    final digits = newValue.text.replaceAll('/', '');
    final buffer = StringBuffer();

    for (var i = 0; i < digits.length && i < 4; i++) {
      if (i == 2) {
        buffer.write('/');
      }
      buffer.write(digits[i]);
    }

    final formatted = buffer.toString();
    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}
