import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  static const routeName = '/register';
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _numeC = TextEditingController();
  final _prenumeC = TextEditingController();
  final _emailC = TextEditingController();
  final _passwordC = TextEditingController();
  final _confirmPasswordC = TextEditingController();
  final _plateC = TextEditingController();
  final ApiService _api = ApiService();
  bool _loading = false;

  String? _validateEmail(String? v) {
    if (v == null || v.isEmpty) return 'Email is required';
    final re = RegExp(r"^[^@\s]+@[^@\s]+\.[^@\s]+");
    if (!re.hasMatch(v)) return 'Invalid email';
    return null;
  }

  String? _validatePassword(String? v) {
    if (v == null || v.isEmpty) return 'Password is required';
    if (v.length < 6) return 'Password must be at least 6 characters';
    return null;
  }

  String? _validateConfirmPassword(String? v) {
    if (v == null || v.isEmpty) return 'Confirm password is required';
    if (v != _passwordC.text) return 'Passwords do not match';
    return null;
  }

  String? _validateRequired(String? v, String field) {
    if (v == null || v.isEmpty) return '$field is required';
    return null;
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    final payload = {
      'nume': _numeC.text.trim(),
      'prenume': _prenumeC.text.trim(),
      'email': _emailC.text.trim(),
      'password': _passwordC.text,
      'numar_inmatriculare': _plateC.text.trim(),
    };

    try {
      final res = await _api.register(payload);
      if (res.statusCode == 200 || res.statusCode == 201) {
        // Success
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Registered successfully')));
        Navigator.pop(context);
      } else {
        String msg = 'Registration failed';
        try {
          final body = jsonDecode(res.body);
          if (body is Map && body['detail'] != null) msg = body['detail'].toString();
        } catch (_) {}
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _numeC.dispose();
    _prenumeC.dispose();
    _emailC.dispose();
    _passwordC.dispose();
    _confirmPasswordC.dispose();
    _plateC.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Align(
                  alignment: Alignment.centerLeft,
                  child: IconButton(
                    icon: const Icon(Icons.arrow_back, color: Color(0xFF1E293B)),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Creează cont',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Completează datele de mai jos',
                  style: TextStyle(
                    fontSize: 16,
                    color: Color(0xFF64748B),
                  ),
                ),
                const SizedBox(height: 32),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _numeC,
                        decoration: const InputDecoration(labelText: 'Nume'),
                        validator: (v) => _validateRequired(v, 'Nume'),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        controller: _prenumeC,
                        decoration: const InputDecoration(labelText: 'Prenume'),
                        validator: (v) => _validateRequired(v, 'Prenume'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _emailC,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                  validator: _validateEmail,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _passwordC,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Parolă',
                    prefixIcon: Icon(Icons.lock_outline),
                  ),
                  validator: _validatePassword,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _confirmPasswordC,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Confirmă parola',
                    prefixIcon: Icon(Icons.lock_reset_outlined),
                  ),
                  validator: _validateConfirmPassword,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _plateC,
                  decoration: const InputDecoration(
                    labelText: 'Număr înmatriculare',
                    prefixIcon: Icon(Icons.directions_car_outlined),
                  ),
                  textCapitalization: TextCapitalization.characters,
                  inputFormatters: [UpperCaseTextFormatter()],
                  validator: (v) => _validateRequired(v, 'Număr înmatriculare'),
                ),
                const SizedBox(height: 48),
                SizedBox(
                  height: 56,
                  child: _loading
                      ? const Center(child: CircularProgressIndicator())
                      : FilledButton(
                          onPressed: _submit,
                          child: const Text('Înregistrare', style: TextStyle(fontSize: 18)),
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
    return TextEditingValue(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
      composing: TextRange.empty,
    );
  }
}
