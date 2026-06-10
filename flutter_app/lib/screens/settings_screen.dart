import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  static const routeName = '/settings';
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _numeController = TextEditingController();
  final _prenumeController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _plateController = TextEditingController();
  final ApiService _apiService = ApiService();

  bool _loading = true;
  bool _saving = false;
  String? _token;

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) return 'Email is required';
    final emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+');
    if (!emailRegex.hasMatch(value)) return 'Invalid email';
    return null;
  }

  String? _validateOptionalPassword(String? value) {
    if (value != null && value.isNotEmpty && value.length < 6) {
      return 'Password must be at least 6 characters';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    final password = _passwordController.text.trim();
    if (password.isEmpty) return null;
    if (value == null || value.isEmpty) return 'Confirm password is required';
    if (value != password) return 'Passwords do not match';
    return null;
  }

  String? _validateRequired(String? value, String field) {
    if (value == null || value.isEmpty) return '$field is required';
    return null;
  }

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');
      if (!mounted) return;

      if (token == null || token.isEmpty) {
        setState(() {
          _loading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please login again')),
        );
        return;
      }

      _token = token;
      final response = await _apiService.getProfile(token);
      if (!mounted) return;

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        _numeController.text = body['nume']?.toString() ?? '';
        _prenumeController.text = body['prenume']?.toString() ?? '';
        _emailController.text = body['email']?.toString() ?? '';
        _plateController.text = body['numar_inmatriculare']?.toString() ?? '';
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load profile (${response.statusCode})')),
        );
      }
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Load error: $error')),
      );
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;
    if (_token == null || _token!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Missing authentication token')),
      );
      return;
    }

    setState(() => _saving = true);
    final payload = <String, dynamic>{
      'nume': _numeController.text.trim(),
      'prenume': _prenumeController.text.trim(),
      'email': _emailController.text.trim(),
      'numar_inmatriculare': _plateController.text.trim(),
    };
    if (_passwordController.text.trim().isNotEmpty) {
      payload['password'] = _passwordController.text;
    }

    try {
      final response = await _apiService.updateProfile(_token!, payload);
      if (!mounted) return;

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully')),
        );
        _passwordController.clear();
      } else {
        String message = 'Failed to update profile';
        try {
          final body = jsonDecode(response.body);
          if (body is Map<String, dynamic> && body['detail'] != null) {
            message = body['detail'].toString();
          }
        } catch (_) {}
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Save error: $error')),
      );
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  @override
  void dispose() {
    _numeController.dispose();
    _prenumeController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _plateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: ListView(
                  children: [
                    TextFormField(
                      controller: _numeController,
                      decoration: const InputDecoration(labelText: 'Nume', border: OutlineInputBorder()),
                      validator: (value) => _validateRequired(value, 'Nume'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _prenumeController,
                      decoration: const InputDecoration(labelText: 'Prenume', border: OutlineInputBorder()),
                      validator: (value) => _validateRequired(value, 'Prenume'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                      validator: _validateEmail,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Parolă (opțional)', border: OutlineInputBorder()),
                      validator: _validateOptionalPassword,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _confirmPasswordController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Confirmă parola', border: OutlineInputBorder()),
                      validator: _validateConfirmPassword,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _plateController,
                      decoration: const InputDecoration(labelText: 'Număr înmatriculare', border: OutlineInputBorder()),
                      textCapitalization: TextCapitalization.characters,
                      inputFormatters: [UpperCaseTextFormatter()],
                      validator: (value) => _validateRequired(value, 'Număr înmatriculare'),
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      height: 48,
                      child: _saving
                          ? const Center(child: CircularProgressIndicator())
                          : ElevatedButton(
                              onPressed: _saveProfile,
                              child: const Text('Save changes'),
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
