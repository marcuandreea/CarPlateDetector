import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/subscription_plan.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

enum PaymentType { subscription, directParking }

class CardPaymentScreen extends StatefulWidget {
  final PaymentType paymentType;
  final double amount;
  final SubscriptionPlan? subscriptionPlan;
  final String? parkingCode;

  const CardPaymentScreen({
    super.key,
    required this.paymentType,
    required this.amount,
    this.subscriptionPlan,
    this.parkingCode,
  }) : assert(
          (paymentType == PaymentType.subscription &&
                  subscriptionPlan != null) ||
              (paymentType == PaymentType.directParking && parkingCode != null),
        );

  CardPaymentScreen.subscription({
    super.key,
    required SubscriptionPlan plan,
  })  : paymentType = PaymentType.subscription,
        amount = plan.price,
        subscriptionPlan = plan,
        parkingCode = null;

  CardPaymentScreen.directParking({
    super.key,
    required this.amount,
    required String parkingCode,
  })  : paymentType = PaymentType.directParking,
        subscriptionPlan = null,
        parkingCode = parkingCode;

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

  bool get _isSubscription => widget.paymentType == PaymentType.subscription;

  String? _validateCardNumber(String? value) {
    final digits = value?.replaceAll(' ', '') ?? '';
    if (!RegExp(r'^\d{16}$').hasMatch(digits)) {
      return 'Numărul cardului trebuie să conțină 16 cifre';
    }
    return null;
  }

  String? _validateExpiryDate(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Data expirării este obligatorie';
    }

    final match = RegExp(r'^(\d{2})/(\d{2}|\d{4})$').firstMatch(value.trim());
    if (match == null) return 'Folosește formatul LL/AA';

    final month = int.tryParse(match.group(1)!);
    final yearText = match.group(2)!;
    final year =
        yearText.length == 2 ? 2000 + int.parse(yearText) : int.parse(yearText);
    if (month == null || month < 1 || month > 12) {
      return 'Luna nu este validă';
    }

    final now = DateTime.now();
    final expiry = DateTime(year, month + 1, 0);
    final currentMonthEnd = DateTime(now.year, now.month + 1, 0);
    if (expiry.isBefore(currentMonthEnd)) return 'Cardul este expirat';
    return null;
  }

  String? _validateCvv(String? value) {
    if (!RegExp(r'^\d{3}$').hasMatch(value?.trim() ?? '')) {
      return 'CVV trebuie să conțină 3 cifre';
    }
    return null;
  }

  String? _validateCardholderName(String? value) {
    final name = value?.trim() ?? '';
    if (name.isEmpty) return 'Numele titularului este obligatoriu';
    if (!RegExp(r"^[A-Za-zÀ-ÖØ-öø-ÿĂÂÎȘȚăâîșț\s'-]+$").hasMatch(name)) {
      return 'Numele poate conține doar litere';
    }
    return null;
  }

  String _responseError(String body, int statusCode) {
    try {
      final decoded = jsonDecode(body);
      if (decoded is Map<String, dynamic> && decoded['detail'] != null) {
        return decoded['detail'].toString();
      }
    } catch (_) {
      // Raspunsul nu este JSON.
    }
    return 'Plata nu a putut fi procesată ($statusCode)';
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _loading = true);
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');
      if (token == null || token.isEmpty) {
        throw Exception('Autentifică-te din nou');
      }

      final response = _isSubscription
          ? await _apiService.activateSubscription(
              token,
              widget.subscriptionPlan!.id,
            )
          : await _apiService.payParking(
              token,
              widget.parkingCode!,
              widget.amount,
            );

      if (!mounted) return;
      if (response.statusCode != 200) {
        throw Exception(
          _responseError(response.body, response.statusCode),
        );
      }

      await showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Plată confirmată'),
          content: Text(
            _isSubscription
                ? 'Abonamentul a fost activat cu succes.'
                : 'Plata parcării a fost înregistrată cu succes.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Continuă'),
            ),
          ],
        ),
      );

      if (!mounted) return;
      Navigator.pushNamedAndRemoveUntil(
        context,
        HomeScreen.routeName,
        (route) => false,
      );
    } catch (error) {
      if (!mounted) return;
      final message = error.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Eroare la plată: $message')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
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
    final title = _isSubscription ? 'Plată abonament' : 'Plată parcare';
    final confirmLabel =
        _isSubscription ? 'Activează abonamentul' : 'Confirmă plata parcării';

    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                _isSubscription
                    ? widget.subscriptionPlan!.nume
                    : 'Parcare fără abonament',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                '${widget.amount.toStringAsFixed(2)} RON',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              if (_isSubscription) ...[
                const SizedBox(height: 4),
                Text('${widget.subscriptionPlan!.duration} zile'),
              ],
              const SizedBox(height: 24),
              TextFormField(
                controller: _cardNumberController,
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(16),
                  CardNumberTextFormatter(),
                ],
                decoration: const InputDecoration(
                  labelText: 'Număr card',
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
                  labelText: 'Data expirării (LL/AA)',
                  border: OutlineInputBorder(),
                ),
                validator: _validateExpiryDate,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _cvvController,
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(3),
                ],
                obscureText: false,
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
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(
                  labelText: 'Nume titular card',
                  border: OutlineInputBorder(),
                ),
                validator: _validateCardholderName,
              ),
              const SizedBox(height: 20),
              SizedBox(
                height: 48,
                child: FilledButton(
                  onPressed: _loading ? null : _submit,
                  child: _loading
                      ? const SizedBox.square(
                          dimension: 22,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Text(confirmLabel),
                ),
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
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final digits = newValue.text.replaceAll(' ', '');
    final buffer = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i > 0 && i % 4 == 0) buffer.write(' ');
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
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final digits = newValue.text.replaceAll('/', '');
    final buffer = StringBuffer();

    for (var i = 0; i < digits.length && i < 4; i++) {
      if (i == 2) buffer.write('/');
      buffer.write(digits[i]);
    }

    final formatted = buffer.toString();
    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}
