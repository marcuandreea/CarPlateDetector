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
      appBar: AppBar(title: const Text('Register')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(controller: _numeC, decoration: const InputDecoration(labelText: 'Nume'), validator: (v) => _validateRequired(v, 'Nume')),
              const SizedBox(height: 8),
              TextFormField(controller: _prenumeC, decoration: const InputDecoration(labelText: 'Prenume'), validator: (v) => _validateRequired(v, 'Prenume')),
              const SizedBox(height: 8),
              TextFormField(controller: _emailC, decoration: const InputDecoration(labelText: 'Email'), keyboardType: TextInputType.emailAddress, validator: _validateEmail),
              const SizedBox(height: 8),
              TextFormField(controller: _passwordC, decoration: const InputDecoration(labelText: 'Parolă'), obscureText: true, validator: _validatePassword),
              const SizedBox(height: 8),
              TextFormField(
                controller: _confirmPasswordC,
                decoration: const InputDecoration(labelText: 'Confirmă parola'),
                obscureText: true,
                validator: _validateConfirmPassword,
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _plateC,
                decoration: const InputDecoration(labelText: 'Număr înmatriculare'),
                textCapitalization: TextCapitalization.characters,
                inputFormatters: [UpperCaseTextFormatter()],
                validator: (v) => _validateRequired(v, 'Număr înmatriculare'),
              ),
              const SizedBox(height: 16),
              _loading
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(onPressed: _submit, child: const Text('Register')),
              const SizedBox(height: 8),
              TextButton(onPressed: () => Navigator.pop(context), child: const Text('Back to Login')),
            ],
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
